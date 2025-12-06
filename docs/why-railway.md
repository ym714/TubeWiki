---
marp: true
theme: default
paginate: true
header: 'TubeWiki - Architecture Decisions'
footer: '© 2025 TubeWiki'
---

# なぜ Railway を採用しているのか？

**TubeWiki アーキテクチャ選定の背景**

---

## 🚀 結論：開発効率と機能要件のベストバランス

TubeWiki が Railway を採用している主な理由は以下の3点です：

1. **長時間実行プロセスのサポート** (Worker Service)
2. **デプロイの容易さ** (Git-driven)
3. **Python/FastAPI との親和性**

---

## 1. 長時間実行プロセスのサポート (Worker Service)

TubeWiki の `worker` サービスは、AIによる動画要約生成という**重い処理**を担当します。

- **Vercel / AWS Lambda**: 
  - 実行時間に厳しい制限（例: 10秒〜数分）がある。
  - AI推論のような数分かかる処理には不向き。
- **Railway**:
  - コンテナベースで**時間無制限**のバックグラウンドプロセスを実行可能。
  - QStash からの Webhook を安定して受信・処理できる。

---

## 2. デプロイの容易さ (Git-driven)

開発フェーズにおける「スピード」を最優先しました。

- **GitHub 連携**:
  - `git push` するだけで自動ビルド・デプロイ。
  - PRごとのプレビュー環境も作成可能（必要であれば）。
- **設定レス (Zero Config)**:
  - `Dockerfile` がなくても、Nixpacks が自動で Python 環境を検出してビルド。
  - 複雑な YAML 設定（Kubernetes 等）が不要。

---

## 3. Python/FastAPI との親和性

- **ネイティブサポート**:
  - Python の依存関係解決（pip/poetry）がスムーズ。
  - FastAPI (Uvicorn) の起動コマンド設定が直感的。
- **環境変数管理**:
  - ダッシュボードから簡単に設定可能。
  - ローカル開発と本番環境の切り替えが容易。

---

## 🆚 他の選択肢との比較

| プラットフォーム | 判定 | 理由 |
| --- | --- | --- |
| **Railway** | ✅ **採用** | **Workerが動く + 設定が簡単。** |
| **Vercel** | ❌ 不採用 | タイムアウト制限により、AI Worker が動かせない。 |
| **Google Cloud Run** | ⚠️ 保留 | スケール・コスト面で優秀だが、初期設定（IAM, gcloud）が複雑。 |
| **AWS ECS/EC2** | ❌ 不採用 | 管理コストが高すぎる（オーバーエンジニアリング）。 |

---

## 🔮 将来的な展望

現在は Railway がベストですが、将来的に以下のような課題が出た場合は **Google Cloud Run** への移行を検討します：

- **コスト**: 常時起動コンテナのコストが増大した場合（Cloud Run はゼロスケールが可能）。
- **スケーラビリティ**: 秒間数千リクエストを超えるような大規模アクセスが発生した場合。

👉 **現状は「開発スピード」と「Workerの安定稼働」を優先して Railway を利用中。**
