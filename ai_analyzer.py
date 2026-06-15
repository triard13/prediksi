import os
import google.generativeai as genai

def generate_ai_analysis(ticker, current_price, prediction_text, signals_df, news_sentiment):
    """
    Menghasilkan analisis komprehensif menggunakan Google Gemini AI
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "❌ **ERROR:** `GEMINI_API_KEY` belum diatur. Silakan dapatkan API Key dari Google AI Studio dan masukkan ke dalam file `.env` atau Streamlit Secrets Anda."
        
    try:
        genai.configure(api_key=api_key)
        
        # Ekstrak sinyal terakhir dengan aman
        last_signal = signals_df['Signal'].iloc[-1] if (not signals_df.empty and 'Signal' in signals_df.columns) else "Tidak diketahui"
        
        # Ekstrak nilai teknikal dengan aman
        cols = signals_df.columns
        sma_fast_col = [c for c in cols if c.startswith('SMA_')][0] if any(c.startswith('SMA_') for c in cols) else None
        sma_slow_col = [c for c in cols if c.startswith('SMA_')][-1] if sum(c.startswith('SMA_') for c in cols) > 1 else None
        rsi_col = [c for c in cols if c.startswith('RSI_')][0] if any(c.startswith('RSI_') for c in cols) else None
        
        sma_fast = f"{signals_df[sma_fast_col].iloc[-1]:.0f}" if sma_fast_col else "N/A"
        sma_slow = f"{signals_df[sma_slow_col].iloc[-1]:.0f}" if sma_slow_col else "N/A"
        rsi = f"{signals_df[rsi_col].iloc[-1]:.2f}" if rsi_col else "N/A"
        
        # Format angka harga
        try:
            price_formatted = f"Rp {float(current_price):,.0f}"
        except:
            price_formatted = str(current_price)
            
        # Persiapkan prompt
        prompt = f"""
Anda adalah seorang analis saham profesional dan penasihat keuangan yang brilian di pasar saham Indonesia (IHSG).
Tugas Anda adalah memberikan analisis singkat, tajam, dan sangat mudah dipahami (namun profesional) untuk saham {ticker}.

Berikut adalah data teknikal dan pasar terbaru yang berhasil sistem kumpulkan untuk saham {ticker}:
- Harga Penutupan Terakhir: {price_formatted}
- Prediksi Model Machine Learning: {prediction_text}
- Sinyal Teknikal Gabungan: {last_signal}
- Nilai Moving Average (Cepat): {sma_fast}
- Nilai Moving Average (Lambat): {sma_slow}
- RSI Momentum: {rsi} (Panduan: >70 overbought/jenuh beli, <30 oversold/jenuh jual)
- Sentimen Berita & Media: {news_sentiment['label']}

Berdasarkan data di atas, tolong berikan opini Anda mengenai arah pergerakan saham ini.
Aturan format respons:
1. Berikan Ringkasan Eksekutif maksimum 2-3 paragraf. Jelaskan secara logis kaitan antara indikator teknikal, prediksi ML, dan sentimen berita.
2. Gunakan *bullet points* jika ada poin yang penting.
3. Di bagian paling bawah, tulis dengan huruf tebal dan kapital: **REKOMENDASI: [BELI / TAHAN / JUAL]** diikuti dengan 1 kalimat alasan terkuat.
4. Gunakan gaya bahasa Indonesia yang profesional, ramah, dan mudah dicerna pemula. Hindari jargon rumit tanpa penjelasan.
"""
        
        # Gunakan model Gemini terbaru yang cepat
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
         return f"⚠️ **Terjadi kesalahan saat menghubungi Gemini AI:** `{str(e)}`"
