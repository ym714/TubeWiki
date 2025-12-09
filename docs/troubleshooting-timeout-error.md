---
marp: true
theme: default
paginate: true
header: "TubeWiki Troubleshooting: Timeout"
footer: "2025-12-06"
---

# 🚨 トラブルシューティング: Timeout waiting for note generation

### 症状
- 「Export to Notion」ボタンを押した後、しばらくロード中になり、最終的にエラーになる。
- コンソールログ: `Error: Timeout waiting for note generation`

---

# 🧐 原因解析

このエラーは、**「Core APIは依頼を受け付けたが、Workerが60秒以内に処理を完了できなかった」** ことを意味します。

考えられる原因は3つあります：

1.  **Workerのコールドスタート (Cold Start)**
    - Railwayの無料プランや設定によっては、しばらく使っていないとWorkerが停止（スリープ）します。
    - 再起動には数十秒かかるため、最初の1回目はタイムアウトしやすいです。

2.  **動画が長すぎる**
    - 長時間の動画（1時間以上など）は、字幕の取得やAIの要約に時間がかかります。
    - 現在のタイムアウト設定（60秒）を超えてしまうことがあります。

3.  **AI APIの遅延**
    - 使用しているLLM（Groq/OpenAI）の応答が遅れている場合も、全体の処理時間が伸びます。

---

# 🛠 対策

### 1. もう一度試す（Retry）
- 原因が「コールドスタート」の場合、2回目はWorkerが起きているため、すぐに完了する可能性が高いです。
- ページをリロードして、もう一度ボタンを押してみてください。

### 2. 短い動画でテストする
- 3〜5分程度の短い動画で試してみてください。
- これで成功する場合、システム自体は正常で、単に処理時間の問題です。

### 3. ログを確認する (Railway)
- Railwayのダッシュボードで `Worker` サービスのログを確認してください。
- エラー（赤文字）が出ていれば、それが真の原因です（例: API Key切れ、字幕取得エラーなど）。

---

# ℹ️ 技術的な詳細

現在のタイムアウト設定は、拡張機能側で **60秒**（2秒間隔 × 30回ポーリング）になっています。

```typescript
// extension/src/content/ExportBar.tsx
while (attempts < 30) {
    await new Promise(resolve => setTimeout(resolve, 2000))
    // ...
}
```

頻繁にタイムアウトする場合は、この回数を増やす修正が必要かもしれません。
