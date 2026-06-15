import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
from data_fetcher import get_ihsg_tickers, fetch_stock_data, fetch_fundamental_data, fetch_macro_data, fetch_news_sentiment
from signals import calculate_technical_indicators, generate_signals, train_and_predict_ml, run_backtest
from portfolio_manager import load_portfolio, add_to_portfolio, remove_from_portfolio

# Setup halaman
st.set_page_config(page_title="Sistem Analitik Saham IHSG Pro", layout="wide")

# Sistem Otentikasi (Password)
APP_PASSWORD = os.environ.get("APP_PASSWORD", "123456") # Default 123456 jika belum diatur di .env / Secrets

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Aplikasi Terkunci")
    password_input = st.text_input("Masukkan PIN / Password:", type="password")
    if st.button("Masuk"):
        if password_input == APP_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Password salah!")
    st.stop() # Mencegah kode di bawahnya berjalan jika belum login

# CSS Kustom untuk memperbaiki teks metrik dan membuat tata letak responsif (mobile-friendly)
st.markdown("""
<style>
[data-testid="stMetricValue"] > div {
    white-space: normal !important;
    word-break: break-word;
    font-size: 1.6rem !important; 
    line-height: 1.2;
}

/* --- Pengaturan Responsif untuk HP / Layar Kecil --- */
@media (max-width: 768px) {
    /* Paksa semua kolom berdampingan menjadi tersusun ke bawah (vertikal) */
    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
        margin-bottom: 1rem;
    }
    
    /* Sesuaikan sedikit ukuran huruf metrik agar tidak terlalu besar di HP */
    [data-testid="stMetricValue"] > div {
        font-size: 1.3rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

st.title("📈 Sistem Analitik Saham IHSG Pro")
st.markdown("Prototipe tahap 3: Screener, Backtesting Dinamis, Sentimen Berita, dan Portofolio.")

# Ambil data makro sekali saja untuk efisiensi
macro_df = fetch_macro_data()

# Pengaturan Dinamis di Sidebar
st.sidebar.header("⚙️ Parameter Indikator (Dinamis)")
sma_fast_input = st.sidebar.slider("SMA Cepat", min_value=5, max_value=50, value=20, step=1)
sma_slow_input = st.sidebar.slider("SMA Lambat", min_value=20, max_value=200, value=50, step=1)
rsi_len_input = st.sidebar.slider("RSI Length", min_value=5, max_value=30, value=14, step=1)

# Struktur Tab
tab1, tab2, tab3, tab4 = st.tabs(["📊 Analisis Individu", "🔎 Screener Pasar", "⏱️ Backtesting", "💼 Portofolio"])

# ================= TAB 1: ANALISIS INDIVIDU =================
with tab1:
    st.header("Pengaturan Analisis Individu")
    tickers = get_ihsg_tickers()
    
    col_t1, col_t2 = st.columns(2)
    selected_ticker = col_t1.selectbox("Pilih Saham (Populer):", tickers, index=0)
    selected_ticker_input = col_t2.text_input("Atau Ketik Ticker Manual (Opsional):")

    if selected_ticker_input:
        selected_ticker = selected_ticker_input.upper()
        if not selected_ticker.endswith(".JK") and not selected_ticker.startswith("^"):
            selected_ticker += ".JK"

    period = st.selectbox("Pilih Rentang Waktu Historis:", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

    st.write(f"### Menganalisis **{selected_ticker}** (Rentang: {period})")

    # Ambil Data Fundamental & Sentimen Berita
    fundamental = fetch_fundamental_data(selected_ticker)
    news_sentiment = fetch_news_sentiment(selected_ticker)
    
    # Ambil Data Historis
    with st.spinner('Mengambil data historis...'):
        df = fetch_stock_data(selected_ticker, period)

    if df.empty:
        st.error(f"Gagal mengambil data untuk {selected_ticker}.")
    else:
        df = calculate_technical_indicators(df, sma_fast=sma_fast_input, sma_slow=sma_slow_input, rsi_len=rsi_len_input)
        df = generate_signals(df, sma_fast=sma_fast_input, sma_slow=sma_slow_input, rsi_len=rsi_len_input)
        ml_pred_label, ml_pred_prob = train_and_predict_ml(df, macro_df, sma_fast=sma_fast_input, sma_slow=sma_slow_input, rsi_len=rsi_len_input)

        st.markdown("#### 🏢 Data Fundamental & Berita")
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
        col_f1.metric("Market Cap", f"{fundamental.get('Market Cap', '-'):,}" if isinstance(fundamental.get('Market Cap'), (int, float)) else fundamental.get('Market Cap'))
        col_f2.metric("PE Ratio", fundamental.get('PE Ratio', '-'))
        col_f3.metric("PBV", fundamental.get('PBV', '-'))
        col_f4.metric("Dividend Yield", f"{fundamental.get('Dividend Yield', 0)*100:.2f}%" if isinstance(fundamental.get('Dividend Yield'), (int, float)) else "-")
        col_f5.metric("Sentimen Berita", news_sentiment['label'], f"Dari {news_sentiment['news_count']} berita")

        st.markdown("---")
        st.markdown("#### 📈 Data Teknikal Terkini")
        col1, col2, col3, col4 = st.columns(4)
        last_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2] if len(df) > 1 else last_close
        change_pct = ((last_close - prev_close) / prev_close) * 100
        
        col1.metric("Harga Terakhir", f"Rp {last_close:,.0f}", f"{change_pct:.2f}%")
        
        recent_signals = df[df['Signal'] != 'Hold']
        last_active_signal = recent_signals['Signal'].iloc[-1] if not recent_signals.empty else "Belum Ada"
        last_active_date = recent_signals.index[-1].strftime('%Y-%m-%d') if not recent_signals.empty else "-"
        
        if "Buy" in last_active_signal:
            col2.metric("Sinyal Terakhir", last_active_signal, f"Pada: {last_active_date}")
        elif "Sell" in last_active_signal:
            col2.metric("Sinyal Terakhir", last_active_signal, f"Pada: {last_active_date}", delta_color="inverse")
        else:
            col2.metric("Sinyal Terakhir", last_active_signal)

        if "Naik" in ml_pred_label:
            col3.metric("Prediksi ML (Besok)", ml_pred_label, f"Prob: {ml_pred_prob:.1f}%")
        else:
            col3.metric("Prediksi ML (Besok)", ml_pred_label, f"Prob: {ml_pred_prob:.1f}%", delta_color="inverse")
            
        rsi_col_name = f'RSI_{rsi_len_input}'
        last_rsi = df[rsi_col_name].iloc[-1] if rsi_col_name in df.columns else 0
        col4.metric(f"RSI ({rsi_len_input})", f"{last_rsi:.1f}")

        st.subheader("Grafik Harga & Indikator")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Harga'))
        
        sma_fast_col = f'SMA_{sma_fast_input}'
        sma_slow_col = f'SMA_{sma_slow_input}'
        if sma_fast_col in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df[sma_fast_col], line=dict(color='blue', width=1), name=f'SMA {sma_fast_input}'))
        if sma_slow_col in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df[sma_slow_col], line=dict(color='orange', width=1), name=f'SMA {sma_slow_input}'))
        
        bbu_col = f'BBU_{sma_fast_input}_2.0'
        bbl_col = f'BBL_{sma_fast_input}_2.0'
        if bbu_col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[bbu_col], line=dict(color='rgba(128,128,128,0.5)', width=1, dash='dash'), name='BB Upper'))
            fig.add_trace(go.Scatter(x=df.index, y=df[bbl_col], line=dict(color='rgba(128,128,128,0.5)', width=1, dash='dash'), name='BB Lower', fill='tonexty'))

        buy_signals = df[df['Signal'].str.contains('Buy')]
        sell_signals = df[df['Signal'].str.contains('Sell')]
        fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers', marker=dict(symbol='triangle-up', color='green', size=12), name='Sinyal Beli'))
        fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'], mode='markers', marker=dict(symbol='triangle-down', color='red', size=12), name='Sinyal Jual'))

        fig.update_layout(title=f'Grafik {selected_ticker}', yaxis_title='Harga (IDR)', xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, width='stretch')

# ================= TAB 2: SCREENER =================
with tab2:
    st.write("### 🔎 Screener Pasar Aktif (Berdasarkan Parameter Dinamis)")
    st.write("Memindai 50 saham populer untuk menemukan sinyal beli terbaru (hari ini atau kemarin).")
    
    if st.button("Jalankan Screener (Proses 50 Saham)"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        buy_candidates = []
        tickers_to_scan = get_ihsg_tickers()
        
        for i, ticker in enumerate(tickers_to_scan):
            status_text.text(f"Memindai {ticker}... ({i+1}/{len(tickers_to_scan)})")
            df_scan = fetch_stock_data(ticker, period="3mo") # Pendek saja agar cepat
            if not df_scan.empty:
                df_scan = calculate_technical_indicators(df_scan, sma_fast=sma_fast_input, sma_slow=sma_slow_input, rsi_len=rsi_len_input)
                df_scan = generate_signals(df_scan, sma_fast=sma_fast_input, sma_slow=sma_slow_input, rsi_len=rsi_len_input)
                
                recent_scan_signals = df_scan.tail(2)
                for date, row in recent_scan_signals.iterrows():
                    if "Buy" in row['Signal']:
                        rsi_col = f'RSI_{rsi_len_input}'
                        buy_candidates.append({
                            "Ticker": ticker.replace(".JK", ""),
                            "Date": date.strftime('%Y-%m-%d'),
                            "Close Price": row['Close'],
                            "Signal Type": row['Signal'],
                            "RSI": round(row[rsi_col], 2) if rsi_col in row else None
                        })
                        break
            
            progress_bar.progress((i + 1) / len(tickers_to_scan))
            
        status_text.text("Pemindaian Selesai!")
        
        if buy_candidates:
            st.success(f"Ditemukan {len(buy_candidates)} saham dengan sinyal Beli potensial berdasarkan parameter saat ini!")
            st.dataframe(pd.DataFrame(buy_candidates))
            
            if st.button("Kirim Hasil ke Telegram 🚀"):
                from telegram_bot import send_telegram_message
                import datetime
                
                today = datetime.datetime.now().strftime("%d %b %Y")
                message = f"📊 <b>Sinyal Saham IHSG via Web App</b> ({today})\n\n"
                message += "Daftar saham yang disaring saat ini:\n"
                
                for cand in buy_candidates:
                    message += f"✅ <b>{cand['Ticker']}</b> (Rp {cand['Close Price']:,.0f}) - {cand['Signal Type']}\n"
                
                message += f"\n<i>Parameter: SMA Cepat={sma_fast_input}, Lambat={sma_slow_input}, RSI={rsi_len_input}</i>"
                
                try:
                    send_telegram_message(message)
                    st.success("Pesan terkirim ke Telegram Anda!")
                except Exception as e:
                    st.error(f"Gagal mengirim pesan: {e}")
                    
        else:
            st.info("Tidak ada sinyal Beli pada saham yang dipindai saat ini.")

# ================= TAB 3: BACKTESTING =================
with tab3:
    st.write("### ⏱️ Simulasi Backtesting")
    st.write(f"Melihat performa historis jika Anda mengikuti sinyal teknikal pada saham **{selected_ticker if 'selected_ticker' in locals() else 'pilihan Anda'}**.")
    st.write(f"*(Menggunakan parameter dinamis: SMA Cepat={sma_fast_input}, SMA Lambat={sma_slow_input})*")
    
    if 'df' in locals() and not df.empty:
        backtest_result = run_backtest(df, initial_capital=10000000)
        
        if backtest_result and len(backtest_result["Equity Curve"]) > 0:
            c1, c2, c3 = st.columns(3)
            c1.metric("Modal Awal", f"Rp {backtest_result['Initial Capital']:,.0f}")
            c2.metric("Nilai Akhir", f"Rp {backtest_result['Final Capital']:,.0f}", f"{backtest_result['Total Return %']:.2f}%")
            
            trades_df = backtest_result["Trades"]
            total_trades = len(trades_df) if not trades_df.empty else 0
            
            c3.metric("Jumlah Transaksi", total_trades)
            
            st.subheader("Kurva Pertumbuhan Modal (Equity Curve)")
            fig_eq = go.Figure()
            fig_eq.add_trace(go.Scatter(x=backtest_result["Dates"], y=backtest_result["Equity Curve"], mode='lines', name='Nilai Portofolio', line=dict(color='green', width=2)))
            fig_eq.update_layout(yaxis_title='Nilai (IDR)', height=400)
            st.plotly_chart(fig_eq, width='stretch')
            
            if not trades_df.empty:
                with st.expander("Lihat Riwayat Transaksi Detail"):
                    st.dataframe(trades_df)
        else:
            st.info("Data tidak cukup untuk melakukan backtest atau tidak ada sinyal Buy/Sell yang dieksekusi dengan parameter saat ini.")
    else:
        st.warning("Silakan kembali ke tab Analisis Individu dan pilih saham terlebih dahulu.")

# ================= TAB 4: PORTOFOLIO =================
with tab4:
    st.write("### 💼 Manajemen Portofolio Anda")
    st.write("Pantau performa saham yang Anda miliki saat ini.")
    
    portfolio = load_portfolio()
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        add_ticker = st.text_input("Ticker Saham (misal BBCA):").upper()
    with col_p2:
        add_shares = st.number_input("Jumlah Lembar:", min_value=1, step=100)
    with col_p3:
        add_price = st.number_input("Harga Beli Rata-rata (Rp):", min_value=1)
        
    if st.button("Tambah ke Portofolio"):
        if add_ticker and add_shares > 0 and add_price > 0:
            add_ticker_jk = add_ticker if add_ticker.endswith(".JK") else add_ticker + ".JK"
            add_to_portfolio(add_ticker_jk, add_shares, add_price)
            st.success(f"{add_ticker} ditambahkan!")
            st.rerun()
            
    st.markdown("---")
    
    if not portfolio:
        st.info("Portofolio Anda masih kosong.")
    else:
        port_data = []
        for item in portfolio:
            tk = item['ticker']
            shares = item['shares']
            buy_p = item['buy_price']
            
            # Ambil harga terkini dan sinyal terkini
            curr_df = fetch_stock_data(tk, period="1mo")
            if not curr_df.empty:
                curr_price = curr_df['Close'].iloc[-1]
                curr_df = calculate_technical_indicators(curr_df, sma_fast=sma_fast_input, sma_slow=sma_slow_input, rsi_len=rsi_len_input)
                curr_df = generate_signals(curr_df, sma_fast=sma_fast_input, sma_slow=sma_slow_input, rsi_len=rsi_len_input)
                
                recent_sigs = curr_df[curr_df['Signal'] != 'Hold']
                curr_sig = recent_sigs['Signal'].iloc[-1] if not recent_sigs.empty else "Hold"
                
                floating_pl = (curr_price - buy_p) * shares
                floating_pct = ((curr_price - buy_p) / buy_p) * 100
                
                port_data.append({
                    "Ticker": tk.replace(".JK", ""),
                    "Lembar": shares,
                    "Harga Beli": round(buy_p, 2),
                    "Harga Skrg": round(curr_price, 2),
                    "Profit/Loss (Rp)": round(floating_pl, 2),
                    "P/L (%)": round(floating_pct, 2),
                    "Sinyal Terakhir": curr_sig
                })
        
        if port_data:
            port_df = pd.DataFrame(port_data)
            st.dataframe(port_df)
            
        remove_ticker = st.selectbox("Hapus Saham dari Portofolio:", [p['ticker'] for p in portfolio])
        if st.button("Hapus Saham"):
            remove_from_portfolio(remove_ticker)
            st.success("Dihapus!")
            st.rerun()
