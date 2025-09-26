"""
Service for converting markdown to HTML and JSON.
"""
import json
from typing import Any, Dict, List

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_plain.renderer import RendererPlain

from ..models.markdown import ConversionResult, MarkdownElement
from ..utils.exceptions import ContentGenerationError
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class MarkdownConverterService:
    """Service for converting markdown to HTML and JSON formats."""

    def __init__(self):
        """Initialize the markdown converter."""
        try:
            self.md = MarkdownIt("commonmark", {"html": True})
            
            self.md.enable([
                "table",
                "strikethrough", 
                "linkify"
            ])
            
            logger.info("MarkdownConverterService initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MarkdownConverterService: {e}")
            raise ContentGenerationError(f"Markdown converter initialization failed: {e}")

    def convert(self, markdown_text: str) -> ConversionResult:
        """
        Convert markdown text to HTML and JSON structure.
        
        Args:
            markdown_text: The markdown text to convert
            
        Returns:
            ConversionResult containing HTML and JSON representations
        """
        try:
            logger.info("Starting markdown conversion")
            
            html = self.md.render(markdown_text)
            
            tokens = self.md.parse(markdown_text)
            
            json_structure = self._tokens_to_json(tokens)
            
            metadata = self._generate_metadata(markdown_text, tokens)
            
            result = ConversionResult(
                original_markdown=markdown_text,
                html=html,
                json_structure=json_structure,
                metadata=metadata
            )
            
            logger.info("Successfully converted markdown to HTML and JSON")
            return result
            
        except Exception as e:
            logger.error(f"Error converting markdown: {e}")
            raise ContentGenerationError(f"Markdown conversion failed: {e}")

    def _tokens_to_json(self, tokens: List[Token]) -> List[Dict[str, Any]]:
        """Convert markdown tokens to JSON structure."""
        result = []
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            element = self._token_to_element(token)
            
            if token.nesting == 1:
                children_tokens = []
                nesting_level = 1
                j = i + 1
                
                while j < len(tokens) and nesting_level > 0:
                    next_token = tokens[j]
                    if next_token.type == token.type.replace("_open", "_close"):
                        nesting_level -= 1
                        if nesting_level == 0:
                            break
                    elif next_token.type == token.type:
                        nesting_level += 1
                    
                    if nesting_level > 0:
                        children_tokens.append(next_token)
                    j += 1
                
                if children_tokens:
                    element.children = []
                    child_elements = self._tokens_to_json(children_tokens)
                    for child_dict in child_elements:
                        child_element = MarkdownElement(**child_dict)
                        element.children.append(child_element)
                
                i = j + 1
                
            else:
                i += 1
            
            result.append(element.to_dict())
        
        return result

    def _token_to_element(self, token: Token) -> MarkdownElement:
        """Convert a single token to MarkdownElement."""
        element = MarkdownElement(type=token.type)
        
        if token.content:
            element.content = token.content
            
        if token.tag:
            element.tag = token.tag
            
        if token.attrs:
            element.attrs = dict(token.attrs)

        if token.type.startswith("heading") and token.tag:
            element.level = int(token.tag[1])
            
        return element

    def _generate_metadata(self, markdown_text: str, tokens: List[Token]) -> Dict[str, Any]:
        """Generate metadata about the markdown content."""
        metadata = {
            "character_count": len(markdown_text),
            "line_count": len(markdown_text.split('\n')),
            "word_count": len(markdown_text.split()),
            "token_count": len(tokens)
        }
        
        element_counts = {}
        for token in tokens:
            element_type = token.type
            if element_type not in element_counts:
                element_counts[element_type] = 0
            element_counts[element_type] += 1
        
        metadata["element_counts"] = element_counts
        
        headings = []
        for token in tokens:
            if token.type.startswith("heading") and token.content:
                level = int(token.tag[1]) if token.tag else 1
                headings.append({
                    "level": level,
                    "text": token.content
                })
        
        metadata["headings"] = headings
        metadata["has_tables"] = any(token.type.startswith("table") for token in tokens)
        metadata["has_links"] = any(token.type == "link_open" for token in tokens)
        metadata["has_images"] = any(token.type == "image" for token in tokens)
        
        return metadata

    def save_result_to_files(self, result: ConversionResult, base_filename: str) -> Dict[str, str]:
        """
        Save conversion result to separate files.
        
        Args:
            result: ConversionResult to save
            base_filename: Base filename without extension
            
        Returns:
            Dictionary with file paths created
        """
        try:
            files_created = {}
            
            html_file = f"{base_filename}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(result.html)
            files_created["html"] = html_file
            
            json_file = f"{base_filename}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            files_created["json"] = json_file
            
            md_file = f"{base_filename}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(result.original_markdown)
            files_created["markdown"] = md_file
            
            logger.info(f"Saved conversion result to files: {list(files_created.keys())}")
            return files_created
            
        except Exception as e:
            logger.error(f"Error saving result to files: {e}")
            raise ContentGenerationError(f"Failed to save files: {e}")

    def md_to_text(self, markdown_text: str) -> str:
        """Convert markdown text to plain text."""
        parser = MarkdownIt(renderer_cls=RendererPlain)
        plain_text = parser.render(markdown_text)
        return plain_text

    def md_to_html(self, markdown_text: str) -> str:
        """Convert markdown text to HTML."""
        try:
            return self.md.render(markdown_text)
        except Exception as e:
            logger.error(f"Error converting markdown to HTML: {e}")
            raise ContentGenerationError(f"HTML conversion failed: {e}")
