import pytest
from worker.services.notion import markdown_to_notion_blocks_improved

def test_markdown_conversion_headings():
    md = """
# Heading 1
## Heading 2
### Heading 3
    """
    blocks = markdown_to_notion_blocks_improved(md)
    assert len(blocks) == 3
    assert blocks[0]['type'] == 'heading_1'
    assert blocks[0]['heading_1']['rich_text'][0]['text']['content'] == 'Heading 1'
    assert blocks[1]['type'] == 'heading_2'
    assert blocks[2]['type'] == 'heading_3'

def test_markdown_conversion_paragraph():
    md = "This is a paragraph."
    blocks = markdown_to_notion_blocks_improved(md)
    assert len(blocks) == 1
    assert blocks[0]['type'] == 'paragraph'
    assert blocks[0]['paragraph']['rich_text'][0]['text']['content'] == 'This is a paragraph.'

def test_markdown_conversion_list():
    md = """
- Item 1
- Item 2
    """
    blocks = markdown_to_notion_blocks_improved(md)
    assert len(blocks) == 2
    assert blocks[0]['type'] == 'bulleted_list_item'
    assert blocks[0]['bulleted_list_item']['rich_text'][0]['text']['content'] == 'Item 1'
    assert blocks[1]['type'] == 'bulleted_list_item'

def test_markdown_conversion_code_block():
    md = """
```python
print("Hello")
```
    """
    blocks = markdown_to_notion_blocks_improved(md)
    assert len(blocks) == 1
    assert blocks[0]['type'] == 'code'
    assert blocks[0]['code']['language'] == 'python'
    assert blocks[0]['code']['rich_text'][0]['text']['content'].strip() == 'print("Hello")'

def test_markdown_conversion_mixed():
    md = """
# Title

Summary text.

- Point 1
- Point 2

```
Code
```
    """
    blocks = markdown_to_notion_blocks_improved(md)
    # Heading, Paragraph, List Item, List Item, Code
    assert len(blocks) == 5
    assert blocks[0]['type'] == 'heading_1'
    assert blocks[1]['type'] == 'paragraph'
    assert blocks[2]['type'] == 'bulleted_list_item'
    assert blocks[3]['type'] == 'bulleted_list_item'
    assert blocks[4]['type'] == 'code'

@pytest.mark.asyncio
async def test_notion_service_create_page(mocker):
    from worker.services.notion import NotionService
    
    # Mock AsyncClient
    mock_client = mocker.Mock()
    mock_pages_create = mocker.AsyncMock(return_value={"url": "https://notion.so/new-page"})
    mock_client.pages.create = mock_pages_create
    
    mocker.patch("worker.services.notion.AsyncClient", return_value=mock_client)
    
    service = NotionService(token="fake_token")
    url = await service.create_page(
        parent_page_id="parent_id",
        title="Test Page",
        markdown_content="# Hello\nWorld",
        video_url="http://video.url"
    )
    
    assert url == "https://notion.so/new-page"
    mock_pages_create.assert_called_once()
    call_kwargs = mock_pages_create.call_args[1]
    assert call_kwargs['parent'] == {'page_id': 'parent_id'}
    assert call_kwargs['properties']['title'][0]['text']['content'] == 'Test Page'
    assert len(call_kwargs['children']) == 3 # Embed + Heading + Paragraph
    assert call_kwargs['children'][0]['type'] == 'embed'
