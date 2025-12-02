# Notion Integration Specification

## 1. Objective
Enable users to automatically export generated YouTube video notes (summaries, transcripts, etc.) to their own Notion workspace.

## 2. Architecture & Data Flow

We will adopt a **Stateless / Job-Based** approach for the MVP.
Instead of storing user's Notion credentials in our database, the client (Chrome Extension) will pass them as part of the job payload. The Worker service will use these credentials ephemerally to create the Notion page.

### Flow Diagram
1.  **User** configures Notion Integration Token and Parent Page ID in Chrome Extension Settings.
2.  **User** clicks "Generate Note".
3.  **Extension** sends `POST /notes` to Core Service.
    *   Payload includes `options: { notion_token: "...", notion_page_id: "..." }`.
4.  **Core Service** validates request and publishes job to **QStash**.
5.  **Worker Service** receives Webhook from QStash.
6.  **Worker Service** generates content (GPT-4o).
7.  **Worker Service** checks for Notion credentials in job options.
8.  **Worker Service** converts Markdown content to Notion Blocks.
9.  **Worker Service** calls Notion API to create a page under the specified Parent Page.
10. **Worker Service** updates Note status in Supabase.

## 3. Component Responsibilities

### 3.1. Chrome Extension (Client)
*   **Settings UI**: Input fields for `Notion Integration Token` and `Parent Page ID`.
*   **Storage**: Save these credentials locally (using `chrome.storage.local`).
*   **Job Submission**: Include these credentials in the `options` field of the API request.

### 3.2. Core Service (API)
*   **Validation**: Ensure `options` field is allowed in `JobRequest`. (Already supported as `Dict[str, Any]`).
*   **Passthrough**: Pass the `options` to the Worker via QStash payload.

### 3.3. Worker Service (Processor)
*   **Logic**: `services/notion.py` needs to be updated.
    *   Accept `token` and `page_id` as arguments (instead of relying solely on env vars).
    *   **Markdown Conversion**: Implement a robust Markdown-to-Notion-Blocks converter.
        *   Headings (#, ##, ###) -> `heading_1`, `heading_2`, `heading_3`
        *   Lists (-, 1.) -> `bulleted_list_item`, `numbered_list_item`
        *   Code Blocks (```) -> `code`
        *   Bold/Italic -> `rich_text` annotations
        *   Embeds -> `embed` block for YouTube video.
*   **Error Handling**:
    *   If Notion API fails (e.g., invalid token), log the error but **do not fail the entire job**.
    *   The Note status should probably still be `COMPLETED` (since generation succeeded), but maybe append a warning to `error_message` or a separate `integration_status` field (future improvement). For now, log error and proceed.

## 4. Data Models

### JobRequest (Shared Schema)
No changes needed to schema definition, but usage will be:

```json
{
  "video_url": "https://youtube.com/watch?v=...",
  "user_id": "...",
  "options": {
    "notion_token": "secret_...",
    "notion_page_id": "..."
  }
}
```

## 5. Implementation Details

### 5.1. Markdown to Blocks Conversion
Since Notion API does not accept raw Markdown, we must parse it.
We can use a library like `mistune` to parse Markdown into an AST, and then map AST nodes to Notion Block objects.

**Mapping Table:**

| Markdown | Notion Block Type |
| :--- | :--- |
| `# Text` | `heading_1` |
| `## Text` | `heading_2` |
| `### Text` | `heading_3` |
| `- Item` | `bulleted_list_item` |
| `1. Item` | `numbered_list_item` |
| `> Text` | `quote` |
| ` ```code``` ` | `code` |
| `[Text](url)` | `text` with `link` attribute |
| `**Bold**` | `text` with `bold` annotation |

### 5.2. Notion Service Update (`worker/services/notion.py`)

Refactor `NotionService` to be instantiated per-request or accept credentials in methods.

```python
class NotionService:
    def __init__(self, token: str):
        self.client = AsyncClient(auth=token)

    async def create_page(self, parent_page_id: str, title: str, markdown_content: str, video_url: str):
        # ... implementation ...
```

## 6. Security Considerations
*   **Token Storage**: Tokens are stored in the user's browser (Chrome Storage), which is relatively safe for personal extensions.
*   **Transmission**: Sent over HTTPS to Core -> QStash -> Worker.
*   **Persistence**: We do NOT persist the Notion Token in our Supabase database. It exists only in the ephemeral job payload.

## 7. Future Improvements
*   **OAuth Flow**: Implement proper OAuth2 flow so users don't need to copy-paste tokens.
*   **Two-Way Sync**: Allow updates in Notion to reflect in the app (out of scope for MVP).
