# 法人番号システム Web-API からの情報取得

## 概要

下記URLのWeb-APIを利用して、法人番号から法人名を取得する。

https://www.houjin-bangou.nta.go.jp/webapi/

## 使い方

1. .envにAPIキーを記載する。
2. csv/target.csvに取得したい法人番号を記載する。(ヘッダー不要)
3. main.pyを実行する
4. csv/result.csvに法人番号と法人名が出力される。