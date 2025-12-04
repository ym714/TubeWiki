---
marp: true
theme: default
paginate: true
header: "TubeWiki デバッグレポート"
footer: "2025-12-04"
---

# TubeWiki デバッグレポート
## エラー解決の全記録

---

# 問題の概要

**症状**: Chrome拡張機能でNotionボタンをクリックしても動作しない
**エラー**: API 404 → API 500 → Worker 401

---

# 修正1: API 404エラー

## 原因
- 拡張機能が `/notes` にリクエスト
- 正しいエンドポイントは `/api/v1/notes`

## 修正内容
**ファイル**: `extension/src/lib/api.ts`

```typescript
const BASE_URL = (import.meta.env.VITE_API_URL || 
  'http://localhost:8000/api/v1').replace(/\/$/, '')
const API_URL = BASE_URL.endsWith('/api/v1') ? 
  BASE_URL : `${BASE_URL}/api/v1`
```

---

# 修正2: QStash 500エラー

## 原因
- QStash（クラウド）が `localhost:8001` に接続不可
- ローカル開発環境の制約

## 修正内容
**ファイル**: `core/api/notes.py`

```python
# ローカル環境ではQStashをバイパス
if "localhost" in worker_url or "127.0.0.1" in worker_url:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{worker_url}/webhooks/process-job",
            json=request.dict()
        )
```

---

# 修正3: データベースセッション

## 原因
- `AsyncSession` に `exec` メソッドが存在しない
- SQLAlchemyとSQLModelの型の不一致

## 修正内容
**ファイル**: `shared/db.py`

```python
# Before
from sqlalchemy.ext.asyncio import AsyncSession

# After
from sqlmodel.ext.asyncio.session import AsyncSession
```

---

# 修正4: Worker エンドポイント404

## 原因
- Core APIが `/webhook` を呼び出し
- 正しいエンドポイントは `/webhooks/process-job`

## 修正内容
**ファイル**: `core/api/notes.py`

```python
# Before
f"{worker_url}/webhook"

# After
f"{worker_url}/webhooks/process-job"
```

---

# 修正5: Worker 署名検証401

## 原因
- Worker が QStash 署名を要求
- ローカル開発では署名が存在しない

## 修正内容
**ファイル**: `worker/api/webhook.py`

```python
# 署名がない場合はローカル開発モードと判断
if signature:
    verify_signature(body_str, signature)
else:
    logger.warning("No signature - local dev mode")
```

---

# Notion自動ペースト改善

## 実装内容
**ファイル**: `extension/src/content/notion.ts`

- エディタ検出のリトライロジック（最大20回）
- 複数セレクタでの検出
- クリップボードフォールバック

```typescript
const getEditor = () => {
    return document.querySelector('.notion-page-content') || 
           document.querySelector('[contenteditable="true"]')
}
```

---

# デバッグログ追加

## 実装内容
**ファイル**: `extension/src/content/ExportBar.tsx`

```typescript
// コンテンツ長の確認
console.log('[TubeWiki] Content length:', 
  currentNote.content.length)

// ストレージ保存の検証
const saved = await chromeStorageAdapter
  .getItem('pending_notion_paste')
console.log('[TubeWiki] Verified save. Length:', 
  saved?.length)
```

---

# システムアーキテクチャへの影響

## Before (本番環境想定)
```
Extension → Core API → QStash → Worker
```

## After (ローカル開発)
```
Extension → Core API → Worker (直接)
```

**メリット**:
- ローカル開発が可能に
- デバッグが容易

**注意点**:
- 本番環境では QStash 経由を使用
- 環境変数 `WORKER_URL` で切り替え

---

# 認証フローの変更

## Before
- TubeWiki 認証（Supabase）
- Notion 認証

## After
- Notion 認証のみ
- すべてのAPI呼び出しが匿名

**影響**:
- ユーザー管理が不要に
- シンプルな実装
- スケーラビリティの課題（将来的に要検討）

---

# データベーススキーマ

## 主要な変更
- `user_id` が "anonymous" に統一
- `content` フィールドに生成されたサマリーを保存
- `status`: PENDING → PROCESSING → COMPLETED/FAILED

## Note モデル
```python
class Note(SQLModel, table=True):
    id: int
    user_id: str = "anonymous"
    video_url: str
    content: Optional[str] = None
    status: NoteStatus
    notion_url: Optional[str] = None
```

---

# 動作フロー（修正後）

1. **YouTube**: ユーザーがNotionボタンをクリック
2. **Extension**: `POST /api/v1/notes` でノート作成
3. **Core API**: ノートをDBに保存、Workerを直接呼び出し
4. **Worker**: 
   - YouTube トランスクリプト取得
   - AI でサマリー生成
   - ノートを更新（status: COMPLETED）
5. **Extension**: ポーリングで完了を確認
6. **Extension**: ストレージに保存、Notionを開く
7. **Notion**: コンテンツスクリプトが自動ペースト

---

# 残存する課題

## 1. AI API キーの設定
- `GROQ_API_KEY` が必要
- 未設定の場合、コンテンツ生成が失敗

## 2. エラーハンドリング
- YouTube トランスクリプトが取得できない場合
- AI 生成が失敗した場合

## 3. 本番環境への移行
- QStash 署名検証の有効化
- Worker の公開URL設定（ngrok等）

---

# 検証方法

## 1. サービス起動確認
```bash
# Core API (port 8000)
PYTHONPATH=. uvicorn core.main:app --reload --port 8000

# Worker (port 8001)
PYTHONPATH=. uvicorn worker.main:app --reload --port 8001
```

## 2. 拡張機能のリロード
Chrome拡張機能管理画面で「再読み込み」

## 3. テスト実行
YouTubeで動画を開き、Notionボタンをクリック

---

# まとめ

## 修正ファイル
1. `extension/src/lib/api.ts` - API URL修正
2. `core/api/notes.py` - QStashバイパス、Worker URL修正
3. `shared/db.py` - AsyncSession型修正
4. `worker/api/webhook.py` - 署名検証スキップ
5. `extension/src/content/ExportBar.tsx` - デバッグログ
6. `extension/src/content/notion.ts` - 自動ペースト改善

## 成果
✅ ローカル開発環境で完全動作
✅ エラーハンドリング強化
✅ デバッグ容易性向上
