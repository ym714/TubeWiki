---
marp: true
theme: default
paginate: true
header: 'TubeWiki - Deployment Strategy Analysis'
footer: '© 2025 TubeWiki'
---

# デプロイメント戦略とコスト分析

**「常時稼働」のリスクと最適な選択肢**

---

## 🧐 ユーザーの懸念

> "Railwayにデプロイしたら常に動き続けるから良くないのでは？"

**その通りです。**
一般的なPaaS（Railway, Heroku, Render等）のコンテナデプロイは、リクエストがなくてもサーバー（コンテナ）が起動し続けるため、**待機時間中もリソース（メモリ・CPU）に対して課金**されます。

### 潜在的なリスク
1.  **コスト**: アクセスが全くない夜間でも料金が発生する。
2.  **リソースの無駄**: 使っていないのにサーバーが動いている。

---

## 📊 選択肢の比較

TubeWiki（Core API + Worker）のデプロイ先として、以下の3つを比較します。

| 特徴 | 🚂 Railway | ▲ Vercel | ☁️ Google Cloud Run |
| :--- | :--- | :--- | :--- |
| **タイプ** | PaaS (常時稼働) | Serverless (FaaS) | Serverless Container |
| **課金モデル** | リソース使用量 (時間) | リクエスト数 + 実行時間 | リソース使用量 (リクエスト中のみ) |
| **Scale to Zero** | ❌ (基本不可) | ✅ **標準 (0秒)** | ✅ **標準 (0秒)** |
| **タイムアウト** | なし (無制限) | 10秒 (Hobby) / 300秒 (Pro) | 60分 (デフォルト5分) |
| **セットアップ** | 非常に簡単 | 簡単 (Python対応) | やや複雑 (Docker必須) |
| **月額目安** | $5〜 (Hobbyプラン) | $0 (Hobby) / $20 (Pro) | $0〜 (無料枠あり) |

---

## 💰 コスト試算 (個人開発規模)

### 1. Railway (Hobby Plan)
- **仕組み**: メモリ使用量 × 時間
- **無料枠**: 月額$5分のクレジット付与
- **試算**:
    - Core (512MB) + Worker (512MB) = 1GB
    - 常時稼働の場合、約$10/月 - $5(クレジット) = **$5/月** 程度の出費
    - ※リソースを絞れば無料枠に収まる可能性もあり

### 2. Vercel (Hobby Plan)
- **仕組み**: リクエスト数ベース
- **試算**:
    - アクセスが少なければ **完全無料**
    - **課題**: Workerの処理（動画取得+AI生成）が10秒を超えるとタイムアウトで強制終了するリスクあり。

### 3. Google Cloud Run
- **仕組み**: リクエスト処理中のCPU/メモリのみ課金
- **試算**:
    - アクセスがなければ **$0**
    - 無料枠が手厚いため、個人利用ならほぼ無料
    - **メリット**: Vercelのような厳しいタイムアウト制限がない（最大60分）。

---

## 🚀 推奨戦略

ユーザーの「無駄に動かし続けたくない」という意向を尊重し、以下の段階的な戦略を提案します。

### Plan A: Cloud Run (推奨 - コスト最適 & 柔軟)
Dockerコンテナをそのままデプロイでき、**使わない時は自動でゼロになり課金されない**ため、今回の要件に最も適しています。

- **Core API**: Cloud Runへデプロイ
- **Worker**: Cloud Runへデプロイ
- **メリット**: 完全従量課金、タイムアウトの心配なし。
- **デメリット**: 初回セットアップ（gcloud CLI等）がRailwayより少し手間。

### Plan B: Railway (簡単さ優先)
まずはRailwayでデプロイし、Hobbyプランの範囲内（$5クレジット）で運用できるか試す。

- **メリット**: 設定が圧倒的に楽。
- **デメリット**: $5を超えると課金発生。

---

## 🛠️ Cloud Runへの移行ステップ (Plan A採用の場合)

もしCloud Runを採用する場合、以下の手順になります。

1.  **Google Cloud Project作成**
2.  **gcloud CLIインストール**
3.  **Deployコマンド実行**:
    ```bash
    # Core API
    gcloud run deploy tubewiki-core --source ./core --allow-unauthenticated
    
    # Worker
    gcloud run deploy tubewiki-worker --source ./worker --allow-unauthenticated
    ```
4.  **環境変数設定**: GUIまたはCLIで設定。

---

## 📝 結論

**「常に動き続けるのが嫌」であれば、Railwayではなく Google Cloud Run が最適解です。**

- **Railway**: 開発体験は最高だが、常時稼働コストがかかる。
- **Cloud Run**: コンテナを使いつつ、サーバーレス（Scale to Zero）の恩恵を受けられる。

**次のアクション案:**
1.  とりあえず簡単さを取って **Railway** でデプロイしてみる（$5まで無料）。
2.  コスト最適化を目指して **Cloud Run** に挑戦する。

どちらの方針で進めますか？
