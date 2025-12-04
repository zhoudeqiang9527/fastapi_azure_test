# Text Processing API

これはFastAPIベースのテキスト処理APIサービスです。全角/半角文字変換、数字抽出、CSVファイル処理など、さまざまなテキスト処理機能を提供します。

## 機能特性

### 1. 全角/半角文字変換
- `/convert/half-width` - テキストを半角文字に変換
- `/convert/full-width` - テキストを全角文字に変換

### 2. 数字抽出
- `/extract/numbers` - テキストからすべての数字を抽出し、最初の整数、浮動小数点数、数字文字列を識別

### 3. CSVファイル処理
- `/save/csv` - POSTリクエストでコンテンツを全角に変換し、CSVファイルとして保存
- `/getjson` - GETリクエストで同じディレクトリのsample.csvをJSON形式に変換して返す

## インストールと実行

### 環境要件
- Python 3.7+
- FastAPI
- Uvicorn

### 依存関係のインストール
```bash
pip install -r requirements.txt
```

### サービスの実行
メインのmain.pyファイルを直接実行してサービスを起動できます:
```bash
python main.py
```

サービスはデフォルトで http://localhost:8000 で動作します

## APIドキュメント

サービスを起動すると、以下のアドレスで自動生成されたAPIドキュメントにアクセスできます:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 設定

環境変数でCSVファイルの出力パスを設定できます:
- `CSV_OUTPUT_PATH` - CSVファイルの保存ディレクトリ、デフォルトは'output'

## サンプルデータ

プロジェクトにはサンプルCSVファイル(sample.csv)が含まれており、各種金融商品に関連する情報が含まれています。

## ライセンス

MIT