import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 獲取股票成交信息
url_stock_day_all = 'https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL'
response = requests.get(url_stock_day_all)

if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)
    df['TradeValue'] = pd.to_numeric(df['TradeValue'], errors='coerce')
    df['ClosingPrice'] = pd.to_numeric(df['ClosingPrice'], errors='coerce')  # 新增：轉換收盤價為數值型
    top15 = df.sort_values(by='TradeValue', ascending=False).head(15)
    top15_codes = top15['Code'].tolist()
else:
    print("獲取股票資料失敗")
    top15_codes = []

# 獲取EPS信息
def fetch_eps_info(stock_codes):
    url_eps_info = 'https://openapi.twse.com.tw/v1/opendata/t187ap14_L'
    eps_info = []

    response = requests.get(url_eps_info)
    if response.status_code == 200:
        all_data = response.json()
        for code in stock_codes:
            for item in all_data:
                if item['公司代號'] == code:
                    eps_info.append({
                        '公司代號': item['公司代號'],
                        '公司名稱': item['公司名稱'],
                        'EPS': item['基本每股盈餘(元)']
                    })
                    break
    else:
        print("獲取EPS資訊失敗")
    return eps_info

eps_info = fetch_eps_info(top15_codes)
eps_dict = {info['公司代號']: info['EPS'] for info in eps_info}

font_path = "C:\\Windows\\Fonts\\msjh.ttc"
font_properties = FontProperties(fname=font_path, size=8)
plt.rcParams['axes.unicode_minus'] = False

plt.style.use('ggplot')
fig, ax = plt.subplots(figsize=(12, 8))
top15.plot(kind='bar', x='Name', y='TradeValue', legend=None, ax=ax)

ax.set_title('台灣上市公司成交金額前15名及其EPS和收盤價', fontproperties=font_properties)
ax.set_xlabel('公司名稱', fontproperties=font_properties)
ax.set_ylabel('成交金額', fontproperties=font_properties)
ax.set_xticklabels(top15['Name'], fontproperties=font_properties, rotation=45, ha="right")

# 在條形上添加EPS和收盤價標籤
for i, code in enumerate(top15['Code']):
    eps = eps_dict.get(code, 'N/A')
    closing_price = top15.iloc[i]['ClosingPrice']  # 直接使用已經轉換的收盤價數據
    text_position = top15.iloc[i]['TradeValue'] * 1.01  # 稍微提高文字位置，避免與條形重疊
    ax.text(i, text_position, f'EPS: {eps}\n收盤價: {closing_price}', ha='center', va='bottom', fontproperties=font_properties)

plt.tight_layout()

save_path = 'C:\\Users\\User\\Desktop\\project\\quick_analyze_taiwan_hot_stock\\top15_stocks_trade_value.png'
plt.savefig(save_path)
