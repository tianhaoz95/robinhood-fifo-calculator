import flet as ft
import pandas as pd
import collections
from typing import Callable
import datetime


def calculate_mature_shares(path: str, id: str, logger: Callable[[str], None]) -> float:
    report = pd.read_csv(path, skipfooter=1, parse_dates=True, engine='python')
    logger(f"Read in report with {len(report)=}")
    report = report.drop(columns=['Activity Date', 'Process Date', 'Description'])
    report = report.loc[report['Instrument'] == id]
    logger(f"Transaction code values: {report['Trans Code'].unique()}")
    report = report.loc[report['Trans Code'].isin(["Buy", "Sell"])]
    logger(f"Remove everything except Buy/Sell. Remaining {len(report)=}")
    report['Settle Date'] = pd.to_datetime(report['Settle Date'])
    report = report.sort_values(by='Settle Date')
    logger(report.head())
    fifo = collections.deque()
    logger("========================================")
    logger("Start calculating mature stocks...")
    logger("========================================")
    
    class Record:
        def __init__(self, date: datetime.datetime, quantity: float) -> None:
            self.date = date
            self.quantity = quantity


    for idx, record in report.iterrows():
        date, stock_id, code, quantity, price, amount = record
        if code == "Buy":
            fifo.append(Record(date.to_pydatetime(), float(quantity)))
        if code == "Sell":
            sell_quantity = float(quantity)
            while sell_quantity > 0:
                if len(fifo) > 0:
                    earliest_buy = fifo.popleft()
                    earliest_buy.quantity -= sell_quantity
                    if earliest_buy.quantity > 0:
                        fifo.appendleft(earliest_buy)
                    else:
                        sell_quantity = abs(earliest_buy.quantity)
                else:
                    logger(f"Error: not enough stock to sell. Lack {sell_quantity=}. Skip")
                    sell_quantity = 0
    logger(f"Remaining transaction count {len(fifo)=}")

    mature_quantity = 0
    one_year = datetime.timedelta(days=365)
    current_date = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    while len(fifo) > 0:
        earliest_buy = fifo.popleft()
        holding_time = current_date - earliest_buy.date
        conclusion = f"Less than {one_year}"
        if holding_time > one_year:
            conclusion = f"More than {one_year}. Count as mature."
            mature_quantity += earliest_buy.quantity
        logger(f"Compare {current_date=} and {earliest_buy.date=}, {holding_time=}, {conclusion=}")

    logger("==============")
    logger("Final Result")
    logger("==============")
    logger(f"Mature shares {mature_quantity=}")
    return mature_quantity


def main(page: ft.Page):
    intro_text = '''
    Hi! Thanks for using Robinhood FIFO utility tool!

    This tool has 1 simple function: given a list of stock transactions, calculate how many stocks are over 1 year old which is considered long term investment.

    Here are the steps to use this tool.

    1. Go into Robinhood app > Settings > Reports and statements > Reports.

    2. Use the button "Generate new report" to generate transactions in the
    time frame of interest.

    3. Download the report once ready.

    4. Put the stock name in the text field below.

    5. Use the button to upload the CSV report.

    6. Scroll all the way down to see the result.
    '''
    
    page.add(ft.SafeArea(ft.Text(intro_text)))

    stock_name_input = ft.TextField(label="Stock name (e.g., VOO)")
    page.add(stock_name_input)

    def on_dialog_result(e: ft.FilePickerResultEvent):
        print("Selected file:", e.files[0])
        print("Selected file or directory:", e.path)
        path = e.files[0].path
        def screen_print(log: str):
            page.add(ft.SafeArea(ft.Text(log)))
        _ = calculate_mature_shares(path, stock_name_input.value, screen_print)

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)
    
    page.add(
        ft.ElevatedButton(
            "Upload CSV report generated in Robinhood app",
            on_click=lambda _: file_picker.pick_files(allow_multiple=False),
        )
    )
    page.scroll = "always"
    page.update()


ft.app(main)
