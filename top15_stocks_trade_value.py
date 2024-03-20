import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

url = 'https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL'

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)
    df['TradeValue'] = pd.to_numeric(df['TradeValue'], errors='coerce')
    top10 = df.sort_values(by='TradeValue', ascending=False).head(15)

    # 繁中
    font_path = "C:\\Windows\\Fonts\\msjh.ttc"
    font_properties = FontProperties(fname=font_path, size=12)
    plt.rcParams['axes.unicode_minus'] = False 

    plt.style.use('ggplot')
    ax = top10.plot(kind='bar', x='Name', y='TradeValue', legend=None)
    ax.set_title('台灣上市公司成交金額前15名', fontproperties=font_properties)
    ax.set_xlabel('公司名稱', fontproperties=font_properties)
    ax.set_ylabel('成交金額', fontproperties=font_properties)
    ax.set_xticklabels(top10['Name'], fontproperties=font_properties, rotation=45, ha="right")
    
    plt.tight_layout()

    save_path = 'C:\\Users\\User\\Desktop\\project\\tw_hot_stock_history\\top15_stocks_trade_value.png'
    plt.savefig(save_path)