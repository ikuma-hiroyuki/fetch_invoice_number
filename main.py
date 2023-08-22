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
    :param numbers: 法人番号のリスト (最大10件)
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


def create_target_corporate_dict() -> dict[str, str]:
    """
    csv/target.csvから法人番号と法人名の辞書を作成して返す
    :return: 法人番号と法人名の辞書
    """

    with open(target_csv, "r", encoding="utf-8") as file:
        fieldnames = ["事業者名", "登録番号"]
        reader: csv.DictReader = csv.DictReader(file, fieldnames=fieldnames)
        next(reader)
        target_dict = {row["登録番号"].replace("-", "")[1:]: row["事業者名"] for row in reader}
        return target_dict


def get_corporate_number_list() -> list[list[str]]:
    """
    APIリクエストで取得できるデータ数が最大10件なので、法人番号のリストを10件ずつ返す
    :return: 法人番号のリスト
    """

    target_dict = create_target_corporate_dict()
    registration_numbers = []
    for key in target_dict.keys():
        registration_numbers.append(key)
        if len(registration_numbers) == 9:
            yield registration_numbers
            registration_numbers = []
    yield registration_numbers


def create_corporate_dict() -> dict[str, dict[str, str]]:
    """
    法人番号と法人名、住所の辞書を作成してして返す
    :return: 法人番号と法人名、住所の辞書
    """

    corporate_number_list = get_corporate_number_list()
    corp_dict = {}
    for corp_num in corporate_number_list:
        xml_data = fetch_request(corp_num).text

        root = xml.etree.ElementTree.fromstring(xml_data).findall(".//corporation")
        for corp in root:
            name = corp.find("name").text
            number = corp.find("corporateNumber").text
            address = f'{corp.find("prefectureName").text}{corp.find("cityName").text}{corp.find("streetNumber").text}'
            corp_dict[number] = {"name": name, "address": address}
    return corp_dict


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

    # remove_and_create_result_csv()
    # corporate_number_list = get_corporate_number_list()
    # for corp_num in corporate_number_list:
    #     xml_data = fetch_request(corp_num).text
    #     write_csv_by_xml(xml_data)

    d = create_corporate_dict()
    print(d)
