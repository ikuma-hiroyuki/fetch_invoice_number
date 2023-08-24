from pathlib import Path

from api_utils import APIProcessor
from csv_utils import InvoiceCSVProcessor
from excel_utils import InvoiceExcelProcessor


def csv_process():
    resource_dir = Path(__file__).resolve().parent / "resource"
    target_path = resource_dir / "target_corporations.csv"
    result_path = resource_dir / "result.csv"

    csv_processor = InvoiceCSVProcessor(target_path, result_path)
    if csv_processor.corporations:
        api_processor = APIProcessor(csv_processor.corporations)
        csv_processor.write_result_csv(api_processor.fetch_data)
        print("処理が完了しました。")
    else:
        print(f"{csv_processor.target_path}が見つかりませんでした。")


def excel_process():
    resource_dir = Path(__file__).resolve().parent / "resource"
    excel_path = resource_dir / "sample_excel.xlsx"

    excel_processor = InvoiceExcelProcessor(excel_path)
    if excel_processor.target_corporations:
        if not excel_processor.is_open_output_excel():
            api_processor = APIProcessor(excel_processor.target_corporations)
            excel_processor.write_result_excel(api_processor.fetch_data)
            print("処理が完了しました。")
        else:
            print("Excelファイルを閉じてから再度実行してください。")
    else:
        print(f"{excel_processor.path}が見つかりませんでした。")


if __name__ == "__main__":
    excel_process()
