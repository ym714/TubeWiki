---
marp: true
theme: default
paginate: true
header: "TubeWiki Development Roadmap"
footer: "2025-12-06"
---

# TubeWiki: ゴールまでの最短ルート
## 現状分析と残タスク

---

# 🎯 ゴール定義

**YouTube動画からAIノートを生成し、Notionに保存する**

1. 拡張機能が動画URLを送信
2. Workerが動画を処理 (文字起こし -> AI要約)
3. データベースに保存
4. 拡張機能がノートを取得して表示/Notionへペースト

---

# 🚦 現状のステータス

- **Worker**: ⚠️ 起動エラー (DB接続設定の不備) -> **修正済み (Env設定待ち)**
- **Core API**: ❓ デプロイ状況の確認が必要
- **Extension**: ⚠️ ローカル設定 (localhost) のまま -> **本番URL設定が必要**
- **Database**: ✅ Supabase (Transaction Pooler) 設定済み

---

# 🛣️ 最短ルート: ステップ 1

## Workerの復旧 (最優先)

Workerが起動しないと何も始まりません。

1. **Railwayの環境変数を設定**
   - `DATABASE_URL`: SupabaseのTransaction Pooler (ポート6543) のURLを設定
   - `QSTASH_...`: QStashのキーが設定されているか確認
2. **再デプロイ**
   - 設定変更後、Railwayで再デプロイを実行

---

# 🛣️ 最短ルート: ステップ 2

## Core APIの確認

拡張機能はWorkerではなくCore APIと通信します。

1. **Core APIのURLを確認**
   - Railway上のCoreサービスのURL (例: `https://core-production.up.railway.app`) を取得
2. **ヘルスチェック**
   - ブラウザで `https://<CORE_URL>/healthz` にアクセスし `{"status":"ok"}` を確認

---

# 🛣️ 最短ルート: ステップ 3

## 拡張機能の本番ビルド

拡張機能を本番サーバーに向ける必要があります。

1. **`.env.production` の作成 (またはビルド時指定)**
   - `extension/` ディレクトリで実行:
   ```bash
   VITE_API_URL=https://<CORE_URL> npm run build
   ```
2. **Chromeへの読み込み**
   - `extension/dist` ディレクトリをChromeに「パッケージ化されていない拡張機能」として読み込む

---

# 🏁 最終確認 (E2Eテスト)

1. YouTube動画を開く
2. サイドパネルを開く
3. 「Generate Note」をクリック
4. **成功**: ノートが生成され、表示される
5. **Notion連携**: "Copy to Notion" が機能することを確認

---

# 📝 次のアクション

1. **[今すぐ]** RailwayでWorkerの `DATABASE_URL` を設定する
2. **[その後]** Core APIのURLを教えてください (拡張機能のビルドに使います)
