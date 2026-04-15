import streamlit as st
import pandas as pd

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Riset Paket Makan UIN RMS", layout="centered")

# --- 2. INITIALIZING SESSION STATE (Pencegahan AttributeError) ---
# Kita pastikan semua kunci "lahir" dulu saat aplikasi pertama kali dibuka
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

if 'ranking' not in st.session_state:
    st.session_state.ranking = []

if 'profiles' not in st.session_state:
    # Generasi 27 profil secara otomatis
    parts = ["Paha", "Dada", "Sayap"]
    flavors = ["Pedas", "Sedang", "G Pedas"]
    drinks = ["Es Teh", "Es Jeruk", "Air Mineral"]
    st.session_state.profiles = [
        {"label": f"{p} | {f} | {d}", "kat": p} 
        for p in parts for f in flavors for d in drinks
    ]

# --- 3. CUSTOM CSS (Visual Identity) ---
st.markdown("""
    <style>
    /* Styling tombol agar lebih besar dan melengkung */
    div.stButton > button {
        height: 3.5em;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.2s ease;
        margin-bottom: 10px;
    }
    /* Efek hover agar interaktif */
    div.stButton > button:hover {
        transform: scale(1.02);
        border-color: #FF4B4B;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HALAMAN LOGIN (GATE) ---
# Menggunakan .get() agar ekstra aman dari error
if st.session_state.get('user_data') is None:
    st.title("🍗 Riset Preferensi Paket Makan")
    st.subheader("Data Science UIN Raden Mas Said")
    st.write("Selamat datang! Mohon isi identitas singkat sebelum memulai pemilihan.")
    
    with st.form("gate_form"):
        nama = st.text_input("Nama Panggil", placeholder="Masukkan nama Anda...")
        nim = st.text_input("3 Angka Terakhir NIM", placeholder="Contoh: 042", max_chars=3)
        
        st.caption("Data ini digunakan untuk validasi responden murni.")
        submit_btn = st.form_submit_button("Masuk ke Pemilihan")
        
        if submit_btn:
            if nama.strip() != "" and nim.isdigit() and len(nim) == 3:
                st.session_state.user_data = {"nama": nama, "nim": nim}
                st.rerun()
            else:
                st.warning("⚠️ Mohon masukkan Nama dan 3 angka NIM dengan benar!")

# --- 5. HALAMAN PEMILIHAN ---
else:
    user = st.session_state.user_data
    st.title(f"Halo, {user['nama']}! 👋")
    st.write("Silakan klik paket di bawah berdasarkan urutan **PALING ANDA INGINKAN**.")
    st.write("Pilihan akan menghilang satu per satu setelah Anda klik.")

    # Indikator Progres (Sangat penting untuk UX)
    total_profil = 27
    terpilih = len(st.session_state.ranking)
    progress_val = terpilih / total_profil
    
    st.progress(progress_val)
    st.info(f"Progress: **{terpilih}** dari **{total_profil}** paket terurut.")

    # Ambil sisa profil yang belum dipilih
    remaining = [p for p in st.session_state.profiles if p['label'] not in st.session_state.ranking]

    if remaining:
        # Menampilkan Grid 2 Kolom (Cocok untuk Mobile)
        cols = st.columns(2)
        for idx, p in enumerate(remaining):
            # Logika Warna & Icon berdasarkan Kategori (Visual Differentiation)
            if p['kat'] == "Paha":
                btn_label = f"🍗 {p['label']}"
            elif p['kat'] == "Dada":
                btn_label = f"🥩 {p['label']}"
            else: # Sayap
                btn_label = f"🕊️ {p['label']}"
            
            with cols[idx % 2]:
                # Tombol Aksi
                st.button(
                    btn_label, 
                    key=f"btn_{p['label']}", 
                    on_click=lambda l=p['label']: st.session_state.ranking.append(l),
                    use_container_width=True
                )
    else:
        # --- 6. HALAMAN HASIL (SELESAI) ---
        st.balloons()
        st.success("🏁 Luar biasa! Anda telah menyelesaikan seluruh urutan.")
        
        # Susun data hasil dalam tabel murni
        # Peringkat 1 adalah yang diklik PERTAMA (Paling Disukai)
        df_result = pd.DataFrame({
            "Peringkat": range(1, 28),
            "Profil Paket": st.session_state.ranking
        })
        
        # Tambahkan metadata user ke DataFrame untuk CSV
        df_export = df_result.copy()
        df_export['Responden'] = user['nama']
        df_export['NIM_3'] = user['nim']

        st.subheader("Ringkasan Urutan Anda:")
        st.dataframe(df_result, use_container_width=True)
        
        # Ekspor Data
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Download Hasil Data (CSV)",
            data=csv,
            file_name=f"data_ranking_{user['nim']}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.warning("Pastikan Anda sudah menekan tombol download sebelum menutup halaman ini.")

    # --- 7. SIDEBAR (KONTROL EXTRA) ---
    with st.sidebar:
        st.header("Opsi")
        if st.button("🔄 Ulangi Ranking"):
            st.session_state.ranking = []
            st.rerun()
        
        if st.button("🚪 Keluar / Ganti User"):
            st.session_state.user_data = None
            st.session_state.ranking = []
            st.rerun()
            
        st.divider()
        st.caption("Riset Conjoint Analysis - Sains Data UIN RMS")
