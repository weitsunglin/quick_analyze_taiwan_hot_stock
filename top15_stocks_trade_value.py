import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 获取股票成交信息
url_stock_day_all = 'https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL'
response = requests.get(url_stock_day_all)

if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)
    df['TradeValue'] = pd.to_numeric(df['TradeValue'], errors='coerce')
    top15 = df.sort_values(by='TradeValue', ascending=False).head(15)
    top15_codes = top15['Code'].tolist()
else:
    print("Failed to fetch stock data")
    top15_codes = []

# 获取EPS信息
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
                    break  # 找到匹配项后中断循环
    else:
        print("Failed to fetch EPS info")
    return eps_info

eps_info = fetch_eps_info(top15_codes)

# 将EPS信息转换为字典方便查找
eps_dict = {info['公司代號']: info['EPS'] for info in eps_info}

# 绘制成交金额长条图，并在每个条形上标注EPS
font_path = "C:\\Windows\\Fonts\\msjh.ttc"
font_properties = FontProperties(fname=font_path, size=10)
plt.rcParams['axes.unicode_minus'] = False

plt.style.use('ggplot')
fig, ax = plt.subplots(figsize=(12, 8))
top15.plot(kind='bar', x='Name', y='TradeValue', legend=None, ax=ax)

ax.set_title('台灣上市公司成交金額前15名及其EPS', fontproperties=font_properties)
ax.set_xlabel('公司名稱', fontproperties=font_properties)
ax.set_ylabel('成交金額', fontproperties=font_properties)
ax.set_xticklabels(top15['Name'], fontproperties=font_properties, rotation=45, ha="right")

# 在条形上添加EPS标签
for i, code in enumerate(top15['Code']):
    eps = eps_dict.get(code, 'N/A')
    ax.text(i, top15.iloc[i]['TradeValue'], f'EPS: {eps}', ha='center', va='bottom', fontproperties=font_properties)

plt.tight_layout()

save_path = 'C:\\Users\\User\\Desktop\\project\\quick_analyze_taiwan_hot_stock\\top15_stocks_trade_value.png'
plt.savefig(save_path)
plt.show()
