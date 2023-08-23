import os
import xml.etree.ElementTree

import requests
from dotenv import load_dotenv

from csv_utils import InvoiceCSVProcessor


class APIProcessor:
    """
    法人番号APIを利用して対象企業の法人番号と法人名、住所の辞書を作成するクラス
    https://www.houjin-bangou.nta.go.jp/webapi/
    """

    def __init__(self, target_corporations: list[dict[str, str, str]]):
        """
        対象企業のデータを渡すと、法人番号APIを利用して法人番号と法人名、住所の辞書を作成する
        :param target_corporations: 登録番号、事業者名、法人番号の辞書を内包するリスト
        """

        load_dotenv()
        self._api_id = os.getenv("API_ID")
        self._target_corporations: list[str] = self._get_corporate_number_list(target_corporations)
        self._fetch_data = self._set_fetch_data()

    @property
    def fetch_data(self):
        return self._fetch_data

    def _set_fetch_data(self):
        return self._fetch_corporate_dict()

    def _fetch_response(self, corporate_numbers, version: int = 1, history: int = 0) -> requests.Response:
        """
        APIにリクエストを発行し、レスポンスを返す
        :param version: APIのバージョン
        :param corporate_numbers: 法人番号のリスト (最大10件)。法人番号はハイフンなしの13桁。
        :param history: 変更履歴を取得するかどうか。0:取得しない, 1:取得する
        :return: レスポンス
        """

        params = {
            "id": self._api_id,
            "number": ",".join(corporate_numbers),
            "type": 12,
            "history": history
        }
        base_url = f"https://api.houjin-bangou.nta.go.jp/{version}/num"
        response = requests.get(base_url, params=params)
        return response

    @staticmethod
    def _get_corporate_number_list(target: list[dict[str, str, str]]) -> list[str]:
        """
        APIリクエストで取得できるデータ数が最大10件なので、法人番号のリストを10件ずつ返す
        :return: 法人番号のリスト
        """

        registration_numbers = []
        for corporate in target:
            registration_numbers.append(corporate["法人番号"])
            if len(registration_numbers) == 10:
                yield registration_numbers
                registration_numbers = []
        yield registration_numbers

    def _fetch_corporate_dict(self) -> dict[str, dict[str, str]]:
        """
        APIにリクエストし、法人番号と法人名、住所の辞書を作成してして返す
        :return: 法人番号と法人名、住所の辞書
        """

        def parse_xml_data(xml_data: str) -> dict[str, dict[str, str]]:
            """
            APIから取得したxmlデータをパースし、法人番号と法人名、住所の辞書を作成して返す
            :param xml_data: APIから取得したxmlデータ
            :return: 法人番号と法人名、住所の辞書
            """

            root = xml.etree.ElementTree.fromstring(xml_data).findall(".//corporation")
            parse_dict = {}
            for corp in root:
                name = corp.find("name").text
                number = corp.find("corporateNumber").text
                prefecture = corp.find("prefectureName").text
                city = corp.find("cityName").text
                street = corp.find("streetNumber").text
                address = f'{prefecture}{city}{street}'
                parse_dict[number] = {"name": name, "address": address}
            return parse_dict

        corp_dict = {}
        for corp_num in self._target_corporations:
            response = self._fetch_response(corp_num)
            if response.status_code == 200:
                corp_dict.update(parse_xml_data(response.text))
            else:
                print(f"右記の理由により、下記法人番号のリクエストに失敗しました。: {response.text}", end="")
                print(corp_num, end="\n\n")
        return corp_dict


if __name__ == "__main__":
    csv_processor = InvoiceCSVProcessor()
    if csv_processor.target_corporations:
        api_processor = APIProcessor(csv_processor.target_corporations)
        csv_processor.write_result_csv(api_processor.fetch_data)
        print("処理が完了しました。")
    else:
        print("csv/target_corporations.csvが見つかりませんでした。")
