# VSCode共同開発環境のセットアップ完了

このコミットには、VSCodeでチーム開発を行うための設定が含まれています。

## 📁 追加されたファイル

### ドキュメント
1. **COLLABORATION_GUIDE.md** - VSCode共同作業ガイド
2. **CONTRIBUTING.md** - 開発ガイドライン
3. **VSCODE_COLLABORATION.md** - 詳細な共同作業手順

### VSCode設定（`.vscode/`ディレクトリ）
1. **settings.json** - プロジェクト共通設定
2. **extensions.json** - 推奨拡張機能
3. **launch.json** - デバッグ設定

## 🚀 次の手順

### オプション1: リポジトリオーナー（Shiori810さん）がプッシュ

リポジトリのオーナーがこれらの変更をプッシュしてください：

```bash
cd ~/Bakery_system
git push origin main
```

### オプション2: コラボレーターとして追加

1. **Shiori810さんにコラボレーター追加を依頼**
   - GitHub: https://github.com/Shiori810/Bakery_system/settings/access
   - 「Add people」→ SATOET を追加

2. **招待を承認後、再度プッシュ**

### オプション3: Fork & Pull Request

```bash
# 1. GitHubでForkを作成
# https://github.com/Shiori810/Bakery_system → Forkボタン

# 2. 自分のForkをリモートに追加
cd ~/Bakery_system
git remote add myfork https://github.com/SATOET/Bakery_system.git

# 3. 自分のForkにプッシュ
git push myfork main

# 4. GitHubでPull Requestを作成
# https://github.com/Shiori810/Bakery_system/pulls
```

## 📝 変更内容の確認

現在のコミット状態を確認：

```bash
git log --oneline -1
git show HEAD --stat
```

## ✅ VSCodeでの共同作業を開始

設定がプッシュされた後、チームメンバーは：

```bash
# 1. 最新コードを取得
git pull origin main

# 2. VSCodeで開く
code .

# 3. 推奨拡張機能をインストール
# VSCodeが自動的に提案します

# 4. Live Shareで共同編集開始！
# ステータスバーの「Live Share」をクリック
```

## 🎯 Live Shareの使い方（クイックリファレンス）

### ホスト側
1. VSCode下部「Live Share」をクリック
2. 「Start collaboration session」
3. 招待リンクをコピーして送信

### ゲスト側
1. 受け取ったリンクをクリック
2. または `Ctrl+Shift+P` → "Live Share: Join"
3. リンクを貼り付け

## 📚 詳細ドキュメント

- **すぐに始めたい**: [COLLABORATION_GUIDE.md](COLLABORATION_GUIDE.md)
- **開発ルールを知りたい**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Live Shareの詳細**: [VSCODE_COLLABORATION.md](VSCODE_COLLABORATION.md)

---

準備完了！チームでの開発を楽しんでください！
