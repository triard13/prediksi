# 📈 Sistem Analitik Saham IHSG Pro

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B.svg)
![Machine Learning](https://img.shields.io/badge/AI-Machine_Learning-green.svg)
![Database](https://img.shields.io/badge/Database-Supabase-3ECF8E.svg)

**Sistem Analitik Saham IHSG Pro** adalah aplikasi web interaktif komprehensif yang dirancang untuk membantu investor dan *trader* di pasar saham Indonesia (IHSG). Aplikasi ini menggabungkan kekuatan analisis teknikal tradisional, analisis sentimen berita, dan prediksi *Machine Learning* untuk memberikan wawasan pasar yang mendalam secara *real-time*.

---

## 🎯 Deskripsi Proyek
Berinvestasi di pasar saham membutuhkan keputusan yang didasari oleh data, bukan emosi. Aplikasi ini bertindak sebagai asisten analitik pribadi yang mengotomatiskan penarikan data harga saham, menghitung indikator teknikal kompleks (SMA, RSI, MACD, Bollinger Bands), hingga menguji strategi (*backtesting*). 

Dibangun menggunakan **Python** dan **Streamlit**, aplikasi ini menyajikan antarmuka (*dashboard*) yang bersih, responsif, dan mudah digunakan langsung dari *browser* Anda. Seluruh data portofolio juga tersimpan secara aman di *cloud* menggunakan **Supabase**.

---

## ✨ Fitur Utama (Key Features)

### 1. 📊 Analisis Individu Komprehensif
- Visualisasi grafik *candlestick* interaktif menggunakan Plotly.
- Perhitungan otomatis indikator teknikal (RSI, MACD, Moving Averages, Bollinger Bands, Stochastic).
- Ringkasan data fundamental (Market Cap, PE Ratio, PBV, Dividend Yield).
- Analisis sentimen berita otomatis untuk melihat pandangan media terhadap emiten.

### 2. 🤖 Prediksi Machine Learning
- Menggunakan algoritma **Random Forest** & **XGBoost** untuk memprediksi probabilitas arah pergerakan harga saham untuk hari perdagangan berikutnya.
- Model dilatih secara dinamis (*on-the-fly*) berdasarkan pola historis masing-masing saham.

### 3. 🔎 Screener Pasar Otomatis
- Memindai puluhan saham *blue-chip* dan likuid di IHSG dalam hitungan detik.
- Mengidentifikasi saham mana yang sedang memberikan sinyal **Strong Buy**, **Buy**, **Sell**, atau **Strong Sell** berdasarkan persilangan indikator teknikal.

### 4. ⏱️ Backtesting Dinamis
- Uji keandalan strategi teknikal Anda sebelum menggunakan uang sungguhan!
- Menyimulasikan strategi jual-beli berdasarkan sinyal sistem pada data historis (misal: 1 tahun terakhir).
- Membandingkan hasil *return* algoritma vs strategi *Buy & Hold* tradisional.

### 5. 💼 Manajemen Portofolio Berbasis Cloud
- Lacak saham yang Anda miliki beserta harga rata-rata pembelian.
- Terintegrasi dengan basis data **Supabase** (PostgreSQL) sehingga data portofolio Anda tidak akan hilang meskipun aplikasi ditutup.
- Menghitung persentase keuntungan/kerugian (*Gain/Loss*) secara *real-time* berdasarkan harga pasar saat ini.

---

## 💡 Hasil Akhir (Outcomes)
Dengan menggunakan sistem ini, pengguna diharapkan dapat:
1. **Menghemat Waktu:** Tidak perlu lagi menggambar garis *support/resistance* atau menghitung RSI secara manual.
2. **Keputusan Objektif:** Mengurangi bias emosional dengan bersandar pada sinyal algoritma dan probabilitas *Machine Learning*.
3. **Manajemen Risiko:** Menggunakan fitur *Backtesting* untuk melihat apakah sebuah strategi benar-benar efektif di masa lalu sebelum diterapkan.
4. **Sentralisasi Data:** Memantau portofolio, membaca sentimen berita, dan menganalisis teknikal dalam satu layar.

---

## 🛠️ Teknologi yang Digunakan (Tech Stack)
- **Frontend:** Streamlit
- **Backend & Pemrosesan Data:** Python, Pandas, NumPy
- **Visualisasi:** Plotly Graph Objects
- **Machine Learning:** Scikit-Learn (Random Forest), XGBoost
- **Sumber Data:** Yahoo Finance API (`yfinance`), BeautifulSoup4
- **Database:** Supabase (PostgreSQL)
- **Sentimen Analisis:** VaderSentiment

---

## 🚀 Cara Instalasi & Penggunaan (Local Run)

1. **Kloning Repositori**
   ```bash
   git clone https://github.com/username/prediksi-ihsg.git
   cd prediksi-ihsg
   ```

2. **Buat Virtual Environment (Opsional tapi disarankan)**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Instal Dependensi**
   ```bash
   pip install -r requirements.txt
   ```

4. **Atur Variabel Lingkungan (.env)**
   Buat file bernama `.env` di folder utama dan isi dengan konfigurasi Supabase Anda:
   ```env
   SUPABASE_URL="https://proyek-anda.supabase.co"
   SUPABASE_KEY="kunci-rahasia-api-anda"
   APP_PASSWORD="password_rahasia_untuk_login"
   ```

5. **Jalankan Aplikasi**
   ```bash
   streamlit run app.py
   ```
   Aplikasi akan otomatis terbuka di *browser* Anda pada alamat `http://localhost:8501`.

---

## ⚠️ Disklaimer (Disclaimer)
*Aplikasi ini dibuat murni untuk tujuan edukasi, riset, dan analisis informasi. Keputusan investasi dan *trading* di pasar modal mengandung risiko tinggi. Prediksi *Machine Learning* dan sinyal teknikal tidak menjamin keuntungan di masa depan. Pengembang tidak bertanggung jawab atas kerugian finansial yang mungkin timbul dari penggunaan aplikasi ini.*
