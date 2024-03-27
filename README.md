# azureapi

azureで関数作成する時のソース郡

## 開発概要

以下の仕様とします。

* API稼働フレームワークはAzure関数を使用する
* API入力は、以下のものを入力する
  - URLにクエリでJSONキーを指定する。(?key=key1)
  - POSTボディーにJSONデータを入れる
* API出力は以下のものとする
  - クエリで指定したJSONキーに対応した値をプレーンテキストで出力する

## 事前準備

Azureアカウントを作成していること。

＊本システムでしたらかかっても1日あたり0.01ドルですみます。

## Azure関数新規作成(Pythonでの作成)

Azure Functionsの開発環境をローカルマシンにセットアップします。

[Core Tools を使用してローカルで Azure Functions を開発する](https://learn.microsoft.com/ja-jp/azure/azure-functions/functions-run-local?tabs=windows%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-csharp)

macの場合、以下のコマンドになります。

```bash
brew tap azure/functions
brew install azure-functions-core-tools@4
# if upgrading on a machine that has 2.x or 3.x installed:
brew link --overwrite azure-functions-core-tools@4
```

Azure Functions Core Toolsをインストールし、新しいプロジェクトを作成します。

```bash
func init azureapi --worker-runtime python
cd azureapi
```

HTTPトリガーを追加します。

```bash
func new --template "HTTP Trigger" --name HttpTrigger
```

HttpTrigger内の__init__.pyに対して以下の内容で編集する。

```bash
import logging
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        key = req.params.get('key')
        if not key:
            return func.HttpResponse(
                "Please pass a key in the query string",
                status_code=400
            )

        data = req.get_json()
        value = data.get(key)

        if not value:
            return func.HttpResponse(
                f"Key '{key}' not found in JSON data",
                status_code=400
            )

        return func.HttpResponse(value)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return func.HttpResponse(
            "An error occurred while processing the request",
            status_code=500
        )
```

HttpTrigger内のfunction.jsonに対して以下の内容で編集する。

```bash
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": [
        "post"
      ]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

githubなどでソースを保管する。

ここまで作成したソースを以下の場所にも公開しています。

https://github.com/naritomo08/azureapi

## 展開方法

### git cloneを実施(本項から実施するときのみ実施。)

```bash
git clone https://github.com/naritomo08/azureapi.git
cd azureapi.git
rm -rf .git
```

### デプロイ実施

```bash
# 必要に応じてAzureにログイン
az login

# リソースグループ作成
az group create --name <RESOURCE_GROUP_NAME> --location japaneast

# ストレージ作成
az storage account create --name <STORAGE_NAME> --resource-group <RESOURCE_GROUP_NAME>

ストレージ名に大文字や感嘆符は使用せず、ストレージに日付をいれるなどオリジナルの名前にする。

＃ FunctionAppリソース作成
az functionapp create --consumption-plan-location japaneast --runtime python --runtime-version 3.9 --functions-version 3 --name <APP_NAME> --os-type linux --storage-account <STORAGE_NAME> --resource-group <RESOURCE_GROUP>

APP_NAMEに大文字や感嘆符は使用せず、APP_NAMEに日付をいれるなどオリジナルの名前にする。

# ローカル実行(本関数では実施不要、macでは実行不可)
func start

# デプロイ
func azure functionapp publish <APP_NAME>
```

URLを控える。

### 動作テスト

以下コマンドでテスト可能

ターミナルを立ち上げ、以下のコマンドを入力する
（{ドメイン名}、を実際のカスタムドメインのURLに置き換えてください）

```bash
curl -X POST -H "Content-Type: application/json" -d '{"name": "John", "age": "30"}' "<URL>?key=age"
```

30という値が返ってくること

### カスタムドメイン設定(必要に応じ)

AzureDNSで独自ドメイン登録してること。

ドメイン名に対応したSSL証明書(pfx形式、パスワードあり)も作成していること。

Azureコンソール操作で実施

設定方法：

[Azure FunctionでJSONパーサーAPIを作ってみる。](https://qiita.com/drafts/80eb6e69128cad675db2)

### 動作テスト(カスタムドメイン)

以下コマンドでテスト可能

ターミナルを立ち上げ、以下のコマンドを入力する
（{ドメイン名}、を実際のカスタムドメインのURLに置き換えてください）

```bash
curl -X POST -H "Content-Type: application/json" -d '{"name": "John", "age": "30"}' "https://<カスタムドメイン名>/api/httptrigger?key=age"
```

30という値が返ってくること