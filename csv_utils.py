import csv
from pathlib import Path


class InvoiceCSVProcessor:
    """ インボイス情報取得対象企業のcsvファイルの読み書きを行うクラス """

    def __init__(self, target_path: Path, result_path: Path):
        self.target_path = target_path
        self.result_path = result_path
        self.corporations = self._create_target_corporations()

    def _create_target_corporations(self) -> list[dict[str, str, str]]:
        """
        resource/target.csvから登録番号、事業者名、法人番号の辞書を内包するリスト作成し返す
        :return: 登録番号、事業者名、法人番号の辞書を内包するリスト
        """

        try:
            with open(self.target_path, "r", encoding="utf-8") as file:
                fieldnames = ["事業者名", "登録番号"]
                reader: csv.DictReader = csv.DictReader(file, fieldnames=fieldnames)
                next(reader)
                target_corporations = []
                for row in reader:
                    target_corporations.append({
                        "登録番号": row["登録番号"],
                        "事業者名": row["事業者名"],
                        "法人番号": row["登録番号"].replace("-", "")[1:]
                    })
        except FileNotFoundError:
            target_corporations = []
        return target_corporations

    def write_result_csv(self, fetched_data: dict[str, dict[str, str]]):
        """
        取得結果をcsvに書き込む
        :param fetched_data: APIから取得した法人番号と法人名、住所の辞書
        """

        for corp in self.corporations:
            address = fetched_data.get(corp["法人番号"], {}).get("address", "")
            corp["住所"] = address
            corp["国税庁登録名"] = fetched_data.get(corp["法人番号"], {}).get("name", "")

        fields = ["事業者名", "国税庁登録名", "登録番号", "法人番号", "住所"]
        with self.result_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(self.corporations)
