import streamlit as st
import pandas as pd
import requests

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Riset Paket Makan UIN RMS", layout="centered", page_icon="🍗")

# --- 2. INITIALIZING SESSION STATE (Pencegahan Error) ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

# click_counter untuk menentukan urutan klik (1, 2, 3... sampai 27)
if 'click_counter' not in st.session_state:
    st.session_state.click_counter = 1

# Dictionary untuk menyimpan: { "Label Profil": Nilai_Ranking }
if 'assigned_ranks' not in st.session_state:
    st.session_state.assigned_ranks = {}

if 'profiles' not in st.session_state:
    # MENGIKUTI URUTAN GAMBAR: Paha(1-9), Dada(10-18), Sayap(19-27)
    parts = ["Paha", "Dada", "Sayap"]
    flavors = ["Pedas", "Sedang", "G Pedas"]
    drinks = ["Es Teh", "Es Jeruk", "Air Mineral"]
    
    # List ini akan menjadi master urutan Profil 1 sampai 27
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

# --- 4. FUNGSI KIRIM DATA (Mapping Ranking ke ID Profil) ---
def send_to_google_form(nama, angkatan, nim):
    # Endpoint Form Baru kamu
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfqFjwF7MgIFpXtk7PrZ6VLRIch6KilFYBc5KekeM2Z__i-GQ/formResponse"
    
    # --- LOGIKA PEMETAAN (MAPPING) ---
    # Kita membuat string hasil dengan menyisir daftar profil dari 1 sampai 27.
    # Sehingga posisi angka dalam string mewakili ID Profilnya.
    ordered_results = []
    for p in st.session_state.profiles:
        # Ambil nilai ranking yang tersimpan untuk profil ini
        rank_value = st.session_state.assigned_ranks.get(p['label'], 0)
        ordered_results.append(str(rank_value))
    
    # Menghasilkan string seperti: "3,1,2,5,..."
    ranking_string = ",".join(ordered_results)
    
    payload = {
        "entry.90333049": nama,           # Input A
        "entry.346547701": angkatan,      # Input B
        "entry.218479489": nim,           # Input C
        "entry.540131417": ranking_string # Input D
    }
    
    headers = {
        "Referer": "https://docs.google.com/forms/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.post(form_url, data=payload, headers=headers, timeout=10)
        return response.status_code
    except:
        return 500

# --- 5. HALAMAN LOGIN (GATE) ---
if st.session_state.get('user_data') is None:
    st.title("🍗 Riset Preferensi Paket Makan")
    st.subheader("Sains Data UIN Raden Mas Said")
    
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
    
    current_count = st.session_state.click_counter
    
    if current_count <= 27:
        st.write(f"Pilih paket untuk **Peringkat ke-{current_count}**")
        st.caption("(Klik menu yang paling Anda inginkan saat ini)")
        
        # Progress Bar
        progress_val = min(float(current_count - 1) / 27, 1.0)
        st.progress(progress_val)
        
        # Tampilkan Grid Tombol (Tetap urut tapi yang sudah dipilih menghilang)
        cols = st.columns(2)
        for idx, p in enumerate(st.session_state.profiles):
            # Cek apakah profil ini sudah diklik/diberi ranking
            if p['label'] not in st.session_state.assigned_ranks:
                icon = "🍗" if p['kat'] == "Paha" else "🥩" if p['kat'] == "Dada" else "🕊️"
                with cols[idx % 2]:
                    if st.button(f"{icon} {p['label']}", key=f"btn_{idx}", use_container_width=True):
                        # Simpan nomor urutan klik (Rank) ke profil tersebut
                        st.session_state.assigned_ranks[p['label']] = st.session_state.click_counter
                        st.session_state.click_counter += 1
                        st.rerun()
    else:
        # --- 7. HALAMAN HASIL & KIRIM DATA ---
        st.balloons()
        st.success("🏁 Semua paket telah berhasil diurutkan!")
        
        # Tampilkan ringkasan urutan Profil 1-27
        summary_list = []
        for i, p in enumerate(st.session_state.profiles):
            summary_list.append({
                "ID": f"Profil_{i+1}",
                "Menu": p['label'],
                "Ranking": st.session_state.assigned_ranks[p['label']]
            })
        
        df_summary = pd.DataFrame(summary_list)
        st.subheader("Ringkasan Urutan Profil 1-27")
        st.table(df_summary)

        if st.button("📤 KIRIM DATA KE DATABASE PUSAT", use_container_width=True, type="primary"):
            with st.spinner("Menyimpan ke Google Sheets..."):
                status = send_to_google_form(user['nama'], user['angkatan'], user['nim'])
                if status == 200:
                    st.success("✅ Data berhasil tersimpan! Terima kasih.")
                    st.balloons()
                else:
                    st.error(f"❌ Gagal mengirim. Status: {status}")

    # --- 8. SIDEBAR CONTROL ---
    with st.sidebar:
        st.header("Kontrol")
        if st.button("🔄 Ulangi Ranking"):
            st.session_state.assigned_ranks = {}
            st.session_state.click_counter = 1
            st.rerun()
        if st.button("🚪 Ganti Responden"):
            st.session_state.user_data = None
            st.session_state.assigned_ranks = {}
            st.session_state.click_counter = 1
            st.rerun()
