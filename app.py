import streamlit as st
import pandas as pd

# 1. Daftar 27 Profil (Bisa kamu sesuaikan)
if 'profiles' not in st.session_state:
    parts = ["Paha", "Dada", "Sayap"]
    flavors = ["Pedas", "Sedang", "G Pedas"]
    drinks = ["Es Teh", "Es Jeruk", "Air Mineral"]
    st.session_state.profiles = [f"{p} - {f} - {d}" for p in parts for f in flavors for d in drinks]
    st.session_state.ranking = []

st.set_page_config(page_title="Riset Paket Makan", layout="centered")

st.title("🍗 Survei Pilihan Paket Makan")
st.write(f"Silakan klik paket di bawah mulai dari yang **PALING ANDA SUKAI** hingga yang tidak disukai.")
st.info(f"Urutan saat ini: **{len(st.session_state.ranking) + 1} dari 27**")

# 2. Logika klik tombol
def handle_click(profile):
    st.session_state.ranking.append(profile)

# 3. Tampilan Grid Tombol (2 kolom agar nyaman di HP)
cols = st.columns(2)
remaining_profiles = [p for p in st.session_state.profiles if p not in st.session_state.ranking]

if remaining_profiles:
    for idx, profile in enumerate(remaining_profiles):
        with cols[idx % 2]:
            st.button(profile, key=profile, on_click=handle_click, use_container_width=True)
else:
    st.success("✅ Semua paket telah diurutkan!")
    
    # 4. Tampilkan Hasil Akhir
    df_result = pd.DataFrame({
        "Peringkat": range(1, 28),
        "Profil": st.session_state.ranking
    })
    st.table(df_result)
    
    # Tombol Download Hasil
    csv = df_result.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data Hasil (CSV)", csv, "hasil_ranking.csv", "text/csv")

# 5. Tombol Reset jika salah klik
if st.button("🔄 Ulangi Dari Awal"):
    st.session_state.ranking = []
    st.rerun()
