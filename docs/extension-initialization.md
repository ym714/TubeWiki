---
marp: true
theme: default
paginate: true
header: "TubeWiki 拡張機能の初期化"
footer: "2025-12-02"
---

# TubeWiki 拡張機能の初期化

## 概要

TubeWiki 用の Chrome 拡張機能プロジェクトの初期化とアーキテクチャの再構築が完了しました。
本ドキュメントでは、技術スタック、プロジェクト構成、および設定の詳細について概説します。

---

## 技術スタック

- **フレームワーク**: React 19 + TypeScript
- **ビルドツール**: Vite 7
- **拡張機能フレームワーク**: CRXJS Vite Plugin (HMR およびマニフェスト生成用)
- **スタイリング**: Tailwind CSS v3 + PostCSS (Shadow DOM 内でスコープ化)
- **マニフェストバージョン**: MV3

---

## プロジェクト構成

拡張機能は `projects/TubeWiki/extension` に配置されています。

```
extension/
├── src/
│   ├── background/    # Service Worker (バックグラウンドスクリプト)
│   ├── content/       # Content Scripts (YouTube 上で動作)
│   │   ├── index.tsx  # エントリーポイント (Shadow DOM 作成)
│   │   ├── Overlay.tsx # オーバーレイ UI コンポーネント
│   │   └── style.css  # Shadow DOM 用スタイル
│   ├── popup/         # 拡張機能ポップアップ UI
│   │   ├── index.html # ポップアップ HTML
│   │   ├── main.tsx   # ポップアップエントリーポイント
│   │   └── Popup.tsx  # ポップアップコンポーネント
│   └── components/    # 共通コンポーネント
├── public/
│   └── manifest.json  # Manifest V3 設定
├── vite.config.ts     # Vite + CRXJS 設定
└── tailwind.config.js # Tailwind 設定
```

---

## アーキテクチャの改善点

### Shadow DOM の採用
- **目的**: YouTube の CSS と拡張機能の CSS の競合（汚染）を防ぐ。
- **実装**: `src/content/index.tsx` で Shadow Root を作成し、その中に React アプリケーションとスタイルを注入します。

### ディレクトリ構成の分離
- **目的**: ポップアップ（ブラウザアクション）とコンテンツスクリプト（ページ内埋め込み）の責務を明確に分離。
- **実装**: `src/popup` と `src/content` にディレクトリを分割。

---

## 現在のステータス

- [x] Vite + React + TS でプロジェクトを初期化
- [x] Tailwind CSS v3 の設定と動作確認
- [x] YouTube 注入用の Manifest V3 設定
- [x] Shadow DOM を用いたコンテンツスクリプトの実装
- [x] ディレクトリ構成の再構築
- [x] ビルドパイプラインの検証 (`npm run build`)
- [x] 基本的なポップアップ UI の実装

---

## 次のステップ

1. **ポップアップ UI の実装**: ログイン画面とステータス表示。
2. **Content Script の実装**: YouTube プレイヤーへのオーバーレイ注入。
3. **Core API との連携**: Wiki データの取得と保存。
