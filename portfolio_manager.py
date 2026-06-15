import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "ISI_URL_SUPABASE_ANDA")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "ISI_KEY_SUPABASE_ANDA")

def get_supabase_client() -> Client:
    # Mengembalikan dummy client jika tidak dikonfigurasi, agar tidak error di prototipe
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def load_portfolio():
    try:
        supabase = get_supabase_client()
        response = supabase.table("portfolio").select("*").execute()
        return response.data
    except Exception as e:
        print(f"Error loading portfolio dari Supabase: {e}")
        return []

def add_to_portfolio(ticker, shares, buy_price):
    try:
        supabase = get_supabase_client()
        # Cek apakah ticker sudah ada
        response = supabase.table("portfolio").select("*").eq("ticker", ticker).execute()
        existing_data = response.data
        
        if existing_data and len(existing_data) > 0:
            item = existing_data[0]
            # Update rata-rata harga dan jumlah
            total_cost = (item['shares'] * item['buy_price']) + (shares * buy_price)
            new_shares = item['shares'] + shares
            new_buy_price = total_cost / new_shares
            
            supabase.table("portfolio").update({
                "shares": new_shares,
                "buy_price": new_buy_price
            }).eq("ticker", ticker).execute()
        else:
            # Tambahkan data baru
            supabase.table("portfolio").insert({
                "ticker": ticker,
                "shares": shares,
                "buy_price": buy_price
            }).execute()
        return True
    except Exception as e:
        print(f"Error adding to portfolio di Supabase: {e}")
        return False

def remove_from_portfolio(ticker):
    try:
        supabase = get_supabase_client()
        supabase.table("portfolio").delete().eq("ticker", ticker).execute()
    except Exception as e:
        print(f"Error removing from portfolio di Supabase: {e}")

