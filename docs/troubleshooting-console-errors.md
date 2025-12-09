---
marp: true
theme: default
paginate: true
header: "TubeWiki Console Error Analysis"
footer: "2025-12-09"
---

# コンソールエラー解析レポート
## 発生しているエラーの原因と対策

---

# 🚨 エラー1: `requestStorageAccessFor`

```
requestStorageAccessFor: Permission denied.
requestStorageAccessFor: Must be handling a user gesture to use.
```

### 🧐 解析
- **原因**: YouTubeが埋め込んでいるサードパーティのスクリプト（広告やトラッキング、または埋め込みプレーヤーの機能）が、ブラウザのストレージ（Cookieなど）にアクセスしようとしてブロックされています。
- **TubeWikiとの関係**: **無関係**です。
- **対策**: 無視して問題ありません。最近のブラウザ（特にChromeやSafari）のプライバシー保護機能による通常の挙動です。

---

# 🚨 エラー2: `Cannot redefine property: ethereum`

```
evmAsk.js:15 Uncaught TypeError: Cannot redefine property: ethereum
MetaMask encountered an error setting the global Ethereum provider...
```

### 🧐 解析
- **原因**: 複数の仮想通貨ウォレット拡張機能（例: MetaMask, Coinbase Wallet, Phantomなど）がインストールされており、互いに `window.ethereum` というグローバル変数を奪い合っています。
- **TubeWikiとの関係**: **無関係**です。TubeWikiはブロックチェーン機能を使用していません。
- **対策**: 開発に支障がなければ無視して構いません。気になる場合は、使用していないウォレット拡張機能を無効化してください。

---

# ℹ️ ログ: `[TubeWiki] handleExport called`

```
[TubeWiki] handleExport called
```

### 🧐 解析
- **内容**: これはTubeWikiが出力している正常なデバッグログです。
- **意味**: 「Export to Notion」ボタンがクリックされ、処理が開始されたことを示しています。
- **状態**: **正常**です。この後にエラーが続いていなければ、処理は順調に進んでいます。

---

# ⚠️ その他の無視して良いエラー

### `LegacyDataMixin will be applied to all legacy elements`
- **原因**: YouTubeが使用している古いWebコンポーネントライブラリ（Polymerなど）の警告です。
- **対策**: 無視してください。

### `Failed to execute 'postMessage' on 'DOMWindow'`
- **原因**: YouTube Studioなど、異なるオリジン（ドメイン）間で通信しようとしてブロックされたブラウザのセキュリティ警告です。
- **対策**: 無視してください。TubeWikiの機能には影響しません。

---

# ✅ 結論

今回報告されたエラーログの中に、**TubeWikiの動作を阻害する致命的なエラーは見当たりません。**

- 赤いエラー（Permission denied, TypeError）は、YouTube自体や他の拡張機能に起因するものです。
- TubeWikiのログは正常に出力されています。

もし「ボタンを押しても反応がない」「通知が出ない」といった症状がある場合は、その直後のログを確認する必要があります。
