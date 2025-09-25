"""
Data models for markdown conversion.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class MarkdownElement:
    """Individual markdown element structure."""
    type: str
    content: Optional[str] = None
    tag: Optional[str] = None
    attrs: Optional[Dict[str, Any]] = None
    children: Optional[List["MarkdownElement"]] = None
    level: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"type": self.type}
        
        if self.content is not None:
            result["content"] = self.content
        if self.tag is not None:
            result["tag"] = self.tag
        if self.attrs is not None:
            result["attrs"] = self.attrs
        if self.level is not None:
            result["level"] = self.level
        if self.children is not None:
            result["children"] = [child.to_dict() for child in self.children]
            
        return result


@dataclass
class ConversionResult:
    """Result of markdown conversion."""
    original_markdown: str
    html: str
    json_structure: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "original_markdown": self.original_markdown,
            "html": self.html,
            "json_structure": self.json_structure,
            "metadata": self.metadata
        }
