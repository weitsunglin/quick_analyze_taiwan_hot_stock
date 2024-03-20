import requests
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import os

# 清空目錄中的所有文件
def clear_directory(directory):
    # 獲取目錄中的所有文件
    files = os.listdir(directory)
    # 遍歷每個文件，並刪除它們
    for file in files:
        os.remove(os.path.join(directory, file))


def fetch_stock_data(date, stock_no):
    url = f"http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=csv&date={date}&stockNo={stock_no}"
    response = requests.get(url)
    dates, prices = [], []
    if response.status_code == 200:
        lines = response.text.split('\n')
        for line in lines:
            if line.count('",') > 8:
                parts = line.split('","')
                if len(parts) >= 7:
                    date_str = parts[0].replace('"', '')
                    try:
                        year, month, day = map(int, date_str.split('/'))
                    except ValueError:
                        continue
                    gregorian_year = year + 1911
                    date = datetime(gregorian_year, month, day)
                    closing_price = float(parts[6].replace(',', ''))
                    dates.append(date)
                    prices.append(closing_price)
    return dates, prices

def get_previous_month(date, months=1):
    month = date.month - months - 1
    year = date.year + month // 12
    month = month % 12 + 1
    day = min(date.day, [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return datetime(year, month, day).strftime("%Y%m%d")

def plot_stock_data(dates, prices, stock_no, stock_name):
    plt.figure(figsize=(10, 6))
    
    count_red = 0
    count_green = 0

    # 繁中
    font_path = "C:\\Windows\\Fonts\\msjh.ttc"
    font_properties = FontProperties(fname=font_path, size=12)

    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:
            plt.plot([dates[i-1], dates[i]], [prices[i-1], prices[i]], 'r-o')
            count_red += 1
        else:
            plt.plot([dates[i-1], dates[i]], [prices[i-1], prices[i]], 'g-o')
            count_green += 1

    plt.title(f'股票代號{stock_no} {stock_name}收盤價', fontproperties=font_properties)
    plt.xlabel('日期', fontproperties=font_properties)
    plt.ylabel('收盤價', fontproperties=font_properties)
    plt.xticks(rotation=45)
    plt.text(dates[0], max(prices), f'漲價:{count_red}次。跌:{count_green}次', fontproperties=font_properties, color='black')
    plt.tight_layout()
    plt.savefig(f"C:\\Users\\User\\Desktop\\project\\tw_hot_stock_history\\hot\\{stock_no}_3month_history.png")


def get_top15_stock_numbers():
    url = 'https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL'
    response = requests.get(url)
    top15_stock_numbers = []
    top15_stock_names = []
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df['TradeValue'] = pd.to_numeric(df['TradeValue'], errors='coerce')
        top15 = df.sort_values(by='TradeValue', ascending=False).head(15)
        top15_stock_numbers = top15['Code'].head(15).tolist()
        top15_stock_names = top15['Name'].head(15).tolist()

    return top15_stock_numbers, top15_stock_names


if __name__ == "__main__":
    directory = "C:\\Users\\User\\Desktop\\project\\tw_hot_stock_history\\hot"
    clear_directory(directory)

    top15_stock_numbers, top15_stock_names = get_top15_stock_numbers()
    current_date = datetime.now()
    current_month_str = current_date.strftime("%Y%m01")
    previous_month_str = get_previous_month(current_date)
    two_months_ago_str = get_previous_month(current_date, 2)

    for stock_number, stock_name in zip(top15_stock_numbers, top15_stock_names):
        two_months_ago_dates, two_months_ago_prices = fetch_stock_data(two_months_ago_str, stock_number)
        prev_dates, prev_prices = fetch_stock_data(previous_month_str, stock_number)
        curr_dates, curr_prices = fetch_stock_data(current_month_str, stock_number)

        all_dates = two_months_ago_dates + prev_dates + curr_dates
        all_prices = two_months_ago_prices + prev_prices + curr_prices

        plot_stock_data(all_dates, all_prices, stock_number, stock_name)


    with open("C:\\Users\\User\\Desktop\\project\\tw_hot_stock_history\\README.md", "w", encoding="utf-8") as readme_file:
        readme_file.write("# 台灣熱門股票前15名\n\n")
        readme_file.write(f"![hot_15_tw_stock](https://github.com/weitsunglin/tw_hot_stock_history/blob/main/top15_stocks_trade_value.png)\n\n")
        readme_file.write("# 台灣熱門股票歷史走勢圖\n\n")
        readme_file.write("本存儲庫用於保存台灣熱門股票的歷史走勢圖。\n\n")
        readme_file.write("## 股票走勢圖\n\n")
        for stock_number in top15_stock_numbers:
            readme_file.write(f"### 股票代號：{stock_number}\n\n")
            readme_file.write(f"![{stock_number}_3month_history](https://github.com/weitsunglin/tw_hot_stock_history/blob/main/hot/{stock_number}_3month_history.png)\n\n")