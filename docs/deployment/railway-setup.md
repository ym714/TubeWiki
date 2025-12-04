# Railway デプロイガイド

## 📋 前提条件

- Railway アカウント（https://railway.app/）
- GitHub アカウント
- Supabase プロジェクト（PostgreSQL）
- Groq API キー
- Upstash QStash アカウント

---

## 🚀 デプロイ手順

### 1. Railway プロジェクト作成

1. Railway にログイン
2. 「New Project」をクリック
3. 「Deploy from GitHub repo」を選択
4. `ym714/TubeWiki` リポジトリを選択

### 2. サービスの分割

TubeWikiは2つのサービスが必要です：

#### Service 1: Core API

**設定**:
- **Name**: `tubewiki-core`
- **Root Directory**: `/`
- **Start Command**: `uvicorn core.main:app --host 0.0.0.0 --port $PORT`

**環境変数**:
```bash
DATABASE_URL=postgresql://postgres:[password]@[host]:6543/postgres?pgbouncer=true
QSTASH_TOKEN=your_qstash_token
WORKER_URL=https://tubewiki-worker.up.railway.app
PORT=8000
PYTHONPATH=/app
```

#### Service 2: Worker

**設定**:
- **Name**: `tubewiki-worker`
- **Root Directory**: `/`
- **Start Command**: `uvicorn worker.main:app --host 0.0.0.0 --port $PORT`

**環境変数**:
```bash
DATABASE_URL=postgresql://postgres:[password]@[host]:6543/postgres?pgbouncer=true
GROQ_API_KEY=your_groq_api_key
QSTASH_CURRENT_SIGNING_KEY=your_current_key
QSTASH_NEXT_SIGNING_KEY=your_next_key
PORT=8001
PYTHONPATH=/app
```

---

## 🔐 環境変数の取得方法

### Supabase Database URL

1. Supabase Dashboard → Settings → Database
2. **Connection string** → **Transaction pooler**
3. `postgresql://postgres:[password]@[host]:6543/postgres?pgbouncer=true` をコピー

### Groq API Key

1. https://console.groq.com/ にアクセス
2. API Keys → Create API Key
3. キーをコピー

### QStash Credentials

1. https://console.upstash.com/ にアクセス
2. QStash → Create QStash
3. **Current Signing Key** と **Next Signing Key** をコピー
4. **QStash Token** もコピー

---

## 📝 デプロイ後の設定

### 1. Core API URL の確認

Railway が自動生成したURLを確認：
```
https://tubewiki-core.up.railway.app
```

### 2. Worker URL の確認

```
https://tubewiki-worker.up.railway.app
```

### 3. Core API の環境変数を更新

`WORKER_URL` を実際のWorker URLに更新：
```bash
WORKER_URL=https://tubewiki-worker.up.railway.app
```

### 4. 拡張機能の設定を更新

`extension/.env`:
```bash
VITE_API_URL=https://tubewiki-core.up.railway.app/api/v1
```

拡張機能をリビルド：
```bash
cd extension
npm run build
```

---

## ✅ 動作確認

### 1. Health Check

**Core API**:
```bash
curl https://tubewiki-core.up.railway.app/healthz
```

**Worker**:
```bash
curl https://tubewiki-worker.up.railway.app/healthz
```

### 2. API ドキュメント

**Core API**:
```
https://tubewiki-core.up.railway.app/docs
```

**Worker**:
```
https://tubewiki-worker.up.railway.app/docs
```

### 3. ノート作成テスト

```bash
curl -X POST https://tubewiki-core.up.railway.app/api/v1/notes \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'
```

---

## 🔧 トラブルシューティング

### デプロイが失敗する

**原因**: 依存関係のインストールエラー

**解決策**:
1. `requirements.txt` を確認
2. Railway のビルドログを確認
3. Python バージョンを確認（3.10以上）

### データベース接続エラー

**原因**: DATABASE_URL が正しくない

**解決策**:
1. Supabase の Connection Pooler URL を使用
2. `?pgbouncer=true` パラメータを追加
3. パスワードに特殊文字がある場合はURLエンコード

### Worker が応答しない

**原因**: GROQ_API_KEY が設定されていない

**解決策**:
1. 環境変数を確認
2. Groq API の使用制限を確認
3. Worker のログを確認

---

## 💰 コスト見積もり

### Railway 無料枠
- $5/月のクレジット
- 500時間/月の実行時間
- 512MB RAM

### 推定コスト（有料プラン）
- Core API: ~$5/月
- Worker: ~$5/月
- **合計**: ~$10/月

### その他のサービス
- Supabase: 無料枠あり
- Groq: 無料枠あり（制限あり）
- Upstash QStash: 無料枠あり

---

## 📊 モニタリング

### Railway Dashboard

- CPU使用率
- メモリ使用率
- リクエスト数
- エラーログ

### 推奨設定

**アラート**:
- CPU > 80%
- メモリ > 80%
- エラー率 > 5%

---

## 🔄 継続的デプロイ

Railway は GitHub と自動連携されています：

1. `main` ブランチにプッシュ
2. 自動的にビルド開始
3. テスト成功後、自動デプロイ

**注意**: 本番環境では、`production` ブランチを作成することを推奨

---

## 🎯 次のステップ

1. ✅ Railway デプロイ完了
2. ⬜ Chrome 拡張機能の更新
3. ⬜ Chrome Web Store 公開
4. ⬜ ユーザードキュメント作成
5. ⬜ モニタリング設定

---

## 📞 サポート

問題が発生した場合：
1. Railway のログを確認
2. GitHub Issues を作成
3. Discord コミュニティに質問
