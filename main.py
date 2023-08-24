from api_utils import APIProcessor
from csv_utils import InvoiceCSVProcessor
from excel_utils import InvoiceExcelProcessor


def csv_process():
    csv_processor = InvoiceCSVProcessor()
    if csv_processor.target_corporations:
        api_processor = APIProcessor(csv_processor.target_corporations)
        csv_processor.write_result_csv(api_processor.fetch_data)
        print("処理が完了しました。")
    else:
        print(f"{csv_processor.target_csv}が見つかりませんでした。")


def excel_process():
    excel_processor = InvoiceExcelProcessor()
    if not excel_processor.is_open_output_excel():
        if excel_processor.target_corporations:
            api_processor = APIProcessor(excel_processor.target_corporations)
            excel_processor.write_result_excel(api_processor.fetch_data)
            print("処理が完了しました。")
        else:
            print(f"{excel_processor.target_excel}が見つかりませんでした。")
    else:
        print("Excelファイルを閉じてから再度実行してください。")


if __name__ == "__main__":
    excel_process()
