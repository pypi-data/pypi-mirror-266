import pandas as pd
import numpy as np
import yfinance as yf
def getStock(symbol):
    return yf.download(symbol, progress=False)

def energy(Clean=True):
    url = 'https://drive.google.com/file/d/1EpczybaLAzV053G8pG-kB38IXT7NC580/view?usp=sharing'
    data_path = 'https://drive.google.com/uc?export=download&id=' + url.split('/')[-2]
    df = pd.read_csv(data_path,index_col=0)
    if Clean==True:
        df.index=pd.to_datetime(df.index)
        df=df.dropna(subset=["AEP"]).dropna(axis=1).sort_index()
    return df

def titanic():
    titanic = pd.read_csv("https://dlsun.github.io/pods/data/titanic.csv")
    return titanic


def weather():
    url = "https://drive.google.com/uc?export=download&id=18rpxu7b3LQt81aPLYYleI16_C3RiKB_6"
    weather = pd.read_csv(url,index_col=0)
    weather.index=pd.to_datetime(weather.index)
    return weather

def publicCompany():
    url="https://drive.google.com/uc?export=download&id=1gCCH0lMJFvBGf6YQCtYnGMrYKw2IMbhy"
    company=pd.read_csv(url,index_col=0)
    return company

def sp500():
    url = 'https://drive.google.com/file/d/1ERGkh-O_Zd34u4kJvcMfCakY8wKmZMcd/view?usp=sharing'
    sp500 = 'https://drive.google.com/uc?export=download&id=' + url.split('/')[-2]
    sp500 = pd.read_csv(sp500, index_col=0)
    sp500.index=pd.to_datetime(sp500.index)
    return sp500.sort_index()

def appl():
    url = 'https://drive.google.com/file/d/1EPrnGQorOi-JY0qUfz9kVV6-hl6xH_hn/view?usp=sharing'
    AAPL = 'https://drive.google.com/uc?export=download&id=' + url.split('/')[-2]
    apple = pd.read_csv(AAPL, index_col=0)
    apple.index = pd.to_datetime(apple.index)
    return apple.sort_index()

def returnsp500_tesla():
    url = 'https://drive.google.com/file/d/1naXM02nfjESx3ABD-8RQ_E03TXLco9Je/view?usp=sharing'
    returnpath = 'https://drive.google.com/uc?export=download&id=' + url.split('/')[-2]
    returns = pd.read_csv(returnpath, index_col=0)
    returns.index=pd.to_datetime(returns.index)
    return returns.sort_index()

def profit():
    url = 'https://drive.google.com/file/d/1pZ7xqTp_1hRXKl8sjpRuy7zvJLkyUz21/view?usp=share_link'
    profitpath = 'https://drive.google.com/uc?export=download&id=' + url.split('/')[-2]

    df = pd.read_csv(profitpath)  # Store the data to a variable called 'df'
    return df
