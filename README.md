# tech2blogs

ZennとQiitaに自動投稿できる環境を整えたリポジトリです。

※ [notes2blogs](https://github.com/yshi112358/notes2blogs) と同じレイアウトで作成しています。`articles/` は Zenn 側のソース記事のみ空にしており、現状は `articles/.gitkeep` でディレクトリだけ追跡しています（Qiita の `qiita/public/` や `images/` は notes2blogs 由来の複製があります）。

## ディレクトリ構造

```
.
├── .github
│   └── workflows
│       └── publish.yml
├── articles
│   └── <Zenn形式の記事>
├── books
│   └── <Zenn形式の本 (任意)>
├── images
│   └── <記事で使用する画像ファイル>
└── qiita
    └── public
        └── <Qiita形式の記事>
```

## セットアップ

### 1. Zenn CLIをインストール

```bash
npm install
```

### 2. Qiitaのアクセストークンを取得

[Qiitaの設定ページ](https://qiita.com/settings/tokens/new)からアクセストークンを取得してください。

詳細については、[Qiita CLIのドキュメント](https://github.com/increments/qiita-cli/tree/main#qiita-のトークンを発行する)を参照してください。

### 3. GitHubリポジトリにシークレット変数を登録

`https://github.com/yshi112358/tech2blogs/settings/secrets/actions/new` にアクセスして、以下の情報を登録してください：

- **Name**: `QIITA_TOKEN`
- **Secret**: 取得したQiitaのアクセストークン

### 4. 記事を作成

以下のコマンドで記事のテンプレートを作成できます：

```bash
npm run new:article -- --slug 記事のスラッグ --title タイトル
```

または、Zenn CLIを直接使用：

```bash
npx zenn new:article --slug 記事のスラッグ --title タイトル
```

**重要：ファイル名（スラッグ）の制約**

ファイル名（拡張子を除く）は記事のslugとなります。slugは半角英数字（a-z0-9）、ハイフン（-）、アンダースコア（_）の12〜50文字の組み合わせにする必要があります。

例：
- ✅ `obsidian-cursor-setup.md` (23文字)
- ✅ `my_first_article.md` (15文字)
- ❌ `お試し.md` (日本語は不可)
- ❌ `test.md` (11文字、12文字未満)

## 使い方

1. `articles/` ディレクトリにZenn形式の記事を作成・編集します
2. 記事のフロントマターに `published: true` を設定すると、自動的にQiita形式に変換されます
3. GitHubリポジトリにプッシュすると、GitHub Actionsが自動的に実行され：
   - Zenn形式の記事がQiita形式に変換され、`qiita/public/` に保存されます
   - Qiita CLIを使用してQiitaに自動投稿されます

## ローカルプレビュー

記事をローカルでプレビューする場合：

```bash
npm run preview
```

## 詳細ドキュメント

- [GitHub Actions Workflow 解説](./WORKFLOW_EXPLANATION.md) - workflowの動作を詳しく解説
- [CLIでのスラッグ作成について](./CLI_SLUG_GUIDE.md) - CLIを使わずに記事を作成する方法

## 参考

この環境は以下の記事を参考に構築しました：

- [Zenn vs Qiitaを終わらせに来た](https://zenn.dev/naoki0103/articles/zenn-qiita-sync-workflow)
- [zenn-qiita-sync](https://github.com/C-Naoki/zenn-qiita-sync)

## 注意事項

- `books/` に保存されている本については、Qiitaへの同期は行われません
- `published: true` が設定されている記事のみがQiitaに投稿されます
- 画像は `images/` ディレクトリに保存してください
