from pathlib import Path

import csv


class InvoiceCSVProcessor:
    """ インボイス情報取得対象企業のcsvファイルの読み書きを行うクラス """

    base_dir = Path(__file__).resolve().parent
    csv_dir = base_dir / "csv"
    target_csv = csv_dir / "target__corporations.csv"
    result_csv = csv_dir / "fetch_result.csv"

    def __init__(self):
        self.target_corporations = self._create_target_corporations()

    def _create_target_corporations(self) -> list[dict[str, str, str]]:
        """
        csv/target.csvから登録番号、事業者名、法人番号の辞書を内包するリスト作成し返す
        :return: 登録番号、事業者名、法人番号の辞書を内包するリスト
        """

        with open(self.target_csv, "r", encoding="utf-8") as file:
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
        return target_corporations

    def write_result_csv(self, fetched_data: dict[str, dict[str, str]]):
        """
        取得結果をcsvに書き込む
        :param fetched_data: APIから取得した法人番号と法人名、住所の辞書
        """

        for corp in self.target_corporations:
            address = fetched_data.get(corp["法人番号"], {}).get("address", "")
            corp["住所"] = address
            corp["登録有無"] = "有" if address else ""

        fields = ["登録番号", "事業者名", "法人番号", "住所", "登録有無"]
        with self.result_csv.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(self.target_corporations)
