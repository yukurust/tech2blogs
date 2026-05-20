# CLIでのスラッグ作成について

## 結論：毎回CLIでスラッグを作る必要はありません！

Zenn CLIで記事を作成する際、**スラッグ（ファイル名）は必須ではありません**。以下の3つの方法があります：

## 方法1: CLIでテンプレートを作成（推奨）

```bash
npx zenn new:article --slug 記事のスラッグ --title タイトル
```

**メリット：**
- フロントマターが自動生成される
- タイトルが自動的に設定される
- ファイル名とスラッグが一致する

**例：**
```bash
npx zenn new:article --slug obsidian-cursor-setup --title "ObsidianとCursorのセットアップ"
```

→ `articles/obsidian-cursor-setup.md` が作成される

## 方法2: 手動でファイルを作成（最も柔軟）

CLIを使わず、直接`articles/`ディレクトリに`.md`ファイルを作成することも可能です。

**必要なフロントマター：**
```markdown
---
title: "記事のタイトル"
emoji: "😊"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: [タグ1, タグ2]
published: true
---

# 記事のタイトル

ここから本文...
```

**メリット：**
- ファイル名を自由に決められる
- 既存のObsidianノートをコピーして使える
- CLIをインストールする必要がない

**注意点：**
- フロントマターを正しく記述する必要がある
- ファイル名は任意（スラッグとして使用される）

## 方法3: 既存ファイルをコピーして編集

既存の記事ファイルをコピーして、内容を編集する方法も可能です。

```bash
cp articles/お試し.md articles/新しい記事.md
# その後、内容を編集
```

## スラッグのルール

- **ファイル名 = スラッグ**: Zennでは、ファイル名（拡張子を除く）がスラッグとして使用されます
- **使用可能な文字**: 英数字、ハイフン、アンダースコア
- **日本語ファイル名**: 可能ですが、URLが長くなるため英数字推奨

## 実際の使用例

### 例1: CLIで作成
```bash
npx zenn new:article --slug my-first-article --title "初めての記事"
```

### 例2: 手動で作成
`articles/my-first-article.md` を直接作成：
```markdown
---
title: "初めての記事"
emoji: "🎉"
type: "tech"
topics: [Zenn, ブログ]
published: true
---

# 初めての記事

本文...
```

### 例3: Obsidianノートから移行
既存のObsidianノート（例：`メモ管理の沼から抜け出し、AIで自分専用のエコシステムを構築する方法.md`）を`articles/`にコピーし、フロントマターを追加：

```markdown
---
title: "メモ管理の沼から抜け出し、AIで自分専用のエコシステムを構築する方法"
emoji: "🤖"
type: "tech"
topics: [Obsidian, Cursor, AI]
published: true
---

（既存の内容）
```

## 推奨ワークフロー

1. **新規記事**: CLIでテンプレート作成 → 編集
2. **既存ノートの移行**: 手動でファイル作成 → フロントマター追加
3. **既存記事の更新**: そのまま編集（CLI不要）

## まとめ

- ✅ **CLIは必須ではない** - 手動でファイルを作成してもOK
- ✅ **ファイル名は自由** - ただし、URLに使われるので英数字推奨
- ✅ **フロントマターが重要** - `published: true`を忘れずに
- ✅ **既存ノートの再利用可能** - Obsidianノートをコピーして使える
