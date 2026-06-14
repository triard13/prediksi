import yfinance as yf
import pandas as pd
import streamlit as st

# Daftar sampel saham IHSG (populer/likuid)
# Untuk versi lebih lanjut, daftar ini bisa dimuat dari CSV yang berisi ~800+ emiten IHSG
IHSG_TICKERS = [
    "BBCA", "BBRI", "BMRI", "BBNI", "ASII", "TLKM", "GOTO", "AMMN", 
    "BRPT", "TPIA", "UNVR", "ICBP", "INDF", "CPIN", "KLBF", "PGAS", 
    "ADRO", "ITMG", "PTBA", "UNTR", "MDKA", "ANTM", "INCO", "TINS",
    "AKRA", "MEDC", "BRIS", "ARTO", "BUKA", "SRTG", "MNCN", "SCMA",
    "EXCL", "ISAT", "TOWR", "TBIG", "MIKA", "HEAL", "SILO", "SIDO",
    "MYOR", "GGRM", "HMSP", "SMGR", "INTP", "WIKA", "PTPP", "ADHI", "WSKT"
]

def get_ihsg_tickers():
    """Mengembalikan daftar ticker dengan akhiran .JK untuk Yahoo Finance"""
    return [t + ".JK" for t in IHSG_TICKERS]

def fetch_stock_data(ticker, period="1y"):
    """
    Mengambil data saham historis dari Yahoo Finance.
    Parameter period bisa berupa '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'
    """
    try:
        # Tambahkan .JK jika belum ada dan bukan indeks
        if not ticker.endswith(".JK") and not ticker.startswith("^"):
            ticker += ".JK"
            
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        # Bersihkan data jika ada timezone
        if not df.empty:
            if df.index.tz is not None:
                df.index = df.index.tz_convert(None)
                
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_fundamental_data(ticker):
    """
    Mengambil data fundamental dasar dari Yahoo Finance (di-cache agar cepat)
    """
    try:
        if not ticker.endswith(".JK") and not ticker.startswith("^"):
            ticker += ".JK"
        info = yf.Ticker(ticker).info
        
        return {
            "Market Cap": info.get("marketCap", "-"),
            "PE Ratio": info.get("trailingPE", "-"),
            "PBV": info.get("priceToBook", "-"),
            "Dividend Yield": info.get("dividendYield", "-")
        }
    except:
        return {"Market Cap": "-", "PE Ratio": "-", "PBV": "-", "Dividend Yield": "-"}

@st.cache_data(ttl=86400)
def fetch_macro_data(period="1y"):
    """
    Mengambil data makro ekonomi (Kurs USD/IDR)
    """
    try:
        macro = yf.Ticker("IDR=X")
        df = macro.history(period=period)
        if not df.empty and df.index.tz is not None:
            df.index = df.index.tz_convert(None)
        return df[['Close']].rename(columns={'Close': 'USD_IDR'})
    except:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_news_sentiment(ticker):
    """
    Mengambil berita terbaru dari Yahoo Finance dan melakukan analisis sentimen.
    """
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        
        if not ticker.endswith(".JK") and not ticker.startswith("^"):
            ticker += ".JK"
            
        stock = yf.Ticker(ticker)
        news_list = stock.news
        
        if not news_list:
            return {"score": 0, "label": "Netral", "news_count": 0}
            
        total_score = 0
        valid_news = 0
        
        for article in news_list[:5]: # Ambil 5 berita terbaru
            title = article.get('title', '')
            if title:
                score = analyzer.polarity_scores(title)['compound']
                total_score += score
                valid_news += 1
                
        if valid_news == 0:
             return {"score": 0, "label": "Netral", "news_count": 0}
             
        avg_score = total_score / valid_news
        
        # Tentukan label
        if avg_score > 0.05:
            label = "Positif 🟢"
        elif avg_score < -0.05:
            label = "Negatif 🔴"
        else:
            label = "Netral ⚪"
            
        return {"score": avg_score, "label": label, "news_count": valid_news}
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return {"score": 0, "label": "Netral", "news_count": 0}


