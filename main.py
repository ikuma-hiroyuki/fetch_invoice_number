import argparse
from pathlib import Path

from api_utils import APIProcessor
from csv_utils import InvoiceCSVProcessor
from excel_utils import InvoiceExcelProcessor


def csv_process():
    resource_dir = Path(file_path).resolve().parent
    result_path = resource_dir / "result.csv"

    csv_processor = InvoiceCSVProcessor(file_path, result_path)
    api_processor = APIProcessor(csv_processor.corporations)
    csv_processor.write_result_csv(api_processor.fetch_data)
    print("処理が完了しました。")


def excel_process():
    excel_processor = InvoiceExcelProcessor(file_path)
    if not excel_processor.is_open_output_excel():
        api_processor = APIProcessor(excel_processor.target_corporations)
        excel_processor.write_result_excel(api_processor.fetch_data)
        print("処理が完了しました。")
    else:
        print("Excelファイルを閉じてから再度実行してください。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="インボイス登録番号を基に国税庁Web-APIで法人名と住所を取得する。")
    parser.add_argument("file_path", type=str,
                        help="登録番号が記載されたファイルのパス(csvまたはExcelファイル)"
                             "(CSVファイルの場合、同ディレクトリにresult.csvが出力されます。)")
    args = parser.parse_args()

    file_path = Path(args.file_path)
    if file_path.exists():
        if file_path.suffix == ".csv":
            csv_process()
        elif file_path.suffix in [".xlsx", ".xlsm"]:
            excel_process()
        else:
            print("csvまたはExcelファイルを指定してください。")
    else:
        print(f"{file_path}が見つかりませんでした。")
