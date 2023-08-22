from pathlib import Path

import csv

base_dir = Path(__file__).resolve().parent
csv_dir = base_dir / "csv"
target_csv = csv_dir / "target.csv"
result_csv = csv_dir / "fetch_result.csv"


def create_target_corporate_dict() -> dict[str, str]:
    """
    csv/target.csvから登録番号をキー、事業者名を値とする辞書を作成して返す
    :return: 登録番号をキー、事業者名を値とする辞書
    """

    with open(target_csv, "r", encoding="utf-8") as file:
        fieldnames = ["事業者名", "登録番号"]
        reader: csv.DictReader = csv.DictReader(file, fieldnames=fieldnames)
        next(reader)
        target_dict = {row["登録番号"]: row["事業者名"] for row in reader}
        return target_dict


def remove_and_create_result_csv():
    """取得結果ファイルを初期化する"""

    if result_csv.exists():
        result_csv.unlink()
    fields = ["法人番号", "法人名"]
    with open(result_csv, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
