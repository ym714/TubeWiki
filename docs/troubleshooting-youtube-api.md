---
marp: true
theme: default
paginate: true
header: "TubeWiki Troubleshooting Report"
footer: "2025-12-09"
---

# 🐛 トラブルシューティング報告: YouTube Transcript API

## 🚨 発生していた問題

### エラー内容
WorkerサービスでYouTubeの字幕を取得する際に、以下のエラーが発生していました。

```
AttributeError: type object 'YouTubeTranscriptApi' has no attribute 'list_transcripts'
```

### 原因
インストールされている `youtube-transcript-api` ライブラリのバージョン（v1.2.3）が、コードが想定していた古いAPI（静的メソッド）とは異なる、新しいインスタンスベースのAPIを採用していたため。

- **旧コード**: `YouTubeTranscriptApi.list_transcripts(video_id)` (静的メソッド)
- **現行ライブラリ**: `YouTubeTranscriptApi().list(video_id)` (インスタンスメソッド)

---

## 🛠 実施した修正

`worker/services/youtube.py` をリファクタリングし、新しいAPI仕様に合わせました。

### 変更点
1. **インスタンス化**: `yt_api = YouTubeTranscriptApi()` を追加。
2. **メソッド呼び出しの変更**:
   - `list_transcripts(id)` -> `list(id)`
   - `get_transcript(id)` -> `fetch(id)`
3. **データ取得ロジックの修正**:
   - `fetch()` が返す `FetchedTranscript` オブジェクト（イテレータ）を正しく扱うように修正。

---

## ✅ 検証結果

修正後、`scripts/manual_test.py` を実行し、正常に動作することを確認しました。

- **字幕取得**: 成功 (21,531文字)
- **AI要約**: 成功 (Groq API使用)
- **出力**: `output.md` が正常に生成されました。

これにより、TubeWikiのバックエンド（Worker）は正常に機能していることが確認できました。
