---
marp: true
theme: default
paginate: true
header: 'FlashNote AI - デプロイ先プラットフォーム分析'
footer: '© 2025 TubeWiki | 2025-12-03'
---

# FlashNote AI デプロイ先プラットフォーム分析

**ドキュメント間の矛盾と推奨プラットフォームの整理**

---

## 📋 現状の問題

プロジェクトのドキュメント内で、**デプロイ先プラットフォームに関する記載が統一されていない**状況が確認されました。

### ドキュメント間の矛盾

| ドキュメント | Core Service | Worker Service |
|:---|:---|:---|
| [technical_spec.md](file:///Users/motoki/projects/TubeWiki/technical_spec.md) | **Vercel** | **Cloud Run** |
| [architecture-decisions.md](file:///Users/motoki/projects/TubeWiki/docs/architecture-decisions.md) | **Vercel** | **Cloud Run** |
| [roadmap-to-launch.md](file:///Users/motoki/projects/TubeWiki/docs/roadmap-to-launch.md) | Railway / Render / Vercel | Railway / Render / Vercel |
| [next-steps.md](file:///Users/motoki/projects/TubeWiki/docs/next-steps.md) | **Railway** (推奨) | **Railway** (推奨) |

---

## 🎯 技術仕様書での採用プラットフォーム

### Core Service: Vercel Serverless Functions

**選定理由**:
- ユーザーからのAPIリクエスト（認証、データ取得）は**低レイテンシ**が重要
- Vercelは起動が爆速（ミリ秒単位）、エッジに近い配置
- HTTPリクエスト/レスポンスに特化した設計

**制限事項**:
- 実行時間制限（通常10秒〜60秒）
- 重いAI処理には不向き

---

### Worker Service: Google Cloud Run

**選定理由**:
- 動画の字幕取得やGPT-4oによる生成は**数分かかる**場合がある
- Vercelのタイムアウト制限を超えるため、**長時間実行可能**な環境が必要
- 最大60分まで実行可能
- **Scale-to-Zero**: リクエストがない時はインスタンス数0になり、課金されない

**技術的優位性**:
- コンテナをそのまま実行可能
- Dockerfileベースのデプロイ
- CPU/メモリの柔軟な設定

---

## 🔄 ロードマップでのRailway推奨

### なぜRailwayが推奨されているのか？

[next-steps.md](file:///Users/motoki/projects/TubeWiki/docs/next-steps.md#L85) では「推奨プラットフォーム: Railway」と記載されています。

**Railwayの利点**:
- シンプルなデプロイフロー（GitHubと連携）
- Core/Worker両方を**同一プラットフォーム**で管理可能
- 環境変数の一元管理
- 開発者体験（DX）が良い

**想定される背景**:
- 初期段階では**運用の簡素化**を優先
- 複数プラットフォームの管理コストを避けたい
- 小規模トラフィックでは十分な性能

---

## 📊 各プラットフォームの比較

### Vercel + Cloud Run（技術仕様書の構成）

| 項目 | 評価 | 詳細 |
|:---|:---:|:---|
| **パフォーマンス** | ⭐⭐⭐⭐⭐ | 各サービスが最適化された環境で動作 |
| **コスト効率** | ⭐⭐⭐⭐⭐ | 完全なScale-to-Zero、使用量課金 |
| **運用複雑度** | ⭐⭐ | 2つのプラットフォームを管理 |
| **スケーラビリティ** | ⭐⭐⭐⭐⭐ | 無限にスケール可能 |
| **長時間処理** | ⭐⭐⭐⭐⭐ | Cloud Runで最大60分 |

---

### Railway（ロードマップの推奨）

| 項目 | 評価 | 詳細 |
|:---|:---:|:---|
| **パフォーマンス** | ⭐⭐⭐⭐ | 十分な性能、ただし専門特化ではない |
| **コスト効率** | ⭐⭐⭐ | 従量課金だが、常時起動の可能性 |
| **運用複雑度** | ⭐⭐⭐⭐⭐ | 単一プラットフォームで管理が容易 |
| **スケーラビリティ** | ⭐⭐⭐⭐ | 十分にスケール可能 |
| **長時間処理** | ⭐⭐⭐⭐ | 対応可能 |

---

## 🤔 どちらを採用すべきか？

### フェーズ別の推奨

#### Phase 1: MVP〜初期リリース（現在）
**推奨: Railway（Core + Worker両方）**

**理由**:
- 運用の簡素化が最優先
- 単一プラットフォームでの管理が容易
- デプロイの学習コストが低い
- 初期トラフィックでは十分な性能

---

#### Phase 2: 成長期（ユーザー増加後）
**推奨: Vercel (Core) + Cloud Run (Worker)**

**理由**:
- トラフィック増加に伴う**コスト最適化**が重要に
- 各サービスの特性に合わせた最適化
- Scale-to-Zeroによる**コスト削減効果**が顕著に
- パフォーマンスの最大化

**移行タイミング**:
- 月間アクティブユーザーが1,000人を超えた時
- インフラコストが月$100を超えた時
- レスポンス速度の改善が必要になった時

---

## 🎯 推奨アクション

### 1. ドキュメントの統一

現在のフェーズに合わせて、ドキュメントを更新する必要があります。

**提案**:
- [technical_spec.md](file:///Users/motoki/projects/TubeWiki/technical_spec.md) に「Phase 1: Railway」「Phase 2: Vercel + Cloud Run」のセクションを追加
- [roadmap-to-launch.md](file:///Users/motoki/projects/TubeWiki/docs/roadmap-to-launch.md) で「現在はRailway、将来的にVercel + Cloud Runへ移行」と明記

---

### 2. 環境構成の明確化

```
┌─────────────────────────────────┐
│  Production                     │
│  - Core: Railway                │
│  - Worker: Railway              │
│  - DB: Supabase                 │
│  - Extension: Chrome Web Store  │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│  Staging                        │
│  - Core: Railway (staging)      │
│  - Worker: Railway (staging)    │
│  - DB: Supabase (staging)       │
│  - Extension: Local build       │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│  Development                    │
│  - Core: localhost:8000         │
│  - Worker: localhost:8001       │
│  - DB: Supabase (dev)           │
│  - Extension: Local build       │
└─────────────────────────────────┘
```

---

### 3. 移行計画の策定

将来的なVercel + Cloud Runへの移行を見据えた準備:

**今すぐ実施**:
- [ ] 環境変数の管理方法を標準化（`.env.example`の整備）
- [ ] Dockerfileの最適化（Cloud Run対応を意識）
- [ ] CORSやドメイン設定を環境変数化

**Phase 2移行時**:
- [ ] Vercel用の設定ファイル（`vercel.json`）を作成
- [ ] Cloud Runデプロイスクリプトの作成
- [ ] 段階的な移行（まずCoreのみVercelへ）

---

## 📝 結論

### 現在の状況

**Railwayを採用しようとしている**というよりは、**初期段階の運用簡素化のためにRailwayを推奨している**状態です。

### 技術的な最終目標

技術仕様書に記載されている **Vercel + Cloud Run** が、アーキテクチャ的に最適な構成として設計されています。

### 推奨アプローチ

1. **Phase 1（現在〜初期リリース）**: Railway（Core + Worker）
2. **Phase 2（成長期）**: Vercel (Core) + Cloud Run (Worker)

この段階的なアプローチにより、**初期の運用負荷を抑えつつ、将来的なスケーラビリティとコスト最適化を実現**できます。

---

## 🔗 参考ドキュメント

- [technical_spec.md](file:///Users/motoki/projects/TubeWiki/technical_spec.md) - 技術仕様書（Vercel + Cloud Run）
- [architecture-decisions.md](file:///Users/motoki/projects/TubeWiki/docs/architecture-decisions.md) - アーキテクチャ決定の背景
- [roadmap-to-launch.md](file:///Users/motoki/projects/TubeWiki/docs/roadmap-to-launch.md) - リリースまでのロードマップ
- [next-steps.md](file:///Users/motoki/projects/TubeWiki/docs/next-steps.md) - 次のステップ（Railway推奨）

---

## ❓ 次のアクション

**ユーザーへの質問**:

1. **Phase 1でRailwayを採用する方針で進めますか？**
   - YES → Railway用のデプロイ設定を整備
   - NO → 最初からVercel + Cloud Runで構築

2. **Phase 2への移行タイミングの目安は？**
   - ユーザー数、コスト、パフォーマンス指標など

3. **ドキュメントの統一を実施しますか？**
   - technical_spec.mdにPhase 1/2の記載を追加
