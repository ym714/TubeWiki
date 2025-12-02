---
marp: true
theme: default
paginate: true
header: "TubeWiki プロジェクト構造"
footer: "2025-12-02"
---

# TubeWiki プロジェクト構造

## 概要とディレクトリ構成

---

## プロジェクト概要: モノレポ構成

TubeWikiプロジェクトは、PythonバックエンドとChrome拡張機能フロントエンドを単一のリポジトリで管理する**モノレポ（Monorepo）**構成を採用しています。

- **Backend**: Python (FastAPI)
- **Frontend**: TypeScript / JavaScript (Chrome Extension)
- **Shared**: バックエンドサービス間で共有される共通ロジック

---

## 1. バックエンド構成 (Python)

バックエンドは共通コードを共有する2つの主要サービスに分割されています。

- **`core/`**: メインAPIサーバー (FastAPI)。ユーザーリクエストと認証を処理します。
- **`worker/`**: バックグラウンドワーカーサービス。YouTube文字起こし取得、AI要約、Notion連携などの重い処理を担当します。
- **`shared/`**: `core` と `worker` の両方で使用される共通ライブラリ。
  - `models/`: データベースモデル
  - `schemas/`: API用Pydanticスキーマ
  - `utils/`: 共通ユーティリティ関数
  - `db.py`: データベース接続ロジック

---

## 2. フロントエンド構成 (Chrome拡張機能)

フロントエンドは、ユーザーおよびバックエンドAPIと対話するブラウザ拡張機能です。

- **`extension/`**: Chrome拡張機能のソースコード一式。
  - UIコンポーネント（サイドパネル、ポップアップ）を含みます。
- **`package.json` / `package-lock.json`**: Node.jsプロジェクト設定。
  - 拡張機能のビルド用依存関係（Tailwind CSSなど）を管理します。
- **`node_modules/`**: インストールされたNode.js依存パッケージ。

---

## 3. テストと品質保証

コードの品質と信頼性を保証するためのツールとファイルです。

- **`tests/`**: プロジェクト全体の単体テストと結合テストが含まれています。
- **`pytest.ini`**: テストランナー `pytest` の設定ファイルです。
- **`.coverage`**: テスト実行によるコードカバレッジ結果を保存するデータファイルです。
- **`test.db`**: ローカル開発およびテスト用のSQLiteデータベースファイルです。

---

## 4. ドキュメントと仕様書

プロジェクトの定義と構築方法を定義するファイル群です。

- **`product_spec.md`**: プロダクト仕様書（ゴール、ユーザーストーリー）。
- **`technical_spec.md`**: 技術仕様書（アーキテクチャ、API設計）。
- **`implementation_plan.md`**: 開発のステップバイステップ計画。
- **`docs/`**: プロジェクトドキュメント（このファイルなど）を含むディレクトリ。

---

## 5. 設定と依存関係

- **`requirements.txt`**: Python依存ライブラリ（FastAPI, SQLModel, OpenAIなど）。
- **`.gitignore`**: Gitによるバージョン管理から除外するファイル指定（シークレット、ビルド生成物など）。
