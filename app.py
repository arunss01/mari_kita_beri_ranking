import streamlit as st
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Riset Paket Makan UIN RMS", layout="centered")

# --- CUSTOM CSS UNTUK TAMPILAN ---
st.markdown("""
    <style>
    div.stButton > button {
        height: 3em;
        border-radius: 10px;
        border: 1px solid #ddd;
        transition: all 0.3s;
    }
    /* Warna khusus per kategori (Visual Cues) */
    .paha-btn { background-color: #FFF3E0; border-left: 5px solid #FF9800 !important; }
    .dada-btn { background-color: #E3F2FD; border-left: 5px solid #2196F3 !important; }
    .sayap-btn { background-color: #F1F8E9; border-left: 5px solid #8BC34A !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZING SESSION STATE ---
if 'profiles' not in st.session_state:
    parts = ["Paha", "Dada", "Sayap"]
    flavors = ["Pedas", "Sedang", "G Pedas"]
    drinks = ["Es Teh", "Es Jeruk", "Air Mineral"]
    # List of Dict untuk mempermudah identifikasi kategori
    st.session_state.profiles = [
        {"label": f"{p} | {f} | {d}", "kat": p} 
        for p in parts for f in flavors for d in drinks
    ]
    st.session_state.ranking = []
    st.session_state.user_data = None

# --- FUNGSI LOGIKA ---
def handle_click(profile_label):
    st.session_state.ranking.append(profile_label)

# --- 1. HALAMAN LOGIN (GATE) ---
if st.session_state.user_data is None:
    st.title("🍗 Survei Preferensi Rasa")
    st.write("Silakan isi identitas Anda untuk memulai.")
    
    with st.form("login_form"):
        nama = st.text_input("Nama Panggil")
        nim = st.text_input("3 Angka Terakhir NIM", max_chars=3)
        submit_auth = st.form_submit_button("Mulai Pilih")
        
        if submit_auth:
            if nama and nim.isdigit() and len(nim) == 3:
                st.session_state.user_data = {"nama": nama, "nim": nim}
                st.rerun()
            else:
                st.error("Mohon isi nama dan 3 angka NIM dengan benar!")

# --- 2. HALAMAN PEMILIHAN ---
else:
    st.title(f"Halo, {st.session_state.user_data['nama']}!")
    st.write("Klik paket di bawah sesuai urutan yang **paling Anda inginkan**.")
    
    # Progress Bar agar responden tahu sisa tugasnya
    progress = len(st.session_state.ranking) / 27
    st.progress(progress)
    st.caption(f"Terpilih: {len(st.session_state.ranking)} dari 27 paket")

    # Filter sisa profil yang belum diklik
    remaining = [p for p in st.session_state.profiles if p['label'] not in st.session_state.ranking]

    if remaining:
        # Menampilkan Grid Tombol
        cols = st.columns(2)
        for idx, p in enumerate(remaining):
            # Beri icon berdasarkan kategori
            icon = "🍗" if p['kat'] == "Paha" else "🥩" if p['kat'] == "Dada" else "🕊️"
            label_full = f"{icon} {p['label']}"
            
            with cols[idx % 2]:
                st.button(
                    label_full, 
                    key=p['label'], 
                    on_click=handle_click, 
                    args=(p['label'],), 
                    use_container_width=True
                )
    else:
        # --- 3. HALAMAN HASIL ---
        st.success("✅ Semua paket telah diurutkan!")
        
        # Susun DataFrame Akhir
        df_result = pd.DataFrame({
            "Nama": st.session_state.user_data['nama'],
            "NIM_Akhir": st.session_state.user_data['nim'],
            "Peringkat": range(1, 28),
            "Pilihan_Profil": st.session_state.ranking
        })
        
        st.dataframe(df_result, use_container_width=True)
        
        # Download Data
        csv = df_result.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📩 Download Hasil Data",
            data=csv,
            file_name=f"hasil_{st.session_state.user_data['nim']}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Tombol Reset
    if st.sidebar.button("🔄 Reset Pilihan"):
        st.session_state.ranking = []
        st.rerun()

    if st.sidebar.button("🚪 Keluar/Ganti User"):
        st.session_state.user_data = None
        st.session_state.ranking = []
        st.rerun()
