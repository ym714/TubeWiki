---
marp: true
theme: default
paginate: true
header: 'TubeWiki - 完成までのアクションプラン'
footer: '© 2025 TubeWiki | 2025-12-03'
---

# TubeWiki 完成までのアクションプラン

**優先度別・実行可能なタスクリスト**

---

## 📊 現状サマリー

### ✅ 実装完了
- Core API (FastAPI) - ノート作成・取得
- Worker Service - YouTube文字起こし・AI生成・Notion連携
- Chrome拡張機能 - Popup・Content Script・認証
- Stripe決済 - Checkout・Webhook（基本実装）
- Supabase認証・DB接続

### ⚠️ 未完成・要改善
- Stripe本番環境設定
- E2Eテスト
- 本番デプロイ
- ランディングページ

---

## 🎯 優先度1: 最優先（今すぐ実行）

### 1.1 Stripe決済の本番対応

> [!IMPORTANT]
> 現在はダミーURLがハードコードされており、本番利用不可

**タスク**:
- [ ] 環境変数に `SUCCESS_URL` と `CANCEL_URL` を追加
- [ ] `core/api/payment.py` を修正してURLを動的に取得
- [ ] サブスクリプションキャンセル処理を実装
  - Webhook: `customer.subscription.deleted` イベント
  - `User.is_pro = False` に更新

**ファイル**: [`core/api/payment.py`](file:///Users/motoki/projects/TubeWiki/core/api/payment.py)

---

### 1.2 Chrome拡張機能の手動テスト

**目的**: 実際のブラウザ環境で動作確認

**手順**:
1. `cd extension && npm run build`
2. Chrome: `chrome://extensions/` を開く
3. 「デベロッパーモード」をON
4. 「パッケージ化されていない拡張機能を読み込む」→ `extension/dist` を選択
5. YouTubeを開いて以下を確認:
   - [ ] ログインできるか
   - [ ] 「Generate Study Guide」ボタンが表示されるか
   - [ ] ノート生成が完了するか
   - [ ] エラー時に適切なメッセージが表示されるか

---

### 1.3 エラーハンドリングの強化

**現状の問題**:
- QStashのジョブ失敗時、リトライ設定が不明確
- ユーザーに「失敗」が適切に伝わらない可能性

**タスク**:
- [ ] QStash DLQ (Dead Letter Queue) の設定確認
- [ ] `worker/main.py` でエラー時に `Note.status = FAILED` を確実に設定
- [ ] `extension/src/popup/Popup.tsx` で `FAILED` ステータスの表示改善
  - 「再試行」ボタンの追加

---

## 🚀 優先度2: 本番デプロイ準備

### 2.1 本番環境へのデプロイ

**推奨プラットフォーム**: Railway

**タスク**:
- [ ] **Core Service** をRailwayにデプロイ
  - 環境変数: `DATABASE_URL`, `QSTASH_TOKEN`, `WORKER_URL`, `SUPABASE_JWT_SECRET`, `STRIPE_*`
- [ ] **Worker Service** をRailwayにデプロイ
  - 環境変数: `DATABASE_URL`, `GROQ_API_KEY`, `NOTION_TOKEN`
- [ ] Supabase本番プロジェクトの作成
  - 本番用 `DATABASE_URL` を取得
  - 本番用 `SUPABASE_JWT_SECRET` を取得

---

### 2.2 環境変数の整理

**現状**: `.env` ファイルが複数存在し、管理が煩雑

**タスク**:
- [ ] `.env.example` を各サービスに作成
  - `core/.env.example`
  - `worker/.env.example`
  - `extension/.env.example`
- [ ] README.md に環境変数の設定手順を追記

---

### 2.3 Stripe本番キーへの切り替え

**タスク**:
- [ ] Stripe Dashboard で本番モードに切り替え
- [ ] `STRIPE_SECRET_KEY` を `sk_live_*` に更新
- [ ] `STRIPE_PRICE_ID` を本番用に更新
- [ ] Webhook URLを本番URLに設定
  - 例: `https://your-core-api.railway.app/payment/webhook`

---

## 🎨 優先度3: UX改善

### 3.1 Chrome拡張機能のアイコン作成

**現状**: デフォルトのReactアイコン

**タスク**:
- [ ] TubeWiki用のアイコンを作成（16px, 48px, 128px）
- [ ] `extension/public/icons/` に配置
- [ ] `extension/manifest.json` の `icons` フィールドを更新

---

### 3.2 ローディング体験の改善

**タスク**:
- [ ] ノート生成中のプログレス表示を追加
  - 例: 「文字起こし中...」→「AI生成中...」→「Notion保存中...」
- [ ] サイドバーの開閉アニメーション追加（CSS transition）

---

### 3.3 Markdown表示の改善

**タスク**:
- [ ] `Popup.tsx` で `prose` クラスのスタイル確認
- [ ] 必要に応じて `tailwindcss/typography` プラグインを追加

---

## 📝 優先度4: ドキュメント・マーケティング

### 4.1 ランディングページ (LP) 作成

**目的**: ユーザー獲得

**推奨スタック**: Next.js + Vercel

**必須セクション**:
- [ ] ヒーローセクション（キャッチコピー）
- [ ] デモ動画（YouTube埋め込み）
- [ ] 機能紹介（3つのステップ）
- [ ] 価格表 (Pricing)
- [ ] Chrome Web Storeへのリンク

---

### 4.2 Chrome Web Store申請準備

**タスク**:
- [ ] `manifest.json` の最終確認
  - `name`, `description`, `version` の確認
- [ ] スクリーンショット作成（1280x800px、最低3枚）
- [ ] プロモーション画像作成（440x280px）
- [ ] プライバシーポリシーの作成
  - 例: `https://your-landing-page.com/privacy`

---

### 4.3 README.md の充実

**タスク**:
- [ ] プロジェクト概要を追加
- [ ] インストール手順を追加
- [ ] 開発環境のセットアップ手順を追加
- [ ] スクリーンショットを追加

---

## 🧪 優先度5: テスト・品質保証

### 5.1 E2Eテストの実装

**目的**: 全体フローの動作保証

**テストシナリオ**:
1. [ ] ユーザー登録・ログイン
2. [ ] YouTube動画でノート生成リクエスト
3. [ ] Core → QStash → Worker → Groq → Notion の完走確認
4. [ ] Notionページ作成確認
5. [ ] Stripe決済フロー（テストモード）

**ツール**: Playwright または Puppeteer

---

### 5.2 ユニットテストの追加

**現状**: `tests/` ディレクトリに一部テストあり

**タスク**:
- [ ] `core/api/payment.py` のテスト追加
- [ ] `worker/services/ai.py` のテスト追加
- [ ] `shared/models/` のテスト追加

---

## 📅 推奨実行順序

### Week 1: 最小限の動作確認
1. ✅ **1.2 Chrome拡張機能の手動テスト**
2. ✅ **1.3 エラーハンドリングの強化**
3. ✅ **1.1 Stripe決済の本番対応**

### Week 2: 本番環境構築
4. ✅ **2.1 本番環境へのデプロイ**
5. ✅ **2.3 Stripe本番キーへの切り替え**
6. ✅ **1.2 本番環境での手動テスト**（再実行）

### Week 3: 公開準備
7. ✅ **3.1 アイコン作成**
8. ✅ **4.2 Chrome Web Store申請準備**
9. ✅ **4.1 ランディングページ作成**

---

## 🎯 最優先アクション（今日やるべきこと）

### 1. Chrome拡張機能の動作確認
```bash
cd extension
npm run build
# Chrome で extension/dist を読み込み
# YouTube で実際に試す
```

### 2. Stripe URLの修正
- `core/api/payment.py` の `success_url` / `cancel_url` を環境変数化

### 3. エラー表示の改善
- `Popup.tsx` で `FAILED` ステータス時に「再試行」ボタンを追加

---

## 📌 まとめ

### 完成までの距離
- **コア機能**: ✅ 90%完成
- **本番対応**: ⚠️ 50%完成
- **UX/UI**: ⚠️ 70%完成
- **マーケティング**: ❌ 0%

### 次のマイルストーン
**「自分自身が使える状態 (Dogfooding)」** を目指し、まずは **優先度1** のタスクを完了させましょう。

決済機能は後回しでも問題ありません。最初は **完全無料ベータ版** として公開する戦略も有効です。
