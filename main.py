import os
import csv
from pathlib import Path

import requests
import xml.etree.ElementTree
from dotenv import load_dotenv

base_dir = Path(__file__).resolve().parent
csv_dir = base_dir / "csv"
target_csv = csv_dir / "target.csv"
result_csv = csv_dir / "fetch_result.csv"


def fetch_request(numbers: list[str],
                  version: int = 1,
                  request_type: str = "12",
                  history: int = 0) -> requests.Response:
    """
    APIにリクエストを発行し、レスポンスを返す
    :param version: APIのバージョン
    :param numbers: 法人番号のリスト
    :param request_type: 01:CSV 形式/Shift-JIS, 02:CSV 形式/Unicode, 12:XML 形式/Unicode
    :param history: 変更履歴を取得するかどうか。0:取得しない, 1:取得する
    :return:
    """

    params = {
        "id": api_id,
        "number": ",".join(numbers),
        "type": request_type,
        "history": history

    }
    base_url = f"https://api.houjin-bangou.nta.go.jp/{version}/num"
    return requests.get(base_url, params=params)


def write_csv_by_xml(xml_text: str):
    """
    結果をCSVファイルに書き込む
    :param xml_text: APIからのレスポンスのXMLテキスト
    """

    root = xml.etree.ElementTree.fromstring(xml_text)
    with open(result_csv, "a", encoding="utf-8", newline="") as file:
        fields = ["法人番号", "法人名"]
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")

        for corporation in root.findall(".//corporation"):
            name = corporation.find("name").text
            number = corporation.find("corporateNumber").text
            writer.writerow({"法人番号": number, "法人名": name})


def get_corporate_number_list():
    """
    csv/target.csvから法人番号のリストを取得する

    リクエストが10件ずつしか受け入れないので、10件ずつ法人番号のリストを返す
    """

    with open(target_csv, "r", encoding="utf-8") as file:
        fieldnames = ["法人番号"]
        reader: csv.DictReader = csv.DictReader(file, fieldnames=fieldnames)

        corporate_numbers = []
        for row in reader:
            corporate_numbers.append(row["法人番号"])
            if len(corporate_numbers) == 10:
                yield corporate_numbers
                corporate_numbers = []
        yield corporate_numbers


def remove_and_create_result_csv():
    """取得結果ファイルを初期化する"""

    if result_csv.exists():
        result_csv.unlink()
    fields = ["法人番号", "法人名"]
    with open(result_csv, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()


if __name__ == "__main__":
    load_dotenv()
    api_id = os.getenv("API_ID")

    remove_and_create_result_csv()
    corporate_number_list = get_corporate_number_list()
    for corp_num in corporate_number_list:
        xml_data = fetch_request(corp_num).text
        write_csv_by_xml(xml_data)
