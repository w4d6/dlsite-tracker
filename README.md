# DLsite Tracker

DLsiteの作品情報（お気に入り数・販売数）を定期的に取得してGoogle Sheetsに記録するGitHub Actions。

## セットアップ手順

### 1. Google Cloud Platform でサービスアカウントを作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（または既存のプロジェクトを使用）
3. **APIとサービス** → **ライブラリ** から以下を有効化:
   - Google Sheets API
   - Google Drive API
4. **APIとサービス** → **認証情報** → **認証情報を作成** → **サービスアカウント**
5. サービスアカウント名を入力して作成
6. 作成したサービスアカウントをクリック → **キー** タブ → **鍵を追加** → **新しい鍵を作成** → **JSON**
7. ダウンロードされたJSONファイルを保存

### 2. Google スプレッドシートに権限を付与

1. 対象のスプレッドシートを開く
2. **共有** ボタンをクリック
3. サービスアカウントのメールアドレス（`xxx@xxx.iam.gserviceaccount.com`）を追加
4. **編集者** 権限を付与

### 3. GitHub リポジトリにシークレットを設定

1. GitHubリポジトリの **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** をクリック
3. Name: `GOOGLE_CREDENTIALS`
4. Value: ダウンロードしたJSONファイルの中身全体をペースト

### 4. GitHub Actions の実行

- **自動実行**: 毎日 AM 9:00 (JST) に実行
- **手動実行**: Actions タブ → DLsite Tracker → Run workflow

## ローカルでのテスト

```bash
# 仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt

# 環境変数を設定（JSONファイルの内容）
export GOOGLE_CREDENTIALS='{"type": "service_account", ...}'

# 実行
python dlsite_tracker.py
```

## 対象作品の追加・変更

`dlsite_tracker.py` の `PRODUCT_IDS` リストを編集してください:

```python
PRODUCT_IDS = [
    "RJ01486587",  # 作品1
    "RJ01470011",  # 作品2
    # 新しい作品IDを追加
]
```

## 出力形式

| 実行日付 | タイトル | URL | お気に入り数 | 販売数 |
|----------|---------|-----|-------------|--------|
| 2025-12-15 | 作品名 | https://... | 540 | 192 |
