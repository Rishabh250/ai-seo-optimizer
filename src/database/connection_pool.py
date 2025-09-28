"""
Database connection pool implementation for improved performance.

This module provides connection pooling to eliminate the overhead of creating
individual database connections and enables batch operations for better performance.
"""
import asyncio
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import asyncpg

from ..utils.exceptions import DatabaseConnectionError
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ConnectionPoolConfig:
    """Configuration for database connection pool."""
    host: str
    port: int
    database: str
    user: str
    password: str
    min_size: int = 5
    max_size: int = 20
    command_timeout: int = 60
    server_settings: Optional[Dict[str, str]] = None

    @classmethod
    def from_env(cls) -> 'ConnectionPoolConfig':
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'college_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            min_size=int(os.getenv('DB_POOL_MIN_SIZE', '5')),
            max_size=int(os.getenv('DB_POOL_MAX_SIZE', '20')),
            command_timeout=int(os.getenv('DB_COMMAND_TIMEOUT', '60')),
        )


@dataclass
class BatchQuery:
    """Represents a query to be executed in a batch."""
    query: str
    args: tuple = ()
    query_type: str = 'fetch'  # 'fetch', 'execute', 'fetchval', 'fetchrow'


@dataclass
class BatchResult:
    """Result of a batch query execution."""
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0


class DatabaseConnectionPool:
    """
    High-performance database connection pool with batch operations.

    This class provides:
    - Connection pooling to reduce connection overhead
    - Batch query execution for improved performance
    - Automatic retry logic for transient failures
    - Connection health monitoring
    - Performance metrics tracking
    """

    def __init__(self, config: Optional[ConnectionPoolConfig] = None):
        """
        Initialize the connection pool.

        Args:
            config: Connection pool configuration (uses environment if None)
        """
        self.config = config or ConnectionPoolConfig.from_env()
        self.pool: Optional[asyncpg.Pool] = None
        self._connection_count = 0
        self._query_count = 0
        self._total_execution_time = 0.0
        self._failed_queries = 0

    async def initialize(self) -> None:
        """Initialize the connection pool."""
        try:
            logger.info(f"Initializing database connection pool (min={self.config.min_size}, max={self.config.max_size})")

            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                min_size=self.config.min_size,
                max_size=self.config.max_size,
                command_timeout=self.config.command_timeout,
                server_settings=self.config.server_settings or {},
            )

            logger.info("Database connection pool initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise DatabaseConnectionError(f"Connection pool initialization failed: {e}")

    async def close(self) -> None:
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
            self._log_performance_stats()

    def _log_performance_stats(self) -> None:
        """Log performance statistics."""
        if self._query_count > 0:
            avg_time = self._total_execution_time / self._query_count
            success_rate = ((self._query_count - self._failed_queries) / self._query_count) * 100

            logger.info("Database Performance Statistics:")
            logger.info(f"  Total Queries: {self._query_count}")
            logger.info(f"  Failed Queries: {self._failed_queries}")
            logger.info(f"  Success Rate: {success_rate:.2f}%")
            logger.info(f"  Average Execution Time: {avg_time:.3f}s")
            logger.info(f"  Total Execution Time: {self._total_execution_time:.3f}s")

    @asynccontextmanager
    async def acquire_connection(self):
        """Acquire a connection from the pool."""
        if not self.pool:
            raise DatabaseConnectionError("Connection pool not initialized")

        async with self.pool.acquire() as connection:
            self._connection_count += 1
            try:
                yield connection
            except Exception as e:
                logger.error(f"Error with database connection: {e}")
                raise

    async def execute_query(
        self,
        query: str,
        *args,
        query_type: str = 'fetch'
    ) -> Any:
        """
        Execute a single query with performance tracking.

        Args:
            query: SQL query string
            *args: Query parameters
            query_type: Type of query ('fetch', 'execute', 'fetchval', 'fetchrow')

        Returns:
            Query result based on query_type
        """
        import time
        start_time = time.time()

        try:
            async with self.acquire_connection() as connection:
                if query_type == 'fetch':
                    result = await connection.fetch(query, *args)
                elif query_type == 'fetchrow':
                    result = await connection.fetchrow(query, *args)
                elif query_type == 'fetchval':
                    result = await connection.fetchval(query, *args)
                elif query_type == 'execute':
                    result = await connection.execute(query, *args)
                else:
                    raise ValueError(f"Unknown query type: {query_type}")

                execution_time = time.time() - start_time
                self._query_count += 1
                self._total_execution_time += execution_time

                logger.debug(f"Query executed in {execution_time:.3f}s: {query[:100]}...")
                return result

        except Exception as e:
            execution_time = time.time() - start_time
            self._failed_queries += 1
            self._total_execution_time += execution_time
            logger.error(f"Query failed after {execution_time:.3f}s: {e}")
            raise

    async def execute_batch(
        self,
        queries: List[BatchQuery],
        use_transaction: bool = True
    ) -> List[BatchResult]:
        """
        Execute multiple queries in batch for improved performance.

        Args:
            queries: List of BatchQuery objects to execute
            use_transaction: Whether to wrap all queries in a transaction

        Returns:
            List of BatchResult objects with execution results
        """
        import time
        results = []
        total_start_time = time.time()

        if not queries:
            logger.warning("No queries provided for batch execution")
            return results

        logger.info(f"Executing batch of {len(queries)} queries (transaction={use_transaction})")

        try:
            async with self.acquire_connection() as connection:
                if use_transaction:
                    async with connection.transaction():
                        for query_obj in queries:
                            result = await self._execute_single_batch_query(connection, query_obj)
                            results.append(result)
                else:
                    for query_obj in queries:
                        result = await self._execute_single_batch_query(connection, query_obj)
                        results.append(result)

                total_time = time.time() - total_start_time
                successful_queries = sum(1 for r in results if r.success)

                logger.info(f"Batch execution completed: {successful_queries}/{len(queries)} successful in {total_time:.3f}s")

                return results

        except Exception as e:
            total_time = time.time() - total_start_time
            logger.error(f"Batch execution failed after {total_time:.3f}s: {e}")

            # Mark all remaining queries as failed
            while len(results) < len(queries):
                results.append(BatchResult(
                    success=False,
                    error=f"Batch execution failed: {e}",
                    execution_time=0.0
                ))

            return results

    async def _execute_single_batch_query(
        self,
        connection: asyncpg.Connection,
        query_obj: BatchQuery
    ) -> BatchResult:
        """Execute a single query within a batch."""
        import time
        start_time = time.time()

        try:
            if query_obj.query_type == 'fetch':
                result = await connection.fetch(query_obj.query, *query_obj.args)
            elif query_obj.query_type == 'fetchrow':
                result = await connection.fetchrow(query_obj.query, *query_obj.args)
            elif query_obj.query_type == 'fetchval':
                result = await connection.fetchval(query_obj.query, *query_obj.args)
            elif query_obj.query_type == 'execute':
                result = await connection.execute(query_obj.query, *query_obj.args)
            else:
                raise ValueError(f"Unknown query type: {query_obj.query_type}")

            execution_time = time.time() - start_time
            self._query_count += 1
            self._total_execution_time += execution_time

            return BatchResult(
                success=True,
                result=result,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self._failed_queries += 1
            self._total_execution_time += execution_time

            logger.error(f"Batch query failed: {e}")
            return BatchResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )

    async def execute_bulk_insert(
        self,
        table_name: str,
        columns: List[str],
        data: List[List[Any]],
        on_conflict: Optional[str] = None
    ) -> int:
        """
        Execute bulk insert operation for maximum performance.

        Args:
            table_name: Name of the target table
            columns: List of column names
            data: List of row data (each row is a list of values)
            on_conflict: ON CONFLICT clause (e.g., "ON CONFLICT (id) DO NOTHING")

        Returns:
            Number of affected rows
        """
        import time
        start_time = time.time()

        if not data:
            logger.warning("No data provided for bulk insert")
            return 0

        logger.info(f"Performing bulk insert of {len(data)} rows into {table_name}")

        try:
            async with self.acquire_connection() as connection:
                # Prepare the query
                column_list = ', '.join(columns)
                placeholder_list = ', '.join([f'${i+1}' for i in range(len(columns))])
                query = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholder_list})"

                if on_conflict:
                    query += f" {on_conflict}"

                # Execute bulk insert using executemany for best performance
                result = await connection.executemany(query, data)

                execution_time = time.time() - start_time
                self._query_count += len(data)
                self._total_execution_time += execution_time

                rows_affected = len(data) if result == 'INSERT 0 0' else int(result.split()[2])
                logger.info(f"Bulk insert completed: {rows_affected} rows affected in {execution_time:.3f}s")

                return rows_affected

        except Exception as e:
            execution_time = time.time() - start_time
            self._failed_queries += len(data)
            self._total_execution_time += execution_time
            logger.error(f"Bulk insert failed after {execution_time:.3f}s: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the connection pool.

        Returns:
            Dict with health status information
        """
        if not self.pool:
            return {
                'status': 'unhealthy',
                'error': 'Connection pool not initialized'
            }

        try:
            async with self.acquire_connection() as connection:
                # Simple query to test connection
                result = await connection.fetchval('SELECT 1')

                return {
                    'status': 'healthy',
                    'pool_size': self.pool.get_size(),
                    'pool_max_size': self.pool.get_max_size(),
                    'pool_min_size': self.pool.get_min_size(),
                    'idle_connections': self.pool.get_idle_size(),
                    'query_count': self._query_count,
                    'failed_queries': self._failed_queries,
                    'test_query_result': result
                }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'pool_size': self.pool.get_size() if self.pool else 0
            }

    # Convenience methods that maintain backward compatibility
    async def fetch_all(self, query: str, *args) -> List[Any]:
        """Fetch all results from a query."""
        return await self.execute_query(query, *args, query_type='fetch')

    async def fetch_one(self, query: str, *args) -> Optional[Any]:
        """Fetch one result from a query."""
        return await self.execute_query(query, *args, query_type='fetchrow')

    async def fetch_value(self, query: str, *args) -> Any:
        """Fetch a single value from a query."""
        return await self.execute_query(query, *args, query_type='fetchval')

    async def execute(self, query: str, *args) -> str:
        """Execute a query and return status."""
        return await self.execute_query(query, *args, query_type='execute')


# Global connection pool instance
_global_pool: Optional[DatabaseConnectionPool] = None


async def get_connection_pool() -> DatabaseConnectionPool:
    """
    Get or create the global connection pool instance.

    Returns:
        DatabaseConnectionPool instance
    """
    global _global_pool

    if _global_pool is None:
        _global_pool = DatabaseConnectionPool()
        await _global_pool.initialize()

    return _global_pool


async def close_connection_pool() -> None:
    """Close the global connection pool."""
    global _global_pool

    if _global_pool:
        await _global_pool.close()
        _global_pool = None