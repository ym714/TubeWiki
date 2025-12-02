---
marp: true
theme: default
paginate: true
header: FlashNote AI Architecture Decisions
footer: 2025-12-02 | Deep Dive
---

# FlashNote AI Architecture Decisions

## なぜこの技術スタックなのか？

本ドキュメントでは、FlashNote AIの技術選定における「なぜ？」を深掘りします。
特に **Cost Efficiency (コスト効率)** と **Scalability (スケーラビリティ)** の観点から解説します。

---

# 1. Compute: Vercel vs Cloud Run

## Core Service: Vercel Serverless Functions
*   **特性**: 起動が爆速（ミリ秒単位）、エッジに近い、HTTPリクエスト/レスポンスに特化。
*   **理由**: ユーザーからのAPIリクエスト（認証、データ取得）は「低レイテンシ」が命です。Vercelはこれに最適化されています。
*   **制限**: 実行時間制限（通常10秒〜60秒）があり、重いAI処理には向きません。

## Worker Service: Google Cloud Run
*   **特性**: コンテナをそのまま実行。最大60分まで実行可能。
*   **理由**: 動画の字幕取得やGPT-4oによる生成は数分かかる場合があります。Vercelのタイムアウト制限を超えるため、長時間実行可能なCloud Runが必要です。
*   **Scale-to-Zero**: リクエストがない時はインスタンス数0になり、課金されません。

---

# 2. Event Bus: Push (QStash) vs Pull (Redis)

## Pull型 (Redis List / SQS) の課題
*   **仕組み**: Workerが「新しいジョブある？」とキューに定期的に聞きに行く（ポーリング）。
*   **コスト**: 聞きに行くためのプロセス（Worker）を**常時起動**しておく必要があります。ジョブがなくてもサーバー代がかかります。

## Push型 (Upstash QStash) の採用理由
*   **仕組み**: QStashが「ジョブ来たよ！」とWorkerのURLを叩く（Webhook）。
*   **メリット**:
    1.  **完全なScale-to-Zero**: ジョブが来るまでWorkerは停止（0台）していてOK。QStashからのアクセスで初めて起動します。
    2.  **管理不要**: ポーリングのループ処理やデーモン管理コードを書く必要がありません。

---

# 3. Data Persistence: Transaction Pooler

## Serverless x Postgres の「接続数問題」
*   **現象**: Serverless Functionはアクセス増に伴い、数百〜数千個にスケールします。
*   **問題**: 各FunctionがDB接続を1つ開くと、Postgresの最大接続数（`max_connections`: 通常100程度）を瞬時に食いつぶし、エラーになります。

## Supabase Transaction Pooler (Port 6543)
*   **解決策**: アプリとDBの間に立ち、大量の接続リクエストを少数の実際のDB接続に「多重化」します。
*   **Transaction Mode**: トランザクション単位で接続を使い回すため、数千の同時クライアントを捌けます。
*   **結論**: Serverless構成では、直接接続 (5432) ではなく、必ずプーラー (6543) を使う必要があります。

---

# まとめ: コストとスケーラビリティの最適解

| レイヤー | 技術 | 選定理由 (Why?) |
| :--- | :--- | :--- |
| **Core** | **Vercel** | ユーザー体験（低レイテンシ）最優先。 |
| **Worker** | **Cloud Run** | 長時間処理対応 & コンテナ実行環境。 |
| **Queue** | **QStash (Push)** | 待機コストゼロ (Scale-to-Zero) の実現。 |
| **DB** | **Supabase (Pooler)** | Serverless特有の接続数枯渇問題の回避。 |

この構成により、**「使われていない時はコスト0円、アクセス集中時は無限にスケール」** する理想的なインフラを実現します。
