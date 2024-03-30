import requests
import pandas as pd

# 第一步：从台湾证券交易所API获取上市公司的信息
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

# 第二步：定义函数用于从另一个API获取EPS信息
def fetch_eps_info(stock_codes):
    url_eps_info = 'https://openapi.twse.com.tw/v1/opendata/t187ap14_L'
    eps_info = []

    for code in stock_codes:
        # 请注意，这里假设对每个股票代码单独请求，实际上应根据API文档调整
        response = requests.get(url_eps_info)  # 实际上可能需要添加参数以查询特定股票代码的EPS信息
        if response.status_code == 200:
            all_data = response.json()
            for item in all_data:
                if item['公司代號'] == code:
                    eps_info.append({
                        '公司代號': item['公司代號'],
                        '公司名稱': item['公司名稱'],
                        'EPS': item['基本每股盈餘(元)']
                    })
                    break  # 找到匹配项后中断循环
        else:
            print(f"Failed to fetch EPS info for stock code {code}")
    return eps_info

# 第三步：使用股票代码列表获取EPS信息并打印结果
eps_info = fetch_eps_info(top15_codes)
eps_df = pd.DataFrame(eps_info)
print(eps_df)
