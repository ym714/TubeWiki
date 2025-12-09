---
marp: true
theme: default
paginate: true
header: "Notion API Usage Guide"
footer: "2025-12-09 | TubeWiki Team"
---

# Notion API 活用ガイド

現在のNotion APIの基本的な使い方と主要な機能について

---

## 目次

1. Notion APIとは
2. 準備・認証（Authentication）
3. データベースの操作（Reading Data）
4. ページの作成（Writing Data）
5. 実装例（TypeScript）
6. 注意点とベストプラクティス

---

## 1. Notion APIとは

Notionのワークスペース内のページ、データベース、ユーザー情報にプログラムからアクセスするためのインターフェースです。

**主な機能:**
- ページの作成・更新・取得
- データベースのクエリ（フィルタリング・ソート）
- ブロック（テキスト、画像など）の操作
- ユーザー管理（一部）

**公式SDK:**
JavaScript/TypeScript向けに公式クライアントライブラリ `@notionhq/client` が提供されています。

---

## 2. 準備・認証（Authentication）

Notion APIを使用するには「インテグレーション」を作成し、対象のページへのアクセス権を付与する必要があります。

### 手順
1. **インテグレーションの作成**: [Notion My Integrations](https://www.notion.so/my-integrations) にアクセスし、"New integration" を作成します。
   - Type: Internal（社内用）または Public（配布用）
   - Capabilities: 必要な権限（Read content, Update content, Insert content）を選択
2. **APIトークンの取得**: "Internal Integration Secret" (例: `secret_...`) を取得します。これがAPIキーとなります。
3. **コネクションの追加**: 操作したいNotionページまたはデータベースの右上の「...」メニューから "Add connections" を選択し、作成したインテグレーションを追加します。
   - **重要**: 親ページに権限を付与すれば、その子ページにも継承されます。

---

## 3. データベースの操作（Reading Data）

データベースの内容を取得するには、データベースIDが必要です。

### データベースIDの取得方法
ブラウザでデータベースをフルページで開き、URLを確認します。
`https://www.notion.so/myworkspace/a8aec43384f447ed84390e8e42c2e089?v=...`
この場合、`a8aec43384f447ed84390e8e42c2e089` がデータベースIDです。

### データのクエリ
`databases.query` エンドポイントを使用します。
- **Filter**: 特定の条件（ステータス、日付など）で絞り込み
- **Sort**: 並び替え順序の指定

---

## 4. ページの作成（Writing Data）

新しいページを作成するには `pages.create` エンドポイントを使用します。

### 必要な情報
- **Parent**: 親となるデータベースID または ページID
- **Properties**: データベースのスキーマに合わせたプロパティ値（タイトル、タグ、日付など）
- **Children** (オプション): ページ内のコンテンツ（ブロック）

---

## 5. 実装例（TypeScript）

`@notionhq/client` を使用した基本的な実装例です。

```typescript
import { Client } from "@notionhq/client"

// クライアントの初期化
const notion = new Client({ auth: process.env.NOTION_KEY })

const databaseId = process.env.NOTION_DATABASE_ID

async function addItem(text: string) {
  try {
    const response = await notion.pages.create({
      parent: { database_id: databaseId },
      properties: {
        title: { 
          title:[
            {
              "text": {
                "content": text
              }
            }
          ]
        }
      },
    })
    console.log(response)
  } catch (error) {
    console.error(error.body)
  }
}
```

---

## 6. 注意点とベストプラクティス

- **APIバージョン**: Notion APIはバージョニングされています。SDKを使用すれば自動的に適切なバージョンが選択されますが、直接HTTPリクエストを送る場合は `Notion-Version` ヘッダー（例: `2022-06-28`）が必要です。
- **レートリミット**: 平均して1秒あたり3リクエストの制限があります。これを超えると `429 Too Many Requests` が返されます。
- **プロパティの型**: データベースのプロパティ型（Rich Text, Select, Dateなど）に合わせて、正しいJSON構造でデータを送信する必要があります。
- **権限管理**: インテグレーションは追加されたページ（およびその子ページ）にしかアクセスできません。「Not found」エラーが出る場合は、コネクション設定を確認してください。

---

## 参考リンク

- [Notion API 公式ドキュメント](https://developers.notion.com/)
- [Notion API Reference](https://developers.notion.com/reference)
- [GitHub - notionhq/client](https://github.com/makenotion/notion-sdk-js)
