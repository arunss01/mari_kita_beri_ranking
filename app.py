import streamlit as st
import pandas as pd
import requests

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Riset Preferensi Konsumen", layout="centered")

# --- 2. INITIALIZING SESSION STATE ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'click_counter' not in st.session_state:
    st.session_state.click_counter = 1
if 'assigned_ranks' not in st.session_state:
    st.session_state.assigned_ranks = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Dataset 12 Profil (3 Daging x 2 Rasa x 2 Minuman)
if 'profiles' not in st.session_state:
    parts = ["Dada", "Paha", "Sayap"]
    flavors = ["Pedas", "Gak Pedas"]
    drinks = ["Teh/Jus/Soft Drink", "Air Mineral"]
    st.session_state.profiles = [
        {"label": f"{p} | {f} | {d}", "kat": p} 
        for p in parts for f in flavors for d in drinks
    ]

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    div.stButton > button {
        height: 3.5em; border-radius: 12px; font-weight: 600;
        background-color: var(--secondary-background-color);
        color: var(--text-color); border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .intro-box {
        background-color: var(--secondary-background-color);
        padding: 25px; border-radius: 12px; border-left: 5px solid #FF4B4B;
        margin-bottom: 25px; line-height: 1.6;
        box-shadow: rgba(0, 0, 0, 0.05) 0px 1px 2px 0px;
    }
    .team-box {
        font-size: 0.9em; background-color: rgba(128, 128, 128, 0.1);
        padding: 15px; border-radius: 8px; margin-top: 15px;
    }
    .footer { text-align: center; color: gray; padding: 40px 0 20px 0; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNGSI AUTO-SEND KE GOOGLE FORM ---
def auto_submit():
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfqFjwF7MgIFpXtk7PrZ6VLRIch6KilFYBc5KekeM2Z__i-GQ/formResponse"
    
    # Ranking 1 = Paling Disukai, 12 = Paling Tidak Disukai
    ordered_results = [str(st.session_state.assigned_ranks[p['label']]) for p in st.session_state.profiles]
    ranking_string = ",".join(ordered_results)
    
    user = st.session_state.user_data
    payload = {
        "entry.90333049": user['nama'],
        "entry.346547701": user['angkatan'],
        "entry.218479489": user['nim'],
        "entry.540131417": ranking_string
    }
    
    headers = {"Referer": "https://docs.google.com/forms/", "User-Agent": "Mozilla/5.0"}
    try:
        requests.post(form_url, data=payload, headers=headers, timeout=10)
        return True
    except:
        return False

# --- 5. LOGIKA ANTARMUKA ---

# --- A. HALAMAN SUKSES (AUTO-DISPLAY SETELAH KLIK KE-12) ---
if st.session_state.submitted:
    st.balloons()
    st.title("Data Berhasil Terkirim")
    st.markdown(f"### Terima kasih atas partisipasi Kamu, {st.session_state.user_data['nama']}!")
    
    st.markdown("""
    Data preferensi Kamu telah otomatis tersimpan di database kami. Berikut adalah ringkasan urutan menu yang telah Kamu tentukan (1 = Paling Disukai):
    """)
    
    # Tabel Ringkasan
    summary_data = []
    sorted_ranks = sorted(st.session_state.assigned_ranks.items(), key=lambda x: x[1])
    for rank, (label, _) in enumerate(sorted_ranks, 1):
        summary_data.append({"Peringkat": f"Ke-{rank}", "Kombinasi Menu": label})
    
    st.table(pd.DataFrame(summary_data))
    
    st.info("Kontribusi Kamu sangat berharga bagi kelancaran riset kami. Kamu bisa menutup halaman ini sekarang.")
    st.markdown('<div class="footer">© 2026 Program Studi Sains Data UIN Raden Mas Said Surakarta.</div>', unsafe_allow_html=True)

# --- B. HALAMAN AWAL (PENGANTAR & LOGIN) ---
elif st.session_state.user_data is None:
    st.title("Riset Preferensi Konsumen Terhadap Paket Menu Ayam")
    
    st.markdown("""
    <div class="intro-box">
        <strong>Tentang Penelitian:</strong><br>
        Penelitian ini bertujuan untuk menganalisis preferensi mahasiswa terhadap berbagai kombinasi atribut paket menu ayam menggunakan metode statistika multivariat.<br><br>
        <strong>Kriteria Responden:</strong> Mahasiswa Program Studi Sains Data UIN Raden Mas Said Surakarta.<br>
        <strong>Estimasi Waktu:</strong> 1 Menit.<br><br>
        <strong>Disusun Oleh:</strong>
        <div class="team-box">
            1. Annisa Zahrotu Firda Asfari (247411003)<br>
            2. Luthfiya Zuhura Syifa Fuadah (247411008)<br>
            3. Melani Yusi Aryanda (247411011)<br>
            4. Haya Nur Fadhilah (247411014)<br>
            5. Ahmad Ruhayani Azis (247411018)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login"):
        st.write("Silakan lengkapi identitas untuk memulai:")
        nama = st.text_input("Nama Panggil", placeholder="Tuliskan nama Kamu")
        angkatan = st.selectbox("Angkatan", ["2023", "2024", "2025"], index=None, placeholder="Pilih tahun angkatan")
        nim = st.text_input("3 Angka Terakhir NIM", placeholder="Contoh: 042", max_chars=3)
        
        if st.form_submit_button("Masuk ke Halaman Pemilihan"):
            if nama.strip() and angkatan and len(nim) == 3:
                st.session_state.user_data = {"nama": nama, "angkatan": angkatan, "nim": nim}
                st.rerun()
            else:
                st.warning("Mohon lengkapi identitas Nama, Angkatan, dan 3 digit NIM.")
    st.markdown('<div class="footer">© 2026 FAHAM TEAM</div>', unsafe_allow_html=True)

# --- C. HALAMAN PEMILIHAN (AUTO-SUBMIT PADA KLIK TERAKHIR) ---
else:
    current_rank = st.session_state.click_counter
    
    if current_rank <= 12:
        st.title("Pemilihan Preferensi Menu")
        
        st.markdown(f"""
        <div class="intro-box">
            <strong>Panduan Teknis:</strong><br>
            1. Klik paket makanan secara berurutan mulai dari yang <strong>Paling Kamu Suka</strong> hingga <strong>Paling Kurang Disukai</strong>.<br>
            2. Klik pertama akan mendapatkan <strong>Peringkat 1</strong>, sedangkan klik terakhir mendapatkan <strong>Peringkat 12</strong>.<br>
            3. Menu yang telah Kamu klik akan otomatis menghilang dari daftar pilihan.<br><br>
            Status: Sedang menentukan pilihan untuk <strong>Peringkat ke-{current_rank}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(float(current_rank - 1) / 12)
        
        remaining = [p for p in st.session_state.profiles if p['label'] not in st.session_state.assigned_ranks]
        cols = st.columns(2)
        
        for idx, p in enumerate(remaining):
            icon = "🥩" if p['kat'] == "Dada" else "🍗" if p['kat'] == "Paha" else "🕊️"
            with cols[idx % 2]:
                if st.button(f"{icon} {p['label']}", key=f"btn_{p['label']}", use_container_width=True):
                    # Catat urutan klik
                    st.session_state.assigned_ranks[p['label']] = st.session_state.click_counter
                    
                    # Logika Auto-Submit pada klik ke-12
                    if st.session_state.click_counter == 12:
                        with st.spinner("Sedang mengirim data otomatis..."):
                            if auto_submit():
                                st.session_state.submitted = True
                                st.rerun()
                            else:
                                st.error("Gagal mengirim data otomatis. Mohon periksa koneksi.")
                    else:
                        st.session_state.click_counter += 1
                        st.rerun()

    st.markdown('<div class="footer">© 2026 FAHAM TEAM</div>', unsafe_allow_html=True)
