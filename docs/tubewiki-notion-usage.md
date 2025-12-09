---
marp: true
theme: default
paginate: true
header: "TubeWiki Notion Integration"
footer: "2025-12-09 | TubeWiki Team"
---

# TubeWikiにおけるNotion機能の実装状況

現在のプロジェクトで実装されているNotion連携機能の解説

---

## 概要

TubeWikiでは、以下の2つのアプローチでNotionと連携しています。

1. **Backend (Worker)**: 公式APIを使用したページ作成
2. **Frontend (Extension)**: DOM操作による自動ペースト（Auto-paste）

---

## 1. Backend (Worker) - 公式API利用

Pythonの `worker/services/notion.py` にて実装されています。
公式SDK `notion-client` を使用しています。

### 主要機能: ページの作成 (`create_page`)

指定された親ページの下に、Markdownコンテンツを変換して新規ページを作成します。

- **エンドポイント**: `pages.create`
- **入力**: 親ページID, タイトル, Markdownテキスト, 動画URL
- **処理フロー**:
  1. Markdownを解析し、Notion Block形式に変換
  2. 動画URLがある場合、`embed` ブロックとして先頭に追加
  3. APIをコールしてページを作成

---

### Markdown変換ロジック

`mistune` ライブラリを使用してMarkdownのAST（抽象構文木）を解析し、NotionのBlock Objectに変換しています。

**対応しているMarkdown要素:**
- **見出し**: `heading_1`, `heading_2`, `heading_3`
- **段落**: `paragraph`
- **コードブロック**: `code` (言語指定対応)
- **リスト**: `bulleted_list_item`, `numbered_list_item` (ネスト対応)

**制約:**
- テキストコンテンツは2000文字で切り詰め（API制限回避のため）

---

### コード例 (Worker)

```python
# worker/services/notion.py

async def create_page(self, parent_page_id: str, title: str, markdown_content: str, video_url: str = None) -> str:
    # MarkdownをNotion Blockに変換
    blocks = markdown_to_notion_blocks_improved(markdown_content)
    
    # 動画埋め込みブロックの追加
    if video_url:
        blocks.insert(0, { "type": "embed", ... })

    # ページ作成リクエスト
    new_page = await self.client.pages.create(
        parent={"page_id": parent_page_id},
        properties={ "title": ... },
        children=blocks
    )
    return new_page["url"]
```

---

## 2. Frontend (Extension) - DOM操作

拡張機能の `extension/src/content/notion.ts` にて実装されています。
APIは使用せず、ブラウザ上で開いているNotionページに対して直接操作を行います。

### 機能: 自動ペースト (Auto-paste)

ユーザーが「Notionで開く」などを選択した際、生成されたコンテンツをクリップボード経由または直接DOMに挿入します。

**処理フロー:**
1. `chrome.storage.local` から `pending_notion_paste` データを取得
2. Notionのエディタ要素 (`.notion-page-content` 等) を探索
3. `contentEditable` 要素にテキストを挿入し、`input` イベントを発火
4. 失敗時はクリップボードへのコピーにフォールバック

---

## まとめ

| 機能 | 実装場所 | 技術 | 用途 |
| --- | --- | --- | --- |
| **ページ作成** | Worker | Notion API (`pages.create`) | バックグラウンドでの完全なページ生成 |
| **自動ペースト** | Extension | DOM Manipulation | ユーザーが開いたページへのコンテンツ挿入 |

現在は、用途に応じてこれら2つの方法を使い分けています。
API連携は安定性が高い一方、事前の認証設定が必要です。DOM操作は認証不要ですが、NotionのUI変更に弱いという特徴があります。
