import streamlit as st
import pandas as pd
import requests

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Riset FAHAM TEAM - Data Science", layout="centered")

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
        padding: 20px; border-radius: 12px; border-left: 5px solid #FF4B4B;
        margin-bottom: 20px; line-height: 1.6;
    }
    .footer { text-align: center; color: gray; font-size: 0.8em; padding: 30px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNGSI AUTO-SEND KE GOOGLE FORM ---
def auto_submit():
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfqFjwF7MgIFpXtk7PrZ6VLRIch6KilFYBc5KekeM2Z__i-GQ/formResponse"
    
    # Ranking 1 = Paling Disukai, 12 = Paling Tidak Disukai
    # Mengambil urutan berdasarkan susunan profil asli agar database konsisten
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

# --- HALAMAN SETELAH SUBMIT (UCAPAN TERIMA KASIH & TABEL) ---
if st.session_state.submitted:
    st.balloons()
    st.title("Data Berhasil Terkirim!")
    st.success(f"Terima kasih atas partisipasi Kamu, {st.session_state.user_data['nama']}!")
    
    st.markdown("""
    ### Ringkasan Pilihan Kamu:
    Data Kamu telah otomatis tersimpan di database kami. Berikut adalah urutan preferensi yang baru saja Kamu input (1 = Paling Disukai):
    """)
    
    # Membuat tabel ringkasan berdasarkan urutan klik
    summary_data = []
    # Sort berdasarkan peringkat (value dari dictionary)
    sorted_ranks = sorted(st.session_state.assigned_ranks.items(), key=lambda item: item[1])
    
    for rank, (label, _) in enumerate(sorted_ranks, 1):
        summary_data.append({"Peringkat": f"Ke-{rank}", "Kombinasi Menu": label})
    
    st.table(pd.DataFrame(summary_data))
    
    st.info("Kontribusi Kamu sangat berharga bagi riset FAHAM TEAM. Kamu bisa menutup halaman ini sekarang.")
    st.markdown('<div class="footer">© 2026 FAHAM TEAM - Data Science UIN Raden Mas Said Surakarta.</div>', unsafe_allow_html=True)

# --- HALAMAN LOGIN ---
elif st.session_state.user_data is None:
    st.title("Riset Preferensi Konsumen: Paket Menu Ayam")
    st.markdown("""
    <div class="intro-box">
        <strong>Disusun Oleh FAHAM TEAM:</strong><br>
        Annisa, Luthfiya, Melani, Haya, Ahmad Ruhayani Azis.
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_gate"):
        st.write("Silakan lengkapi identitas untuk memulai:")
        nama = st.text_input("Nama Panggil", placeholder="Tuliskan nama Kamu")
        angkatan = st.selectbox("Angkatan", ["2023", "2024", "2025"], index=None, placeholder="Pilih tahun angkatan")
        nim = st.text_input("3 Angka Terakhir NIM", placeholder="Contoh: 042", max_chars=3)
        
        if st.form_submit_button("Mulai Sesi Pemilihan"):
            if nama.strip() and angkatan and nim.isdigit() and len(nim) == 3:
                st.session_state.user_data = {"nama": nama, "angkatan": angkatan, "nim": nim}
                st.rerun()
            else:
                st.warning("Mohon lengkapi identitas Nama, Angkatan, dan 3 digit NIM.")
    
    st.markdown('<div class="footer">© 2026 FAHAM TEAM</div>', unsafe_allow_html=True)

# --- HALAMAN SESI PEMILIHAN (DENGAN AUTO-SUBMIT) ---
else:
    user = st.session_state.user_data
    current_rank = st.session_state.click_counter
    
    if current_rank <= 12:
        st.title("Pemilihan Preferensi")
        st.markdown(f"""
        <div class="intro-box">
            Status: Menentukan pilihan untuk <strong>Peringkat ke-{current_rank}</strong><br>
            <em>Klik menu dari yang <strong>PALING</strong> Kamu sukai hingga yang paling kurang disukai.</em>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(float(current_rank - 1) / 12)
        
        # Filter menu yang belum dipilih
        remaining = [p for p in st.session_state.profiles if p['label'] not in st.session_state.assigned_ranks]
        
        cols = st.columns(2)
        for idx, p in enumerate(remaining):
            # Ikon adaptif
            icon = "🥩" if p['kat'] == "Dada" else "🍗" if p['kat'] == "Paha" else "🕊️"
            
            with cols[idx % 2]:
                if st.button(f"{icon} {p['label']}", key=f"btn_{p['label']}", use_container_width=True):
                    # Simpan peringkat ke dalam state
                    st.session_state.assigned_ranks[p['label']] = st.session_state.click_counter
                    
                    # LOGIKA AUTO-SUBMIT: Jika ini klik terakhir (ke-12)
                    if st.session_state.click_counter == 12:
                        with st.spinner("Mengirim data secara otomatis..."):
                            success = auto_submit()
                            if success:
                                st.session_state.submitted = True
                                st.rerun()
                            else:
                                st.error("Koneksi terganggu. Data gagal terkirim ke server.")
                    else:
                        st.session_state.click_counter += 1
                        st.rerun()
    
    st.markdown('<div class="footer">© 2026 FAHAM TEAM</div>', unsafe_allow_html=True)
