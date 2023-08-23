# 法人番号システム Web-API からの情報取得

## 概要

下記URLのWeb-APIを利用して、法人番号から法人名を取得する。

https://www.houjin-bangou.nta.go.jp/webapi/

## 使い方

1. .envにAPIキーを記載する。
2. csv/target_corporations.csvに取得したい事業者名、登録番号(Tから始まる13桁の番号)を記載する。(要ヘッダー)
3. main.pyを実行する
4. csv/result.csvに登録番号、事業者名、法人番号、住所、登録有無が出力される。