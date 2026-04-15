import streamlit as st
import pandas as pd
import requests

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Riset Paket Makan UIN RMS", layout="centered", page_icon="🍗")

# --- 2. INITIALIZING SESSION STATE (Pagar Error) ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

if 'ranking' not in st.session_state:
    st.session_state.ranking = []

if 'profiles' not in st.session_state:
    parts = ["Paha", "Dada", "Sayap"]
    flavors = ["Pedas", "Sedang", "G Pedas"]
    drinks = ["Es Teh", "Es Jeruk", "Air Mineral"]
    # List berisi dictionary profil
    st.session_state.profiles = [
        {"label": f"{p} | {f} | {d}", "kat": p} 
        for p in parts for f in flavors for d in drinks
    ]

# --- 3. CUSTOM CSS (Visual Identity) ---
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

# --- 4. FUNGSI KIRIM DATA KE GOOGLE FORM ---
def send_to_google_form(nama, angkatan, nim, ranking_list):
    # Mengubah /viewform menjadi /formResponse
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfv9fJ-I8ilVD8DBKyrrETja-zySAiOgKu2zJACwknvgDABzw/formResponse"
    
    # Menggabungkan list ranking menjadi satu string panjang dipisahkan koma
    ranking_string = ", ".join(ranking_list)
    
    # ID Entry berdasarkan link yang kamu berikan
    payload = {
        "entry.136391246": nama,           # a
        "entry.79359752": angkatan,        # b
        "entry.616519573": nim,            # c
        "entry.86268960": ranking_string   # d
    }
    
    try:
        response = requests.post(form_url, data=payload)
        return response.status_code == 200
    except:
        return False

# --- 5. HALAMAN LOGIN (GATE) ---
if st.session_state.get('user_data') is None:
    st.title("🍗 Riset Preferensi Paket Makan")
    st.subheader("Sains Data UIN Raden Mas Said")
    st.write("Silakan isi identitas Anda untuk memulai pemilihan urutan.")
    
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
    st.write("Klik paket mulai dari yang **PALING ANDA INGINKAN** sampai yang tidak diinginkan.")

    # Progress Tracking
    total = 27
    current_ranking = st.session_state.get('ranking', [])
    current_count = len(current_ranking)
    
    st.progress(current_count / total)
    st.info(f"Progress: **{current_count}** dari **{total}** paket telah dipilih.")

    # Ambil sisa profil yang belum diklik
    remaining = [p for p in st.session_state.profiles if p['label'] not in current_ranking]

    if remaining:
        # Tampilan Grid 2 Kolom
        cols = st.columns(2)
        for idx, p in enumerate(remaining):
            # Penentuan Icon Visual
            icon = "🍗" if p['kat'] == "Paha" else "🥩" if p['kat'] == "Dada" else "🕊️"
            
            with cols[idx % 2]:
                st.button(
                    f"{icon} {p['label']}", 
                    key=f"btn_{p['label']}", 
                    on_click=lambda l=p['label']: st.session_state.ranking.append(l),
                    use_container_width=True
                )
    else:
        # --- 7. HALAMAN SELESAI & KIRIM DATA ---
        st.balloons()
        st.success("🏁 Semua paket telah berhasil diurutkan!")
        
        # Tampilkan tabel urutan untuk konfirmasi
        df_display = pd.DataFrame({
            "Peringkat": range(1, 28),
            "Pilihan Anda": st.session_state.ranking
        })
        st.subheader("Konfirmasi Urutan Pilihan Anda")
        st.dataframe(df_display, use_container_width=True)

        # TOMBOL KIRIM KE GOOGLE SHEETS (Lewat Google Form)
        if st.button("📤 KIRIM DATA KE DATABASE PUSAT", use_container_width=True, type="primary"):
            with st.spinner("Menyimpan data..."):
                success = send_to_google_form(
                    user['nama'], 
                    user['angkatan'], 
                    user['nim'], 
                    st.session_state.ranking
                )
                if success:
                    st.success("✅ Data berhasil tersimpan di Google Sheets!")
                    st.balloons()
                else:
                    st.error("❌ Terjadi kendala saat mengirim data. Silakan coba lagi.")

        # Tombol Backup Download
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            "💾 Download Backup (CSV)", 
            data=csv, 
            file_name=f"rank_{user['nim']}.csv",
            use_container_width=True
        )

    # --- 8. SIDEBAR CONTROL ---
    with st.sidebar:
        st.header("Opsi")
        if st.button("🔄 Ulangi Ranking"):
            st.session_state.ranking = []
            st.rerun()
        if st.button("🚪 Ganti Responden"):
            st.session_state.user_data = None
            st.session_state.ranking = []
            st.rerun()
        st.divider()
        st.caption("Aplikasi Pengumpul Data Conjoint - Aruna (UIN RMS)")
