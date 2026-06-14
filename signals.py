import pandas as pd
import pandas_ta as ta
import numpy as np
from sklearn.ensemble import RandomForestClassifier
try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None

def calculate_technical_indicators(df, sma_fast=20, sma_slow=50, rsi_len=14):
    """Menghitung indikator teknikal dasar"""
    if df.empty or len(df) < 50:
        return df
        
    # Moving Averages (Trend)
    df[f'SMA_{sma_fast}'] = ta.sma(df['Close'], length=sma_fast)
    df[f'SMA_{sma_slow}'] = ta.sma(df['Close'], length=sma_slow)
    
    # Relative Strength Index (Momentum)
    df[f'RSI_{rsi_len}'] = ta.rsi(df['Close'], length=rsi_len)
    
    # MACD
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    if macd is not None:
        df = pd.concat([df, macd], axis=1)
        
    # Bollinger Bands
    bbands = ta.bbands(df['Close'], length=sma_fast, std=2)
    if bbands is not None:
        df = pd.concat([df, bbands], axis=1)
        
    # Stochastic Oscillator
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    if stoch is not None:
        df = pd.concat([df, stoch], axis=1)
        
    return df

def generate_signals(df, sma_fast=20, sma_slow=50, rsi_len=14):
    """Menghasilkan sinyal Buy/Sell/Hold berdasarkan indikator"""
    sma_fast_col = f'SMA_{sma_fast}'
    sma_slow_col = f'SMA_{sma_slow}'
    rsi_col = f'RSI_{rsi_len}'
    
    if sma_fast_col not in df.columns or df.empty:
        df['Signal'] = 'Hold'
        return df
        
    signals = []
    for i in range(len(df)):
        sig = 'Hold'
        
        # Skip beberapa baris pertama karena butuh data sebelumnya
        if i > 0:
            # 1. Golden Cross / Death Cross
            if df[sma_fast_col].iloc[i] > df[sma_slow_col].iloc[i] and df[sma_fast_col].iloc[i-1] <= df[sma_slow_col].iloc[i-1]:
                sig = 'Buy (Golden X)'
            elif df[sma_fast_col].iloc[i] < df[sma_slow_col].iloc[i] and df[sma_fast_col].iloc[i-1] >= df[sma_slow_col].iloc[i-1]:
                sig = 'Sell (Death X)'
            # 2. Kondisi Ekstrem RSI (Oversold/Overbought)
            elif df[rsi_col].iloc[i] < 30:
                sig = 'Buy (RSI OS)'
            elif df[rsi_col].iloc[i] > 70:
                sig = 'Sell (RSI OB)'
                
        signals.append(sig)
        
    df['Signal'] = signals
    return df

def train_and_predict_ml(df, macro_df=None, sma_fast=20, sma_slow=50, rsi_len=14):
    """
    Prediksi pergerakan arah besok menggunakan XGBoost / Random Forest.
    """
    if df.empty or len(df) < 100:
        return "Data tidak cukup", 0.0
        
    ml_df = df.copy()
    
    # Gabungkan dengan data makro (USD/IDR) jika ada
    if macro_df is not None and not macro_df.empty:
        # Paskan index waktu (tanggal)
        ml_df = ml_df.join(macro_df, how='left')
        ml_df['USD_IDR'] = ml_df['USD_IDR'].ffill() # Isi nilai yang kosong dengan hari sebelumnya
        
    # Target: 1 jika harga besok lebih tinggi dari hari ini (Naik), 0 jika turun/tetap
    ml_df['Target'] = np.where(ml_df['Close'].shift(-1) > ml_df['Close'], 1, 0)
    
    # Hapus baris dengan NaN
    ml_df = ml_df.dropna()
    
    if len(ml_df) < 50:
         return "Data bersih tidak cukup", 0.0
         
    # Pisahkan data hari terakhir untuk diprediksi
    predict_data = ml_df.iloc[-1:]
    train_data = ml_df.iloc[:-1]
    
    # Pilih Fitur
    features = ['Open', 'High', 'Low', 'Close', 'Volume', f'SMA_{sma_fast}', f'SMA_{sma_slow}', f'RSI_{rsi_len}']
    if 'MACD_12_26_9' in ml_df.columns:
        features.extend(['MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9'])
    if f'BBL_{sma_fast}_2.0' in ml_df.columns:
        features.extend([f'BBL_{sma_fast}_2.0', f'BBM_{sma_fast}_2.0', f'BBU_{sma_fast}_2.0'])
    if 'USD_IDR' in ml_df.columns:
        features.append('USD_IDR')
        
    X_train = train_data[features]
    y_train = train_data['Target']
    
    if len(X_train) < 10:
        return "Data training terlalu sedikit", 0.0
        
    # Inisialisasi dan latih model
    if XGBClassifier is not None:
        model = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42, use_label_encoder=False, eval_metric='logloss')
    else:
        model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
        
    model.fit(X_train, y_train)
    
    # Lakukan prediksi untuk hari ini (memprediksi besok)
    X_predict = predict_data[features]
    prediction = model.predict(X_predict)[0]
    probability = model.predict_proba(X_predict)[0]
    
    if prediction == 1:
        return "Naik 📈", probability[1] * 100
    else:
        return "Turun 📉", probability[0] * 100

def run_backtest(df, initial_capital=10000000):
    """
    Mensimulasikan hasil trading berdasarkan sinyal teknikal (Sederhana).
    Beli semua modal saat sinyal Buy, Jual semua saat sinyal Sell.
    """
    if 'Signal' not in df.columns or df.empty:
        return None
        
    capital = initial_capital
    position = 0 # Jumlah lembar saham yang dimiliki
    buy_price = 0
    
    equity_curve = []
    trades = []
    
    for date, row in df.iterrows():
        current_price = row['Close']
        signal = row['Signal']
        
        # Eksekusi Sinyal
        if 'Buy' in signal and position == 0:
            # Beli
            position = capital / current_price
            buy_price = current_price
            capital = 0
            trades.append({"Date": date, "Type": "Buy", "Price": current_price, "Signal": signal})
            
        elif 'Sell' in signal and position > 0:
            # Jual
            capital = position * current_price
            position = 0
            profit = (current_price - buy_price) / buy_price * 100
            trades.append({"Date": date, "Type": "Sell", "Price": current_price, "Profit %": profit, "Signal": signal})
            
        # Catat total aset harian
        current_value = capital + (position * current_price)
        equity_curve.append(current_value)
        
    # Hitung nilai aset terakhir
    final_value = equity_curve[-1] if equity_curve else initial_capital
    return_pct = ((final_value - initial_capital) / initial_capital) * 100
    
    return {
        "Initial Capital": initial_capital,
        "Final Capital": final_value,
        "Total Return %": return_pct,
        "Equity Curve": equity_curve,
        "Dates": df.index,
        "Trades": pd.DataFrame(trades)
    }
