# Railway デプロイ手順（実行用）

## 🎯 デプロイ開始

### ステップ1: Railway プロジェクト作成

1. **Railway にアクセス**: https://railway.app/
2. **GitHub でログイン**
3. **「New Project」をクリック**
4. **「Deploy from GitHub repo」を選択**
5. **`ym714/TubeWiki`** を検索して選択
6. **「Deploy Now」をクリック**

---

### ステップ2: Core API サービスの設定

#### 2-1. サービス名を変更
1. デフォルトで作成されたサービスをクリック
2. **Settings** → **Service Name** → `tubewiki-core` に変更

#### 2-2. Start Command を設定
1. **Settings** → **Deploy**
2. **Custom Start Command** を有効化
3. 以下を入力:
```bash
uvicorn core.main:app --host 0.0.0.0 --port $PORT
```

#### 2-3. 環境変数を設定
1. **Variables** タブをクリック
2. 以下の環境変数を追加:

```bash
DATABASE_URL=<Supabase の Transaction Pooler URL>
QSTASH_TOKEN=<worker/.env の QSTASH_TOKEN>
WORKER_URL=https://tubewiki-worker.up.railway.app
PORT=8000
PYTHONPATH=/app
```

**注意**: `WORKER_URL` は後で更新します（まずWorkerをデプロイ）

---

### ステップ3: Worker サービスの追加

#### 3-1. 新しいサービスを追加
1. プロジェクトダッシュボードに戻る
2. **「+ New」** → **「GitHub Repo」**
3. 同じリポジトリ `ym714/TubeWiki` を選択

#### 3-2. サービス名を変更
1. **Settings** → **Service Name** → `tubewiki-worker` に変更

#### 3-3. Start Command を設定
1. **Settings** → **Deploy**
2. **Custom Start Command** を有効化
3. 以下を入力:
```bash
uvicorn worker.main:app --host 0.0.0.0 --port $PORT
```

#### 3-4. 環境変数を設定
1. **Variables** タブをクリック
2. 以下の環境変数を追加:

```bash
DATABASE_URL=<Supabase の Transaction Pooler URL>
GROQ_API_KEY=<worker/.env の GROQ_API_KEY>
QSTASH_CURRENT_SIGNING_KEY=<worker/.env の QSTASH_CURRENT_SIGNING_KEY>
QSTASH_NEXT_SIGNING_KEY=<worker/.env の QSTASH_NEXT_SIGNING_KEY>
PORT=8001
PYTHONPATH=/app
```

---

### ステップ4: Core API の WORKER_URL を更新

#### 4-1. Worker の URL を取得
1. **tubewiki-worker** サービスをクリック
2. **Settings** → **Networking**
3. **Public Networking** の URL をコピー
   - 例: `https://tubewiki-worker.up.railway.app`

#### 4-2. Core API の環境変数を更新
1. **tubewiki-core** サービスに戻る
2. **Variables** タブ
3. `WORKER_URL` の値を更新:
```bash
WORKER_URL=https://tubewiki-worker.up.railway.app
```
4. サービスが自動的に再デプロイされます

---

### ステップ5: デプロイ確認

#### 5-1. デプロイログを確認
1. 各サービスの **Deployments** タブをクリック
2. 最新のデプロイをクリック
3. **View Logs** でビルドログを確認
4. ✅ "Application startup complete" が表示されればOK

#### 5-2. Health Check
**Core API**:
```bash
curl https://tubewiki-core.up.railway.app/healthz
```

**Worker**:
```bash
curl https://tubewiki-worker.up.railway.app/healthz
```

#### 5-3. API ドキュメントにアクセス
**Core API**:
```
https://tubewiki-core.up.railway.app/docs
```

---

### ステップ6: 拡張機能の更新

#### 6-1. Core API URL を取得
1. **tubewiki-core** サービスをクリック
2. **Settings** → **Networking**
3. **Public Networking** の URL をコピー
   - 例: `https://tubewiki-core.up.railway.app`

#### 6-2. 拡張機能の環境変数を更新
`extension/.env`:
```bash
VITE_API_URL=https://tubewiki-core.up.railway.app/api/v1
```

#### 6-3. 拡張機能をリビルド
```bash
cd extension
npm run build
```

#### 6-4. 拡張機能をリロード
Chrome の拡張機能管理画面で「再読み込み」

---

## ✅ 完了チェックリスト

- [ ] Railway プロジェクト作成
- [ ] Core API サービス設定
- [ ] Worker サービス設定
- [ ] WORKER_URL 更新
- [ ] デプロイログ確認
- [ ] Health Check 成功
- [ ] API ドキュメントアクセス可能
- [ ] 拡張機能の環境変数更新
- [ ] 拡張機能リビルド
- [ ] 動作テスト

---

## 🎉 デプロイ完了！

これで TubeWiki が本番環境で動作しています！

次のステップ:
1. Chrome Web Store への公開準備
2. ユーザードキュメントの作成
3. モニタリング設定
