---
marp: true
theme: default
paginate: true
header: FlashNote AI - 残タスク報告書
footer: 2025-12-03 | Project Status Report
---

# FlashNote AI 残タスク報告書

**現在の進捗と今後のステップ**

---

## 1. プロジェクト進捗概要

**現在のステータス: フェーズ3 (Frontend) 完了間近**

- **Backend (Core & Worker)**: ほぼ完了 ✅
    - モノレポ構成、DB、QStash連携、YouTube取得、AI生成(Groq)、Notion連携まで実装済み。
- **Frontend (Chrome Extension)**: 基本機能完了 ✅
    - React環境、Supabase認証、API連携、メインロジック実装済み。
- **残タスク**: インフラ調整、決済機能、UI/UXの磨き込み、QA。

---

## 2. 完了したタスク (Achievements)

### Backend (Core & Worker)
- [x] モノレポ構成の確立 (`core`, `worker`, `shared`)
- [x] データベース設計 & Supabase Auth連携
- [x] **Core API**: ノート作成エンドポイント (`POST /notes`) & QStash配信
- [x] **Worker**: Webhook処理、署名検証、冪等性担保
- [x] **AI処理**: YouTube字幕取得 -> **Groq (Llama 3.3)** による要約・図解生成
- [x] **Notion連携**: 生成結果のNotionページへの自動エクスポート

### Frontend (Chrome Extension)
- [x] Vite + React + CRXJS による拡張機能開発環境
- [x] Supabase Auth (Email/Password) ログイン
- [x] 現在のタブのURLを取得し、バックエンドへ送信するロジック

---

## 3. 残タスク (Remaining Tasks)

### 3.1 インフラ & 設定 (Week 2)
- [ ] **Supabase Transaction Pooler 設定**
    - ポート6543を使用した接続プールの構成（高負荷対策）。
    - 現在は直接接続またはデフォルト設定で動作中。

### 3.2 フロントエンド機能拡張 (Week 3)
- [ ] **Stripe 決済機能の実装**
    - サブスクリプション課金の導入。
    - ユーザーごとの利用制限ロジック。
- [ ] **UI/UXの磨き込み**
    - **ポーリング処理**: ノート生成完了を検知し、ユーザーに通知/表示する機能。
    - ローディング表示、エラーハンドリングの改善。

---

## 3.3 品質保証 & リリース準備 (Week 4)

- [ ] **堅牢性 (Robustness) の検証**
    - **QStash リトライ & Dead Letter Queue (DLQ)**: 失敗時の再試行ロジックの確認。
    - エラー時のNotionへの通知など。
- [ ] **ユーザビリティテスト**
    - 実際のユーザーフローを通したテスト（インストール -> ログイン -> 生成 -> Notion確認）。
- [ ] **ランディングページ (LP) 作成**
    - サービス紹介、インストール誘導、価格表を含むWebサイト。

---

## 4. 推奨される次のステップ

**優先度: 高 (High)**

1.  **UIポーリングの実装**:
    - ユーザーが「生成ボタン」を押した後、完了するまで待機・確認できるUIを作る必要があります。これがUXに直結します。
2.  **E2Eテスト (Frontend -> Backend -> Notion)**:
    - 拡張機能から実際にリクエストを送り、Notionにページができるまでの一連の流れを検証します。

**優先度: 中 (Medium)**

3.  **Stripe決済**:
    - マネタイズを急ぐ場合は優先度を上げますが、まずは無料版としての完成度を高めることを推奨します。

---

## 5. まとめ

バックエンドのコア機能（特にAI生成とNotion連携）は非常に強力な状態で完成しています。
Groqへの移行により、コストと速度の課題も解決しました。

残るは **「ユーザーインターフェース（拡張機能）とバックエンドを滑らかに繋ぐこと」** です。
特に、非同期処理（生成待ち）のUXをどう見せるかが鍵となります。
