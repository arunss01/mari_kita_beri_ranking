import streamlit as st
import pandas as pd
import requests

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Riset Analisis Multivariat - FAHAM TEAM", layout="centered")

# --- 2. INITIALIZING SESSION STATE ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

if 'click_counter' not in st.session_state:
    st.session_state.click_counter = 1

if 'assigned_ranks' not in st.session_state:
    st.session_state.assigned_ranks = {}

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Definisi Atribut Baru (Total 12 Profil)
if 'profiles' not in st.session_state:
    parts = ["Dada", "Paha", "Sayap"]
    flavors = ["Pedas", "Gak Pedas"]
    drinks = ["Teh/Jus/Soft Drink", "Air Mineral"]
    st.session_state.profiles = [
        {"label": f"{p} | {f} | {d}", "kat": p} 
        for p in parts for f in flavors for d in drinks
    ]

# --- 3. CUSTOM CSS (ADAPTIF LIGHT & DARK MODE) ---
st.markdown("""
    <style>
    div.stButton > button {
        height: 3.5em;
        border-radius: 12px;
        font-weight: 600;
        margin-bottom: 10px;
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    .intro-box {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 25px;
        line-height: 1.6;
        box-shadow: rgba(0, 0, 0, 0.05) 0px 1px 2px 0px;
    }
    
    .team-box {
        font-size: 0.9em;
        background-color: rgba(128, 128, 128, 0.1);
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        border: 1px solid rgba(128, 128, 128, 0.1);
    }
    
    .footer {
        text-align: center;
        color: gray;
        padding: 40px 0 20px 0;
        font-size: 0.8em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNGSI KIRIM DATA ---
def send_to_google_form(nama, angkatan, nim):
    # Ganti URL ini dengan URL Google Form Kamu yang baru jika perlu
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfqFjwF7MgIFpXtk7PrZ6VLRIch6KilFYBc5KekeM2Z__i-GQ/formResponse"
    
    ordered_results = []
    for p in st.session_state.profiles:
        # Mengambil urutan klik langsung sebagai rank (1-12)
        rank_value = st.session_state.assigned_ranks.get(p['label'], 12)
        ordered_results.append(str(rank_value))
    
    ranking_string = ",".join(ordered_results)
    
    payload = {
        "entry.90333049": nama,
        "entry.346547701": angkatan,
        "entry.218479489": nim,
        "entry.540131417": ranking_string
    }
    
    headers = {"Referer": "https://docs.google.com/forms/", "User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.post(form_url, data=payload, headers=headers, timeout=10)
        return response.status_code
    except:
        return 500

# --- 5. LOGIKA HALAMAN ---

if st.session_state.submitted:
    st.balloons()
    st.title("Data Berhasil Terkirim")
    st.markdown(f"""
    ### Terima kasih atas partisipasi Kamu, {st.session_state.user_data['nama']}
    
    Data preferensi Kamu telah tersimpan. Urutan klik Kamu (1-12) telah dicatat sebagai representasi pilihan konsumen untuk analisis multivariat FAHAM TEAM.
    """)
    st.markdown('<div class="footer">© 2026 FAHAM TEAM. Program Studi Sains Data UIN Raden Mas Said Surakarta.</div>', unsafe_allow_html=True)

elif st.session_state.user_data is None:
    st.title("Riset Preferensi Konsumen Terhadap Paket Menu Ayam")
    
    st.markdown("""
    <div class="intro-box">
        <strong>Tentang Penelitian:</strong><br>
        Penelitian ini bertujuan untuk menganalisis preferensi mahasiswa terhadap berbagai kombinasi atribut paket menu ayam menggunakan metode statistika multivariat.<br><br>
        <strong>Kriteria Responden:</strong> Mahasiswa Program Studi Sains Data UIN Raden Mas Said Surakarta.<br>
        <strong>Estimasi Waktu:</strong> 1 Menit.<br><br>
        <strong>Disusun Oleh FAHAM TEAM:</strong>
        <div class="team-box">
            1. Annisa Zahrotu Firda Asfari (247411003)<br>
            2. Luthfiya Zuhura Syifa Fuadah (247411008)<br>
            3. Melani Yusi Aryanda (247411011)<br>
            4. Haya Nur Fadhilah (247411014)<br>
            5. Ahmad Ruhayani Azis (247411018)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_gate"):
        st.write("Silakan lengkapi identitas untuk memulai:")
        nama = st.text_input("Nama Panggil", placeholder="Tuliskan nama Kamu")
        angkatan = st.selectbox("Angkatan", ["2023", "2024", "2025"], index=None, placeholder="Pilih tahun angkatan")
        nim = st.text_input("3 Angka Terakhir NIM", placeholder="Contoh: 042", max_chars=3)
        
        if st.form_submit_button("Masuk ke Halaman Pemilihan"):
            if nama.strip() and angkatan and nim.isdigit() and len(nim) == 3:
                st.session_state.user_data = {"nama": nama, "angkatan": angkatan, "nim": nim}
                st.rerun()
            else:
                st.warning("Mohon lengkapi identitas Nama, Angkatan, dan 3 digit NIM.")
    
    st.markdown('<div class="footer">© 2026 FAHAM TEAM</div>', unsafe_allow_html=True)

else:
    user = st.session_state.user_data
    current_rank = st.session_state.click_counter
    
    if current_rank <= 12:
        st.title("Pemilihan Preferensi Menu")
        
        st.markdown(f"""
        <div class="intro-box">
            <strong>Panduan Teknis:</strong><br>
            1. Klik paket makanan secara berurutan mulai dari yang <strong>Paling Kamu Suka</strong> hingga <strong>Paling Kurang Disukai</strong>.<br>
            2. Klik pertama akan menjadi <strong>Peringkat 1 (Terbaik)</strong>, sedangkan klik terakhir menjadi <strong>Peringkat 12</strong>.<br>
            3. Menu yang telah Kamu klik akan otomatis menghilang dari daftar pilihan.<br><br>
            Status: Sedang menentukan pilihan untuk <strong>Peringkat ke-{current_rank}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(min(float(current_rank - 1) / 12, 1.0))
        
        remaining = [p for p in st.session_state.profiles if p['label'] not in st.session_state.assigned_ranks]
        
        # Grid layout untuk tombol
        cols = st.columns(2)
        for idx, p in enumerate(remaining):
            # Penentuan icon sesuai bagian daging
            icon = "🥩" if p['kat'] == "Dada" else "🍗" if p['kat'] == "Paha" else "🕊️"
            
            with cols[idx % 2]:
                if st.button(f"{icon} {p['label']}", key=f"btn_{p['label']}", use_container_width=True):
                    # Simpan urutan klik (1, 2, 3... 12)
                    st.session_state.assigned_ranks[p['label']] = st.session_state.click_counter
                    st.session_state.click_counter += 1
                    st.rerun()
    else:
        st.title("Konfirmasi Data")
        st.success("Seluruh paket telah berhasil diurutkan berdasarkan preferensi Kamu (1 = Paling Disukai).")
        
        summary = []
        # Menampilkan summary berdasarkan urutan yang diklik user
        sorted_summary = sorted(st.session_state.assigned_ranks.items(), key=lambda x: x[1])
        
        for rank, (label, click_idx) in enumerate(sorted_summary, 1):
            summary.append({
                "Peringkat": f"Ke-{rank}",
                "Kombinasi Menu": label
            })
        
        st.table(pd.DataFrame(summary))

        if st.button("Kirim Data ke Database Pusat", use_container_width=True, type="primary"):
            with st.spinner("Sedang memproses pengiriman data..."):
                status = send_to_google_form(user['nama'], user['angkatan'], user['nim'])
                if status == 200:
                    st.session_state.submitted = True
                    st.rerun()
                else:
                    st.error(f"Gagal mengirim data. (Status Error: {status})")

    st.markdown('<div class="footer">© 2026 FAHAM TEAM</div>', unsafe_allow_html=True)
