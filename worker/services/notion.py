import logging
from typing import List, Dict, Any, Optional
from notion_client import AsyncClient
import mistune

logger = logging.getLogger(__name__)

class NotionRenderer(mistune.HTMLRenderer):
    """
    Custom Mistune Renderer to convert Markdown AST to Notion Blocks.
    Note: Mistune is primarily for HTML, but we can abuse the AST walking or use the AST directly.
    Actually, it's easier to just use the AST.
    """
    def __init__(self):
        super().__init__()
        self.blocks = []

    def text(self, text):
        return text

    # We will not use the Renderer class directly for block generation because Mistune's Renderer
    # expects string returns for HTML concatenation.
    # Instead, we will traverse the AST produced by mistune.create_markdown(renderer=None, plugins=[...])

def markdown_to_notion_blocks(markdown_text: str) -> List[Dict[str, Any]]:
    """
    Parses Markdown text and converts it to a list of Notion Block objects.
    """
    if not markdown_text:
        return []

    # Parse Markdown to AST
    markdown = mistune.create_markdown(renderer=None)
    ast = markdown(markdown_text)
    
    blocks = []
    
    for node in ast:
        block = convert_node_to_block(node)
        if block:
            blocks.append(block)
            
    return blocks

def convert_node_to_block(node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Converts a single AST node to a Notion Block.
    """
    node_type = node.get('type')
    attrs = node.get('attrs', {})
    children = node.get('children', [])
    
    # Helper to extract text content from children
    def get_text_content(n):
        if 'raw' in n:
            return n['raw']
        if 'children' in n:
            return "".join([get_text_content(c) for c in n['children']])
        return ""

    # Helper to create rich text object
    def create_rich_text(text_content):
        # Truncate to 2000 chars to avoid Notion API errors
        return [{"type": "text", "text": {"content": text_content[:2000]}}]

    if node_type == 'heading':
        level = attrs.get('level', 1)
        text_content = get_text_content(node)
        block_type = f"heading_{min(level, 3)}" # Notion only supports 1, 2, 3
        return {
            "object": "block",
            "type": block_type,
            block_type: {
                "rich_text": create_rich_text(text_content)
            }
        }
    
    elif node_type == 'paragraph' or node_type == 'block_text':
        text_content = get_text_content(node)
        if not text_content.strip():
            return None
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": create_rich_text(text_content)
            }
        }
        
    elif node_type == 'block_code':
        code_content = node.get('raw', '')
        language = attrs.get('info', 'plain text')
        return {
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": create_rich_text(code_content),
                "language": language if language else "plain text"
            }
        }
        
    # Fallback for other types
    return None

# Improved AST traversal to handle lists flattening
def markdown_to_notion_blocks_improved(markdown_text: str) -> List[Dict[str, Any]]:
    markdown = mistune.create_markdown(renderer=None)
    ast = markdown(markdown_text)
    
    blocks = []
    
    for node in ast:
        node_type = node.get('type')
        
        if node_type == 'list':
            # Handle list items
            is_ordered = node.get('attrs', {}).get('ordered', False)
            block_type = "numbered_list_item" if is_ordered else "bulleted_list_item"
            
            for child in node.get('children', []):
                if child.get('type') == 'list_item':
                    text_content = ""
                    # List items might have paragraph/block_text children or direct text
                    # We need to extract text from all children of the list item
                    def extract_text_recursive(n):
                        if 'raw' in n:
                            return n['raw']
                        if 'children' in n:
                            return "".join([extract_text_recursive(c) for c in n['children']])
                        return ""
                    
                    text_content = extract_text_recursive(child)
                            
                    blocks.append({
                        "object": "block",
                        "type": block_type,
                        block_type: {
                            "rich_text": [{"type": "text", "text": {"content": text_content[:2000]}}]
                        }
                    })
        else:
            block = convert_node_to_block(node)
            if block:
                blocks.append(block)
                
    return blocks


class NotionService:
    def __init__(self, token: str):
        """
        Initialize with a user-provided Notion Token.
        """
        self.client = AsyncClient(auth=token)

    async def create_page(self, parent_page_id: str, title: str, markdown_content: str, video_url: str = None) -> str:
        """
        Creates a new page in Notion.
        """
        try:
            # Convert Markdown to Blocks
            blocks = markdown_to_notion_blocks_improved(markdown_content)
            
            # Add Video Embed at the top if provided
            if video_url:
                blocks.insert(0, {
                    "object": "block",
                    "type": "embed",
                    "embed": {
                        "url": video_url
                    }
                })

            # Create Page
            new_page = await self.client.pages.create(
                parent={"page_id": parent_page_id},
                properties={
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                children=blocks
            )
            return new_page["url"]
            
        except Exception as e:
            logger.error(f"Failed to create Notion page: {e}")
            raise
