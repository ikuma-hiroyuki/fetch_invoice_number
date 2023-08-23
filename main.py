import os
import xml.etree.ElementTree

import requests
from dotenv import load_dotenv

from utils import create_target_corporations, write_result_csv


def fetch_response(numbers: list[str],
                   version: int = 1,
                   request_type: str = "12",
                   history: int = 0) -> requests.Response:
    """
    APIにリクエストを発行し、レスポンスを返す
    :param version: APIのバージョン
    :param numbers: 法人番号のリスト (最大10件)。法人番号はハイフンなしの13桁。
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


def get_corporate_number_list(target_corporations: list[dict[str, str, str]]) -> list[list[str]]:
    """
    APIリクエストで取得できるデータ数が最大10件なので、法人番号のリストを10件ずつ返す
    :return: 法人番号のリスト
    """

    registration_numbers = []
    for corporate in target_corporations:
        registration_numbers.append(corporate["法人番号"])
        if len(registration_numbers) == 10:
            yield registration_numbers
            registration_numbers = []
    yield registration_numbers


def fetch_corporate_dict(corp_num_list: list[list[str]]) -> dict[str, dict[str, str]]:
    """
    APIにリクエストし、法人番号と法人名、住所の辞書を作成してして返す
    :return: 法人番号と法人名、住所の辞書
    """

    corp_dict = {}
    for corp_num in corp_num_list:
        xml_data = fetch_response(corp_num).text

        root = xml.etree.ElementTree.fromstring(xml_data).findall(".//corporation")
        for corp in root:
            name = corp.find("name").text
            number = corp.find("corporateNumber").text
            address = f'{corp.find("prefectureName").text}{corp.find("cityName").text}{corp.find("streetNumber").text}'
            corp_dict[number] = {"name": name, "address": address}
    return corp_dict


def create_result_csv():
    target_corporations = create_target_corporations()
    corporate_number_list = get_corporate_number_list(target_corporations)
    fetched_data = fetch_corporate_dict(corporate_number_list)
    write_result_csv(target_corporations, fetched_data)


if __name__ == "__main__":
    load_dotenv()
    api_id = os.getenv("API_ID")

    create_result_csv()
