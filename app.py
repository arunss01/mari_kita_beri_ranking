import streamlit as st
import pandas as pd
import requests

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Riset Paket Makan - FAHAM TEAM", layout="centered", page_icon="🍗")

# --- 2. INITIALIZING SESSION STATE ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

if 'click_counter' not in st.session_state:
    st.session_state.click_counter = 1

if 'assigned_ranks' not in st.session_state:
    st.session_state.assigned_ranks = {}

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

if 'profiles' not in st.session_state:
    # URUTAN PROFIL 1-27 SESUAI GAMBAR
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
        margin-bottom: 10px;
    }
    .guide-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 25px;
        color: #31333F;
    }
    .footer {
        text-align: center;
        color: #888;
        padding: 50px 0 20px 0;
        font-size: 0.8em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNGSI KIRIM DATA (DENGAN KONVERSI SKOR 27-1) ---
def send_to_google_form(nama, angkatan, nim):
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfqFjwF7MgIFpXtk7PrZ6VLRIch6KilFYBc5KekeM2Z__i-GQ/formResponse"
    
    # LOGIKA KONVERSI: Klik 1 -> 27, Klik 2 -> 26, ..., Klik 27 -> 1
    ordered_results = []
    for p in st.session_state.profiles:
        click_order = st.session_state.assigned_ranks.get(p['label'], 27)
        # Rumus: 28 - urutan_klik
        transformed_score = 28 - click_order
        ordered_results.append(str(transformed_score))
    
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

# A. HALAMAN SETELAH SUBMIT (POST-SUBMISSION)
if st.session_state.submitted:
    st.balloons()
    st.title("✅ Data Berhasil Terkirim!")
    st.markdown(f"""
    ### Terima kasih, {st.session_state.user_data['nama']}!
    
    Kontribusi lo sangat berarti buat riset kami. Pilihan yang lo berikan bakal jadi bahan utama 
    buat nemuin kombinasi paket makan paling ideal lewat analisis data yang kami lakukan.
    
    **Apa selanjutnya?**
    Lo bisa menutup halaman ini sekarang. Info lebih lanjut mengenai hasil riset akan 
    kami bagikan setelah seluruh data terkumpul dan diolah.
    
    *Stay curious, stay hungry!*
    """)
    
    st.info("💡 Pilihan lo sudah tersimpan secara otomatis di database pusat FAHAM TEAM.")
    
    st.markdown('<div class="footer">© 2026 FAHAM TEAM. All rights reserved.</div>', unsafe_allow_html=True)

# B. HALAMAN LOGIN (GATE)
elif st.session_state.user_data is None:
    st.title("🍗 Riset Preferensi Paket Makan")
    st.write("Selamat datang! Riset ini dilakukan untuk memetakan paket makan favorit mahasiswa.")
    
    with st.form("login_gate"):
        nama = st.text_input("Nama Panggil", placeholder="Siapa nama lo?")
        angkatan = st.selectbox("Angkatan", ["2023", "2024", "2025"], index=None, placeholder="Pilih tahun...")
        nim = st.text_input("3 Angka Terakhir NIM", placeholder="Contoh: 042", max_chars=3)
        
        if st.form_submit_button("Mulai Pilih Paket"):
            if nama.strip() and angkatan and nim.isdigit() and len(nim) == 3:
                st.session_state.user_data = {"nama": nama, "angkatan": angkatan, "nim": nim}
                st.rerun()
            else:
                st.warning("⚠️ Isi Nama, Angkatan, dan 3 digit NIM dulu ya!")
    
    st.markdown('<div class="footer">© 2026 FAHAM TEAM</div>', unsafe_allow_html=True)

# C. HALAMAN PEMILIHAN
else:
    user = st.session_state.user_data
    current_rank = st.session_state.click_counter
    
    if current_rank <= 27:
        st.title(f"Halo, {user['nama']}! 👋")
        
        st.markdown(f"""
        <div class="guide-box">
            <b>Teknis Pengisian:</b><br>
            • Klik paket makanan mulai dari yang <b>Paling Lo Suka</b> sampai <b>Paling Gak Disuka</b>.<br>
            • Klik pertama akan mendapat skor tertinggi (27), klik terakhir skor terendah (1).<br>
            • Paket yang udah lo klik bakal hilang dari daftar.<br><br>
            🎯 <b>Sekarang pilih paket untuk peringkat ke-{current_rank}</b>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(min(float(current_rank - 1) / 27, 1.0))
        
        remaining = [p for p in st.session_state.profiles if p['label'] not in st.session_state.assigned_ranks]
        cols = st.columns(2)
        for idx, p in enumerate(remaining):
            icon = "🍗" if p['kat'] == "Paha" else "🥩" if p['kat'] == "Dada" else "🕊️"
            with cols[idx % 2]:
                if st.button(f"{icon} {p['label']}", key=f"btn_{p['label']}", use_container_width=True):
                    st.session_state.assigned_ranks[p['label']] = st.session_state.click_counter
                    st.session_state.click_counter += 1
                    st.rerun()
    else:
        # HALAMAN KONFIRMASI SEBELUM KIRIM
        st.success("🏁 Semua paket sudah diurutkan!")
        st.write("Periksa kembali urutan pilihan lo di bawah sebelum mengirim.")
        
        # Mapping untuk tampilan tabel (agar user paham 1st click = Skor 27)
        summary = []
        for i, p in enumerate(st.session_state.profiles):
            click_order = st.session_state.assigned_ranks[p['label']]
            summary.append({
                "Profil": f"Profil_{i+1}",
                "Menu": p['label'],
                "Klik Ke-": click_order,
                "Skor Akhir": 28 - click_order
            })
        
        st.table(pd.DataFrame(summary))

        if st.button("📤 KIRIM DATA KE DATABASE PUSAT", use_container_width=True, type="primary"):
            with st.spinner("Mengirim data..."):
                status = send_to_google_form(user['nama'], user['angkatan'], user['nim'])
                if status == 200:
                    st.session_state.submitted = True
                    st.rerun()
                else:
                    st.error(f"❌ Gagal mengirim. (Status: {status})")

    st.markdown('<div class="footer">© 2026 FAHAM TEAM</div>', unsafe_allow_html=True)
