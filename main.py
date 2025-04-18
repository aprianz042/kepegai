import streamlit as st
import os
import shelve
import google.generativeai as genai
import re
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import warnings
import joblib
from dotenv import load_dotenv

# Menonaktifkan semua warning
warnings.filterwarnings("ignore")
load_dotenv()

with st.sidebar:
    pilihan = st.sidebar.radio(
    "Debug Mode:",
    options=[False, True])

    debug_mode = pilihan
    status_debug = f"Debug Mode: {debug_mode}" 
    st.code(status_debug, language="python")

############################# Set Kredensial #############################
host=st.secrets["DB_HOST"]       
user=st.secrets["DB_USER"]          
password=st.secrets["DB_GEMBOK"] 
database=st.secrets["DB_NYA"]
gem_api=st.secrets["GOOGLE_API_KEY"]

#host=os.getenv("DB_HOST")       
#user=os.getenv("DB_USER")       
#password=os.getenv("DB_GEMBOK")   
#database=os.getenv("DB_NYA")
#gem_api=os.getenv("GOOGLE_API_KEY")
############################################################################

############################# READ STRUKTUR DB #############################
conn = pymysql.connect(host=host, user=user, password=password, database=database)
cursor = conn.cursor()
cp = conn.cursor()
cursor.execute("SHOW TABLES;")
cp.execute(f"""
SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = '{database}' AND REFERENCED_TABLE_NAME IS NOT NULL;
""")
tables = cursor.fetchall()
foreign_keys = cp.fetchall()
hasil = []
kolom = []
for table in tables:
    table_name = table[0]
    cursor.execute(f"DESCRIBE {table_name};")
    columns = cursor.fetchall()
    for column in columns:
        #print(f"{column[0]},")
        kolom.append(column[0])
    text = ', '.join(kolom)
    gab = f"- Tabel: {table_name} ({text})"
    hasil.append(gab)
    kolom = []
prompt_db = '\n'.join([f"{item}" for item in hasil])
for_k = []
for fk in foreign_keys:
    for_k.append(f"- {fk[0]}({fk[1]}) REFERENCES {fk[2]}({fk[3]})")
prompt_fk = '\n'.join([f"{item}" for item in for_k])
conn.close()
#########################################################################

############################# Setting Engine #############################
setUP = f"mysql+pymysql://{user}:{password}@{host}/{database}"
db_connection = create_engine(setUP)
client = genai.configure(api_key=gem_api)
#########################################################################

############################# Variabel Header #############################
TAWA = "🤣"
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"
disclaimer = "⚠ Jawaban ini terbatas pada basis data yang kami miliki !!!"
st.title(BOT_AVATAR+"Asisten Kepegawaian")
st.write("Siap Perintah")
#########################################################################

############################# Fungsi Utama #############################
if "genai_model" not in st.session_state:
    st.session_state["genai_model"] = genai.GenerativeModel('gemini-2.0-flash')

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content([prompt[0], question])
    return response.text

def hapus_kata(kalimat, kata_dihapus):
    pola = r'\b(?:' + '|'.join(map(re.escape, kata_dihapus)) + r')\b'
    return re.sub(pola, '', kalimat, flags=re.IGNORECASE).strip()

def grafik_bar(a,b,judul,kategori):
    panjang_data = len(a)

    warna = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    bar_label = []
    bar_colors = []
    
    for i in range(panjang_data):
        bar_label.append(warna[i])
        bar_colors.append('tab:'+warna[i])

    #st.write("Grafik "+judul)
    fig, ax = plt.subplots()
    bar_container = ax.bar(a, b, label=a, color=bar_colors)
    #ax.bar(a, b, label=a, color=bar_colors)
    ax.set_ylabel('Jumlah Pegawai')
    ax.set_title(judul)
    ax.bar_label(bar_container, fmt='{:,.0f}')
    ax.legend(title=kategori)
    #st.pyplot(fig)
    return fig

def grafik_pie(a,b,judul):
    #st.write("Grafik "+judul)
    fig, ax = plt.subplots()
    ax.pie(b, labels=a, autopct='%1.1f%%')
    #st.pyplot(fig)
    return fig

def respon(question,prompt):
    response=get_gemini_response(question,prompt)
    response = str(response).replace("```", "").replace("sql", "").replace("`", "").replace(";", "").replace("\n", " ").replace("   ", " ")
    if debug_mode:
        print(response)
    return response

def clean_code(kode):
    kode = str(kode).replace("**Kode Python:**", "").replace("```python", "").replace("```", "")
    return kode

def run_task_grafik(question,prompt):
    if debug_mode:
        st.success("perintah grafik")
    query = respon(question,prompt)  
    try:
        df = pd.read_sql(query, db_connection)
        sum_data = len(df)
        if sum_data == 0:
            stat = "fail"
            graf = "None"
            return query, df, graf, disclaimer, stat
        else:
            stat = "success"

            header = df.columns.tolist()
            x = header[0]
            y = header[1]

            # Membuat DataFrame contoh
            if df[x].dtypes == 'int64':
                a = df[y].tolist()
                b = df[x].tolist()
                kategori = y
            else:        
                a = df[x].tolist()
                b = df[y].tolist()
                kategori = x

            panjang_data = len(a)

            # Menampilkan judul
            kalimat = question
            filter = ["tampilkan", "buatkan", "buat", "coba", "apa", "bagaimana", "gimana", "mengapa", "dimana", "grafik"]
            judul = hapus_kata(kalimat, filter)

            if panjang_data <= 10:
                graf = grafik_bar(a,b,judul,kategori)
            else:
                graf = grafik_pie(a,b,judul)
            return query, df, graf, disclaimer, stat
    except Exception as e:
        st.markdown("Oops! Terjadi kesalahan, ulangi kembali atau ganti perintah", icon="🚨")

def run_task_khusus(question,prompt):
    if debug_mode:
        st.success("perintah khusus")
    query = respon(question,prompt)
    try:
        df = pd.read_sql(query, db_connection)
        #df = df.set_index(pd.RangeIndex(start=1, stop=len(df)+1, step=1))
        sum_data = len(df)
        
        if debug_mode:
            print(df)
        
        if sum_data == 0:
            stat = 0
            return query, df, disclaimer, stat, stat
        else:
            stat = 1
            if sum_data == 1:
                aturan = [question+""" ,\nberdasarkan dataframenya berikan analisis datanya secara singkat maksimal dua paragraf
                          dalam konteks kepegawaian ASN Indonesia
                          dan jangan tampilkan data dalam bentuk tabel."""]
                text = """Dataframe : """+df.to_string()
                hasil = get_gemini_response(text, aturan)
            else:
            #    aturan = [question+""" ,\nberdasarkan dataframenya berikan analisis datanya maksimal satu paragraf 
            #              dengan konteks kepegawaian ASN Indonesia
            #              dan jangan tampilkan data dalam bentuk tabel."""]
                hasil = "🙏"
            return query, df, disclaimer, stat, hasil
    except Exception as e:
        st.markdown("Oops! Terjadi kesalahan, ulangi kembali atau ganti perintah", icon="🚨")    

def run_task_grafik_gem(question,prompt):
    if debug_mode:
        st.success("perintah grafik gemini")
    filter = ["dengan", "gemini", "dengan gemini"]
    question = hapus_kata(question, filter)
    query = respon(question,prompt)
    try:
        df = pd.read_sql(query, db_connection)
        df = df.set_index(pd.RangeIndex(start=1, stop=len(df)+1, step=1))
        sum_data = len(df)
        if debug_mode:
            print(df)
    
        if sum_data == 0:
            stat = "fail"
            return query, df, disclaimer, stat, stat
        else:
            stat = "success"
            aturan = [question+""" ,\ndataframenya jadikan bahan grafik lalu buatkan satu kode python untuk membuat grafiknya dengan matplotlib fig dan tampilkan fig dengan lib streamlit,
                        \nhasilnya hanya kodenya saja tanpa mengandung judul dan karakter ``` pada bagian awal dan akhir dari kode!
                      """]
            text = """Dataframe : """+df.to_string()
            hasil = get_gemini_response(text, aturan)
            return query, df, disclaimer, stat, hasil
    except Exception as e:
        st.markdown("Oops! Terjadi kesalahan, ulangi kembali atau ganti perintah", icon="🚨")  

def run_task_umum(question,prompt):
    if debug_mode:
        st.success("perintah umum")
    response=get_gemini_response(question,prompt)
    return response

def cek_frasa(kalimat, frasa_list):
    #pola = "|".join(frasa_list)
    #pola = [frasa for frasa in frasa_list if frasa.lower() in kalimat.lower()]
    pola = [frasa for frasa in frasa_list if frasa and frasa.lower() in kalimat.lower()]
    return pola

def klasifikasi_perintah(perintah):
    loaded_knn = joblib.load('knn_model.pkl')
    loaded_vectorizer = joblib.load('tfidf_vectorizer.pkl')
    new_X_tfidf = loaded_vectorizer.transform([perintah])
    predictions = loaded_knn.predict(new_X_tfidf)
    if debug_mode:
        print(predictions[0])
    return predictions[0]

def cek_perintah(kalimat, kata_list):
    hasil = cek_frasa(kalimat, kata_list)
    return bool(hasil)

def kesalahan():
    st.session_state.messages.append({"role": "assistant", "content": prompt, "gagal": "Sistem Gagal Menjawab!"})
#########################################################################


############################# Fungsi UX UI Chat #############################
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

if "ulangi" not in st.session_state:
    st.session_state.ulangi = False

if "perintah" not in st.session_state:
    st.session_state.perintah = None

if "masalah" not in st.session_state:
    st.session_state.masalah = False

# Sidebar with a button to delete chat history
with st.sidebar:
    try:
        if st.button("Reset"):
            st.session_state.messages = []
            st.session_state.perintah = None
            save_chat_history([])
    except Exception as e:
        st.error("Terjadi kesalahan !!!, Klik tombolnya kembali")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":   
        with st.chat_message(message["role"], avatar=USER_AVATAR):
            st.success(message["content"])
    else: 
        with st.chat_message(message["role"], avatar=BOT_AVATAR):
            if "respon" in message:
                st.markdown(message["respon"])
            if debug_mode:
                if "qu" in message:
                    st.code(message["qu"], language="sql")
            if "dataframe" in message:
                st.dataframe(message["dataframe"])
            if debug_mode:
                if "kode" in message:
                    st.code(message["kode"], language="python")
            if "limit" in message:
                st.markdown(message["limit"])
            if "jawaban_t" in message:
                st.markdown(message["jawaban_t"])
            if "figure" in message:
                st.pyplot(message["figure"])
            if "disclaimer" in message:
                st.markdown(message["disclaimer"])
            if "gagal" in message:
                st.error(message["gagal"])
#########################################################################

############################# Prompt Engineering #############################
aturan = [
    f"""
    Tugas:
    Tuliskan query SQL menggunakan JOIN untuk mendapatkan hasil sesuai instruksi.

    \nSkema Database:
    {prompt_db}

    \nForeign Key:
    {prompt_fk}
    
    \nSesuaikan instruksi dengan melakukan sinonim field sesuai dengan skema database di atas, 
    \nContohnya: siapa saja pegawai yang belum kawin, hasilnya menjadi siapa saja pegawai yang belum menikah

    Contoh instruksi:
    \n- Tampilkan data pegawai yang sedang Tugas Belajar?,
    Hasilnya akan seperti SELECT p.nip, p.nama tb.perguruan_tinggi tb.pembiayaan FROM pegawai p JOIN tugas_belajar tb ON p.id = tb.id_pegawai WHERE tb.status = 'berlangsung';
    \n- Tampilkan data pegawai yang sedang Cuti berserta alasannya?,
    Hasilnya akan seperti SELECT p.nip, p.nama c.tanggal_mulai c.lama_hari c.alasan FROM pegawai p JOIN cuti c ON p.id = c.id_pegawai WHERE c.status = 'berlangsung';
    \n- Tampilkan data pegawai yang pernah cuti melahirkan?,
    Hasilnya akan seperti SELECT p.nip, p.nama c.tanggal_mulai c.lama_hari c.alasan FROM pegawai p JOIN cuti c ON p.id = c.id_pegawai WHERE c.alasan = 'Melahirkan';
    \n- Tampilkan jumlah pegawai berdasarkan pendidikan?,
    Hasilnya akan seperti SELECT pendidikan, COUNT(*) AS jumlah_pegawai FROM pegawai GROUP BY pendidikan ORDER BY pendidikan ASC;
    \n- Tampilkan pegawai yang berumur di atas 40 tahun?,
    Hasilnya akan seperti SELECT nip, nama, tanggal_lahir, TIMESTAMPDIFF(YEAR, tanggal_lahir, CURDATE()) AS umur FROM pegawai WHERE TIMESTAMPDIFF(YEAR, tanggal_lahir, CURDATE()) > 40;
    \n- Buatkan grafik pegawai berdasarkan jenis kelamin?,
    Hasilnya akan seperti SELECT jenis_kelamin, COUNT(*) AS jumlah_pegawai FROM pegawai GROUP BY jenis_kelamin ORDER BY jumlah_pegawai DESC;
    \n- Buatkan grafik pegawai berdasarkan umur?,
    Hasilnya akan seperti 
    SELECT 
        CASE 
            WHEN TIMESTAMPDIFF(YEAR, tanggal_lahir, CURDATE()) < 30 THEN 'Di bawah 30 tahun'
            WHEN TIMESTAMPDIFF(YEAR, tanggal_lahir, CURDATE()) BETWEEN 30 AND 39 THEN '30-39 tahun'
            WHEN TIMESTAMPDIFF(YEAR, tanggal_lahir, CURDATE()) BETWEEN 40 AND 49 THEN '40-49 tahun'
            ELSE '50 tahun ke atas'
        END AS kategori_umur,
        COUNT(*) AS jumlah_pegawai
    FROM pegawai
    GROUP BY kategori_umur
    ORDER BY kategori_umur;
    \n- Pegawai yang telat hari ini?,
    hasilnya akan seperti SELECT p.nip, p.nama, k.waktu FROM pegawai AS p JOIN kehadiran AS k ON p.id = k.id_pegawai WHERE k.tanggal = CURDATE() AND k.status > 'terlambat';
    \n- tampilkan data kehadiran pegawai?,
    hasilnya akan seperti SELECT p.nip, p.nama, k.waktu FROM pegawai AS p JOIN kehadiran AS k ON p.id = k.id_pegawai;
    \n- Siapa pegawai yang berumur paling tua,
    hasilnya akan seperti SELECT nip, nama, tanggal_lahir, TIMESTAMPDIFF(YEAR, tanggal_lahir, CURDATE()) AS umur FROM pegawai ORDER BY umur DESC LIMIT 1;
    \n- Siapa pegawai yang berumur 30 tahun
    hasilnya akan seperti SELECT nip, nama, tanggal_lahir, TIMESTAMPDIFF(YEAR, tanggal_lahir, CURDATE()) AS umur FROM pegawai WHERE TIMESTAMPDIFF(YEAR, tanggal_lahir, CURDATE()) = 30 ORDER BY tanggal_lahir DESC;
    
    \nHasil dari query SQL nya jangan sampai mengandung karakter ``` pada bagian awal dan akhir dari text keluaran
    """
]

umum = [
    """
    Tugas:
    Jawablah pertanyaan tersebut dalam konteks ASN Indonesia dengan singkat namun tetap informatif dan mudah dipahami, 
    Jika ada pertanyaan yang tidak bisa dijawab dapat dialihkan ke CS BKN.
    """
]
#########################################################################

############################# Fungsi Eksekusi Utama #############################
def eksekusi_utama(prompt):
    st.session_state.ulangi = False
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.success(prompt)

    p_khusus = ["data pegawai", "tampilkan", "buatkan", "siapa pegawai", "siapa saja", "berapa jumlah pegawai", 
    "siapa pegawai yang", "sebutkan pegawai yang"]
    p_grafik = ["buatkan grafik", "grafik"]
    p_gem_grafik = ["dengan gemini"]

    perintah = klasifikasi_perintah(prompt)

    #if cek_perintah(prompt, p_gem_grafik):
    if perintah == 'gemini':
        try:
            q,d,disc,s,hasil = run_task_grafik_gem(prompt, aturan)
            with st.chat_message("assistant", avatar=BOT_AVATAR):
                if debug_mode:
                    st.code(q, language="sql")
                if s == "success":
                    st.dataframe(d)
                    output = """st.session_state.messages.append({"role": "assistant", "content": prompt, "qu": q, "dataframe": d, "kode": hasil, "figure": fig, "disclaimer": disc})"""
                    hasil = hasil +"\n"+ output
                    hasil = clean_code(hasil)
                    if debug_mode:
                        st.code(hasil, language="python")
                    try:
                        exec(hasil)
                    except Exception as e:
                        st.error(" Ada kesalahan pada kode dan tidak bisa dieksekusi", icon="🙏")
                    st.markdown(disc)
                    limit = "🙏 Maaf storage terbatas sehingga hasil grafik dari gemini tidak bisa ditampilkan"
                    #st.session_state.messages.append({"role": "assistant", "content": prompt, "qu": q, "dataframe": d, "kode": hasil, "limit": limit,"disclaimer": disc})
                else:
                    st.error("Siap Salah !!!, saya belum bisa menjawabnya, saya akan belajar lebih giat lagi", icon="🙏")  
                    kesalahan()
        except TypeError as e:
            st.error("Siap salah! Saya melakukan kesalahan, mohon izin untuk mengulangi kembali atau ganti perintah", icon="🙏")
            kesalahan()

    #elif cek_perintah(prompt, p_grafik):
    elif perintah == 'grafik':
        try:
            q,d,fi,disc,s = run_task_grafik(prompt, aturan)
            with st.chat_message("assistant", avatar=BOT_AVATAR):
                if debug_mode:
                    st.code(q, language="sql")
                if s == "success":
                    st.dataframe(d)
                    st.pyplot(fi)
                    st.markdown(disc)
                else:
                    st.error("Siap Salah !!!, saya belum bisa menjawabnya, saya akan belajar lebih giat lagi", icon="🙏")
                    kesalahan()
            if debug_mode:
                st.session_state.messages.append({"role": "assistant", "content": prompt, "qu": q, "dataframe": d, "figure": fi, "disclaimer": disc})
            else:
                if s == "success":
                    st.session_state.messages.append({"role": "assistant", "content": prompt, "dataframe": d, "figure": fi, "disclaimer": disc})
        except TypeError as e:
            st.error("Ada kesalahan, mohon izin untuk mengulangi kembali atau ganti perintah", icon="🙏")
            kesalahan()
            
    #elif cek_perintah(prompt, p_khusus):
    elif perintah == 'khusus':
        try:
            q,d,disc,stat,hasil = run_task_khusus(prompt, aturan)
            with st.chat_message("assistant", avatar=BOT_AVATAR):
                if debug_mode:
                    st.code(q, language="sql")
                if stat == 1:
                    st.dataframe(d)
                    st.markdown(hasil)
                    st.markdown(disc)
                    st.session_state.messages.append({"role": "assistant", "content": prompt, "qu": q, "dataframe": d, "jawaban_t": hasil, "disclaimer": disc})
                else:
                    st.error("Siap Salah !!!, saya belum bisa menjawabnya, saya akan belajar lebih giat lagi", icon="🙏")  
                    kesalahan()
        except TypeError as e:
            st.error("Ada kesalahan, mohon izin untuk mengulangi kembali atau ganti perintah", icon="🙏")
            kesalahan()
    else:
        q = run_task_umum(prompt, umum)
        with st.chat_message("assistant", avatar=BOT_AVATAR):
            st.markdown(q)
        st.session_state.messages.append({"role": "assistant", "content": prompt, "respon": q})
############################################################################################

###################### Fungsi Streamlit yang dijalankan pertama kali ######################
prompt = st.chat_input("Contoh perintah : Tampilkan data ... / Buatkan grafik ... dll ")
if prompt:
    st.session_state.perintah = prompt
    eksekusi_utama(prompt)    

if st.session_state.ulangi:
    #print(st.session_state.perintah)
    eksekusi_utama(st.session_state.perintah)

if st.session_state.perintah is not None:
    if st.button("Jika jawaban tidak sesuai, klik disini untuk mengulangi !"):
        st.session_state.ulangi = True

#save_chat_history(st.session_state.messages)
############################################################################################
