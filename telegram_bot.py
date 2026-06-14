import requests
import datetime
import pandas as pd
from data_fetcher import get_ihsg_tickers, fetch_stock_data
from signals import calculate_technical_indicators, generate_signals
import time

# ==========================================
# PENGATURAN BOT TELEGRAM
# Masukkan Token dari @BotFather dan Chat ID Anda di sini
# ==========================================
TELEGRAM_BOT_TOKEN = "8973650359:AAG052i9szjbfRRi_W0NS-3ATlnLBDprlaI"
TELEGRAM_CHAT_ID = "843142600"

def send_telegram_message(message):
    """Mengirim pesan ke Telegram."""
    if TELEGRAM_BOT_TOKEN == "8973650359:AAG052i9szjbfRRi_W0NS-3ATlnLBDprlaI" or TELEGRAM_CHAT_ID == "843142600":
        print("Peringatan: Token Bot atau Chat ID belum diisi. Pesan tidak dikirim.")
        print(f"Pesan yang seharusnya dikirim:\n{message}")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Pesan berhasil dikirim ke Telegram!")
        else:
            print(f"Gagal mengirim pesan. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error mengirim pesan Telegram: {e}")

def run_screener_and_notify():
    """Menjalankan screener dan mengirim hasilnya via Telegram."""
    print("Memulai proses Screener Harian...")
    tickers_to_scan = get_ihsg_tickers()
    buy_candidates = []
    
    for i, ticker in enumerate(tickers_to_scan):
        print(f"Memindai {ticker}... ({i+1}/{len(tickers_to_scan)})")
        df_scan = fetch_stock_data(ticker, period="1mo")
        if not df_scan.empty:
            df_scan = calculate_technical_indicators(df_scan, sma_fast=20, sma_slow=50, rsi_len=14)
            df_scan = generate_signals(df_scan, sma_fast=20, sma_slow=50, rsi_len=14)
            
            # Cek hari terakhir apakah ada sinyal Beli
            recent_scan_signals = df_scan.tail(1)
            for date, row in recent_scan_signals.iterrows():
                if "Buy" in row['Signal']:
                    buy_candidates.append(f"✅ <b>{ticker.replace('.JK', '')}</b> (Rp {row['Close']:,.0f}) - {row['Signal']}")
        time.sleep(0.5) # Jeda sedikit agar tidak kena limit
        
    print("Pemindaian Selesai.")
    
    # Format pesan
    today = datetime.datetime.now().strftime("%d %b %Y")
    message = f"📊 <b>Laporan Sinyal Saham IHSG</b> ({today})\n\n"
    
    if buy_candidates:
        message += "Saham yang memunculkan sinyal <b>BELI</b> hari ini:\n"
        for cand in buy_candidates:
            message += f"{cand}\n"
        message += "\n<i>Buka aplikasi untuk melihat grafik dan probabilitas XGBoost!</i>"
    else:
        message += "Tidak ada sinyal Beli baru yang terdeteksi hari ini."
        
    send_telegram_message(message)

if __name__ == "__main__":
    run_screener_and_notify()
