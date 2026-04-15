import streamlit as st
import pandas as pd
import requests

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Riset Paket Makan UIN RMS", layout="centered", page_icon="🍗")

# --- 2. INITIALIZING SESSION STATE ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

if 'ranking' not in st.session_state:
    st.session_state.ranking = []

if 'profiles' not in st.session_state:
    parts = ["Paha", "Dada", "Sayap"]
    flavors = ["Pedas", "Sedang", "G Pedas"]
    drinks = ["Es Teh", "Es Jeruk", "Air Mineral"]
    st.session_state.profiles = [
        {"label": f"{p} | {f} | {d}", "kat": p} 
        for p in parts for f in flavors for d in drinks
    ]

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    div.stButton > button {
        height: 3.5em;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.2s;
        margin-bottom: 10px;
    }
    div.stButton > button:hover {
        border-color: #FF4B4B;
        color: #FF4B4B;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNGSI KIRIM DATA (STRICT VERSION) ---
def send_to_google_form(nama, angkatan, nim, ranking_list):
    # Endpoint formResponse
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfv9fJ-I8ilVD8DBKyrrETja-zySAiOgKu2zJACwknvgDABzw/formResponse"
    
    ranking_string = ", ".join(ranking_list)
    
    # Payload ID sesuai link yang kamu berikan
    payload = {
        "entry.136391246": nama,
        "entry.79359752": angkatan,
        "entry.616519573": nim,
        "entry.86268960": ranking_string
    }
    
    # Headers lebih lengkap untuk meniru browser Chrome terbaru
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    try:
        # Menggunakan session agar lebih stabil
        session = requests.Session()
        response = session.post(form_url, data=payload, headers=headers, timeout=10)
        return response.status_code, response.reason
    except Exception as e:
        return 500, str(e)

# --- 5. HALAMAN LOGIN ---
if st.session_state.get('user_data') is None:
    st.title("🍗 Riset Preferensi Paket Makan")
    st.subheader("Data Science UIN Raden Mas Said")
    st.write("Silakan isi identitas Anda untuk memulai.")
    
    with st.form("login_gate"):
        nama = st.text_input("Nama Panggil", placeholder="Masukkan nama...")
        angkatan = st.selectbox("Angkatan", ["2023", "2024", "2025"], index=None, placeholder="Pilih tahun...")
        nim = st.text_input("3 Angka Terakhir NIM", placeholder="Contoh: 042", max_chars=3)
        
        submit_btn = st.form_submit_button("Masuk ke Pemilihan")
        
        if submit_btn:
            if nama.strip() and angkatan and nim.isdigit() and len(nim) == 3:
                st.session_state.user_data = {"nama": nama, "angkatan": angkatan, "nim": nim}
                st.rerun()
            else:
                st.warning("⚠️ Mohon lengkapi Nama, Angkatan, dan 3 digit NIM!")

# --- 6. HALAMAN PEMILIHAN ---
else:
    user = st.session_state.user_data
    st.title(f"Halo, {user['nama']}! 👋")
    st.write("Klik paket sesuai urutan **PALING DISUKAI** (Pilihan akan menghilang).")

    # Progress bar
    total = 27
    current_ranking = st.session_state.get('ranking', [])
    current_count = len(current_ranking)
    
    st.progress(current_count / total)
    st.info(f"Progress: **{current_count}** dari **{total}** paket terurut.")

    # Filter sisa opsi
    remaining = [p for p in st.session_state.profiles if p['label'] not in current_ranking]

    if remaining:
        cols = st.columns(2)
        for idx, p in enumerate(remaining):
            icon = "🍗" if p['kat'] == "Paha" else "🥩" if p['kat'] == "Dada" else "🕊️"
            with cols[idx % 2]:
                st.button(
                    f"{icon} {p['label']}", 
                    key=f"btn_{p['label']}", 
                    on_click=lambda l=p['label']: st.session_state.ranking.append(l),
                    use_container_width=True
                )
    else:
        # --- 7. HALAMAN HASIL & KIRIM ---
        st.balloons()
        st.success("🏁 Semua paket telah berhasil diurutkan!")
        
        df_display = pd.DataFrame({
            "Peringkat": range(1, 28),
            "Pilihan": st.session_state.ranking
        })
        st.dataframe(df_display, use_container_width=True)

        if st.button("📤 KIRIM DATA KE DATABASE PUSAT", use_container_width=True, type="primary"):
            with st.spinner("Menghubungi server Google..."):
                status, reason = send_to_google_form(
                    user['nama'], 
                    user['angkatan'], 
                    user['nim'], 
                    st.session_state.ranking
                )
                
                if status == 200:
                    st.success("✅ Data Berhasil Tersimpan!")
                    st.balloons()
                else:
                    st.error(f"❌ Error {status}: {reason}")
                    st.info("Pesan 401 berarti Google Form kamu masih terkunci.")

        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Backup: Download CSV", data=csv, file_name=f"rank_{user['nim']}.csv", use_container_width=True)

    # --- 8. SIDEBAR ---
    with st.sidebar:
        st.header("Kontrol")
        if st.button("🔄 Ulangi Ranking"):
            st.session_state.ranking = []
            st.rerun()
        if st.button("🚪 Keluar / Ganti User"):
            st.session_state.user_data = None
            st.session_state.ranking = []
            st.rerun()
