from pathlib import Path

import csv

base_dir = Path(__file__).resolve().parent
csv_dir = base_dir / "csv"
target_csv = csv_dir / "target.csv"
result_csv = csv_dir / "fetch_result.csv"


def create_target_corporations() -> list[dict[str, str, str]]:
    """
    csv/target.csvから登録番号、事業者名、法人番号の辞書を内包するリスト作成し返す
    :return: 登録番号、事業者名、法人番号の辞書を内包するリスト
    """

    with open(target_csv, "r", encoding="utf-8") as file:
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


def write_result_csv(target_corporations: list[dict], fetched_data: dict[str, dict[str, str]]):
    """
    取得結果をcsvに書き込む

    :param target_corporations:
    :param fetched_data:
    """

    for corp in target_corporations:
        address = fetched_data.get(corp["法人番号"], {}).get("address", "")
        corp["住所"] = address
        corp["登録有無"] = True if address else False
    fields = ["登録番号", "事業者名", "法人番号", "住所", "登録有無"]

    with result_csv.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(target_corporations)
