---
marp: true
theme: default
paginate: true
header: 'TubeWiki - Chrome拡張機能エラー対応ガイド'
footer: '© 2025 TubeWiki'
---

# Chrome拡張機能エラー対応ガイド

**TubeWikiのChrome拡張機能で発生するエラーのトラブルシューティング**

---

## 🔍 現状確認

### 確認済み項目 ✅
- ビルドは正常に完了（`npm run build`）
- `dist/` フォルダに必要なファイルが生成されている
- `manifest.json` の構造は正しい
- Service Worker ファイル（`service-worker-loader.js`）は存在

### 問題
- Service Worker が「Inactive」状態
- 拡張機能に「Errors」ボタンが表示されている

---

## 📋 エラー詳細の確認方法

### ステップ1: エラーメッセージを確認

1. `chrome://extensions/` を開く
2. TubeWiki拡張機能の **「Errors」** ボタンをクリック
3. 表示されたエラーメッセージをコピー

### ステップ2: Service Workerのログを確認

1. `chrome://extensions/` で「service worker (Inactive)」をクリック
2. DevToolsが開く
3. Consoleタブでエラーログを確認

---

## 🐛 よくあるエラーと解決方法

### エラー1: 環境変数が設定されていない

**症状**:
```
Uncaught ReferenceError: process is not defined
```

**原因**: Viteのビルド時に環境変数が正しく処理されていない

**解決方法**:
1. `extension/.env` ファイルを作成
2. 必要な環境変数を設定:
```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_CORE_API_URL=http://localhost:8000
```

---

### エラー2: Supabase初期化エラー

**症状**:
```
Error: supabaseUrl is required
Error: supabaseAnonKey is required
```

**原因**: Supabaseクライアントの初期化に必要な環境変数が不足

**解決方法**:

#### 1. `.env` ファイルを確認
[`extension/.env`](file:///Users/motoki/projects/TubeWiki/extension/.env) が存在するか確認

#### 2. Supabase設定を確認
[`extension/src/lib/supabase.ts`](file:///Users/motoki/projects/TubeWiki/extension/src/lib/supabase.ts) で環境変数が正しく読み込まれているか確認

---

### エラー3: モジュールインポートエラー

**症状**:
```
Failed to load module script
Uncaught SyntaxError: Cannot use import statement outside a module
```

**原因**: Service Workerでのモジュールインポートの問題

**解決方法**:

#### 1. `manifest.json` の確認
```json
"background": {
  "service_worker": "service-worker-loader.js",
  "type": "module"  // ← これが必須
}
```

#### 2. Vite設定の確認
[`extension/vite.config.ts`](file:///Users/motoki/projects/TubeWiki/extension/vite.config.ts) でService Workerのビルド設定を確認

---

### エラー4: CORS エラー

**症状**:
```
Access to fetch at 'http://localhost:8000/...' from origin 'chrome-extension://...' has been blocked by CORS policy
```

**原因**: Core APIがChrome拡張機能からのリクエストを許可していない

**解決方法**:

#### Core APIのCORS設定を修正
[`core/main.py`](file:///Users/motoki/projects/TubeWiki/core/main.py) で以下を確認:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番では制限すべき
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔧 デバッグ手順

### 1. 環境変数の確認

```bash
cd extension
cat .env
```

必要な環境変数:
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_CORE_API_URL`

---

### 2. ビルドのクリーンアップ

```bash
cd extension
rm -rf dist node_modules
npm install
npm run build
```

---

### 3. 拡張機能の再読み込み

1. `chrome://extensions/` を開く
2. TubeWiki拡張機能の **「更新」** ボタン（🔄）をクリック
3. または、拡張機能を削除して再度読み込む

---

### 4. Popup のデバッグ

1. 拡張機能のアイコンをクリック
2. Popupを右クリック → **「検証」**
3. DevToolsでConsoleタブを確認

---

### 5. Content Script のデバッグ

1. YouTubeページを開く
2. F12キーを押してDevToolsを開く
3. Consoleタブで `TubeWiki` 関連のログを確認

---

## 🛠️ 環境変数の設定手順

### ステップ1: `.env.example` を確認

```bash
cd extension
cat .env.example
```

### ステップ2: `.env` ファイルを作成

```bash
cp .env.example .env
```

### ステップ3: 環境変数を設定

```bash
# extension/.env
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
VITE_CORE_API_URL=http://localhost:8000
```

---

## 📝 チェックリスト

### ビルド前
- [ ] `extension/.env` ファイルが存在する
- [ ] 環境変数が正しく設定されている
- [ ] `npm install` が完了している

### ビルド後
- [ ] `extension/dist/` フォルダが存在する
- [ ] `dist/manifest.json` が正しく生成されている
- [ ] `dist/service-worker-loader.js` が存在する

### Chrome読み込み後
- [ ] 拡張機能が「有効」状態
- [ ] Service Workerが「Active」状態
- [ ] エラーが表示されていない

---

## 🚨 緊急対応: エラーメッセージの共有

エラーが解決しない場合、以下の情報を共有してください:

### 1. エラーメッセージ
`chrome://extensions/` の「Errors」ボタンから確認

### 2. Service Workerのログ
「service worker」リンクをクリックして表示されるConsoleログ

### 3. 環境変数の確認
```bash
cd extension
cat .env | grep -v "KEY"  # キーを除外して表示
```

---

## 📌 次のステップ

### エラーが解決したら:
1. ✅ YouTubeページで動作確認
2. ✅ ログイン機能のテスト
3. ✅ ノート生成機能のテスト

### まだエラーが出る場合:
1. 🔍 具体的なエラーメッセージを確認
2. 📸 エラー画面のスクリーンショットを撮影
3. 💬 エラー内容を共有

---

## 🔗 関連ファイル

- [`extension/manifest.json`](file:///Users/motoki/projects/TubeWiki/extension/manifest.json) - 拡張機能の設定
- [`extension/vite.config.ts`](file:///Users/motoki/projects/TubeWiki/extension/vite.config.ts) - ビルド設定
- [`extension/src/lib/supabase.ts`](file:///Users/motoki/projects/TubeWiki/extension/src/lib/supabase.ts) - Supabase初期化
- [`extension/src/background/index.ts`](file:///Users/motoki/projects/TubeWiki/extension/src/background/index.ts) - Service Worker

---

## まとめ

### よくある原因
1. ❌ 環境変数が設定されていない
2. ❌ Supabase URLまたはAnon Keyが間違っている
3. ❌ Core APIが起動していない
4. ❌ CORS設定が正しくない

### 解決の鍵
- 🔑 `.env` ファイルの正しい設定
- 🔑 エラーメッセージの詳細確認
- 🔑 DevToolsでのログ確認
