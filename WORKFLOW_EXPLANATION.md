# GitHub Actions Workflow 解説

## publish.yml の詳細解説

### 1. ワークフロー名とトリガー

```yaml
name: Publish articles

on:
  push:
    branches:
      - main
      - master
  workflow_dispatch:
```

**解説：**
- `name`: ワークフローの名前。GitHub ActionsのUIに表示されます
- `on.push`: `main`または`master`ブランチにプッシュされたときに自動実行
- `workflow_dispatch`: GitHubのUIから手動実行も可能（「Actions」タブから実行ボタンが表示される）

### 2. 権限設定

```yaml
permissions:
  contents: write
```

**解説：**
- `contents: write`: リポジトリの内容を書き込む権限
- これにより、Qiita形式の記事を`qiita/public/`に生成・コミットできます

### 3. 並行実行制御

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: false
```

**解説：**
- `concurrency`: 同じワークフローが同時に複数実行されるのを防ぐ
- `group`: 同じブランチでの実行をグループ化
- `cancel-in-progress: false`: 実行中のワークフローをキャンセルしない（安全のため）

### 4. ジョブの実行

```yaml
jobs:
  publish_articles:
    runs-on: ubuntu-latest
    timeout-minutes: 5
```

**解説：**
- `runs-on`: Ubuntuの最新版で実行
- `timeout-minutes`: 5分でタイムアウト（無限実行を防ぐ）

### 5. ステップ1: コードのチェックアウト

```yaml
- name: Checkout
  uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

**解説：**
- `actions/checkout@v4`: リポジトリのコードを取得
- `fetch-depth: 0`: 全履歴を取得（変更されたファイルを検出するため）

### 6. ステップ2: zenn-qiita-syncの実行

```yaml
- name: Run
  uses: C-Naoki/zenn-qiita-sync@main
  with:
    qiita-token: ${{ secrets.QIITA_TOKEN }}
```

**解説：**
- `C-Naoki/zenn-qiita-sync@main`: 公開されているGitHub Actionを使用
- このアクションが以下を自動実行：
  1. **変更検出**: `articles/`内で変更された`.md`ファイルを検出
  2. **形式変換**: Zenn形式 → Qiita形式に変換
  3. **ファイル生成**: `qiita/public/`にQiita形式の記事を生成
  4. **自動投稿**: Qiita CLIを使用してQiitaに投稿

## zenn-qiita-syncの内部動作

### 処理フロー

1. **変更ファイルの検出**
   ```bash
   git diff --name-only ${{ github.event.before }} ${{ github.sha }} | grep "^articles/.*\.md$"
   ```
   - 前回のコミットと現在のコミットを比較
   - `articles/`内の`.md`ファイルのみを抽出

2. **記事の変換**
   - `published: true`が設定されている記事のみ処理
   - Zenn形式のフロントマターをQiita形式に変換
   - 画像パスなどの調整も自動実行

3. **Qiitaへの投稿**
   - `qiita/public/`に生成されたファイルをQiita CLIで投稿
   - 既存記事の場合は更新、新規記事の場合は作成

## よくある質問

### Q: どのタイミングで実行される？
A: `main`または`master`ブランチにプッシュしたとき、または手動実行したとき

### Q: エラーが発生したら？
A: GitHub Actionsのログを確認してください。「Actions」タブから各実行の詳細を見られます

### Q: 特定の記事だけを投稿したい？
A: `published: true`を設定した記事のみが投稿されます。`published: false`にすると投稿されません
