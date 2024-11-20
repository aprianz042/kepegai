import streamlit as st
import os
import shelve
import google.generativeai as genai
import re
import pymysql
import pandas as pd
import matplotlib.pyplot as plt

from dotenv import load_dotenv
load_dotenv()

debug_mode = False # True / False

db_connection = pymysql.connect(
    host=st.secrets["DB_HOST"],       
    user=st.secrets["DB_USER"],          
    password=st.secrets["DB_GEMBOK"], 
    database=st.secrets["DB_NYA"]) 

TAWA = "🤣"
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"
disclaimer = "⚠ Jawaban ini terbatas pada basis data yang kami miliki !!!"


st.title(BOT_AVATAR+"Asisten Kepegawaian")
st.subheader("Siap Menggantikan Anda yang Useless HaHaHAhA"+TAWA)
client = genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Ensure genai_model is initialized in session state
if "genai_model" not in st.session_state:
    st.session_state["genai_model"] = genai.GenerativeModel('gemini-pro')

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

def read_sql_query(sql,db):
    conn = db_connection
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    for row in rows:
        print(row)
    return rows

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
############################################################

# Load chat history from shelve file
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

# Save chat history to shelve file
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
    if st.button("Delete Chat History"):
        st.session_state.messages = []
        st.session_state.perintah = None
        save_chat_history([])

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":   
        with st.chat_message(message["role"], avatar=USER_AVATAR):
            st.markdown(message["content"])
    else: 
        with st.chat_message(message["role"], avatar=BOT_AVATAR):
            if "respon" in message:
                st.markdown(message["respon"])
            if debug_mode:
                if "qu" in message:
                    st.code(message["qu"], language="sql")
            if "dataframe" in message:
                st.dataframe(message["dataframe"])
            if "figure" in message:
                st.pyplot(message["figure"])
            if "disclaimer" in message:
                st.markdown(message["disclaimer"])
            if "gagal" in message:
                st.error(message["gagal"])

aturan=[
    """
    Anda adalah seorang ahli dalam mengubah perintah berbahasa indonesia menjadi kode query SQL!
    Basis data MySQL nya memiliki tabel bernama pegawai dan mempunyai kolom - nip, nik, kota_lahir, 
    tanggal_lahir, jenis_kelamin, status_pernikahan, status_kepegawaian, agama, 
    alamat, email, no_hp, pangkat, tanggal_sk, tanggal_sk_cpns, jabatan, 
    spesialis, gaji_pokok, grade, pendidikan \n
    \nSebagai contoh,
    \nContoh 1 - Berapa banyak jumlah data pegawai yang ada?,
    perintah SQL yang dihasilkan akan seperti ini SELECT COUNT(*) FROM pegawai;
    \nContoh 2 - Tampilkan data pegawai dengan pendidikan S1?,
    perintah SQL yang dihasilkan akan seperti ini SELECT * FROM pegawai WHERE pendidikan="S1";
    dan juga hasil dari query SQL nya jangan sampai mengandung karakter ``` pada bagian awal dan akhir dari text keluaran

    """
]

aturan_eng = [
    """
    You are an expert in converting Bahasa questions to SQL query!
    The SQL database has the name pegawai and has the following columns - nip, nik, kota_lahir, tanggal_lahir, jenis_kelamin, status_pernikahan, status_kepegawaian, agama, alamat, email, no_hp, pangkat, tanggal_sk, tanggal_sk_cpns, jabatan, spesialis, gaji_pokok, grade, pendidikan\n
    \nFor example,
    \nExample 1 - How many entries of records are present?, 
    the SQL command will be something like this SELECT COUNT(*) FROM pegawai ;
    \nExample 2 - Tell me all the pegawai dengan status Aktif?, 
    the SQL command will be something like this SELECT * FROM pegawai 
    where pendidikan = "S1"; 
    also the sql code should not have ``` in beginning or end and sql word in output

    """
]

umum = [
    """
    Anda seorang ahli dalam bidang kepegawaian aparatur sipil negara indonesia!
    \nContoh 1 - Apa perbedaan PNS dan PPPK?,
    anda akan menjawab seperti ini PNS berstatus sebagai pegawai tetap negara, dengan jaminan pensiun dan berbagai hak lainnya, sedangkan PPPK adalah pegawai pemerintah dengan perjanjian kerja tertentu dan dapat diperpanjang berdasarkan kebutuhan.
    \nContoh 2 - Apa yang dimaksud dengan tugas belajar bagi PNS?,
    anda akan menjawab seperti ini Tugas belajar adalah izin resmi yang biasanya dibiayai atau disponsori oleh pemerintah, sementara izin belajar adalah izin untuk melanjutkan pendidikan secara mandiri di luar jam kerja tanpa pembiayaan dari pemerintah. PNS dengan izin belajar tetap harus melaksanakan tugas hariannya.
    \nDengan menggunakan pengetahuan yang Anda miliki tentang kepegawaian aparatur sipil negara indonesia, jawablah pertanyaan-pertanyaan tersebut dengan cara yang informatif dan mudah dipahami bagi penanya tidak harus terpaku dengan jawaban potensial untuk setiap pertanyaan. 
    Jika ada pertanyaan yang tidak bisa dijawab dapat dialihkan ke CS BKN.
    """
]

def run_task_grafik(question,prompt):
    response=get_gemini_response(question,prompt)
    response = str(response).replace("```", "").replace("sql", "").replace("`", "").replace(";", "").replace("\n", " ")
    print(response)
    query = response  # Ganti dengan query yang sesuai
    try:
        df = pd.read_sql_query(query, db_connection)
        sum_data = len(df)
        exi = 0
        fail = 0
        thres = 5
        while exi == 0:
            if sum_data == 0:
                fail += 1
            else:
                if debug_mode:
                    print(df)
                exi = 1
                stat = "success"
            if fail > thres:
                stat = "fail"
                exi = 1

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

    except pymysql.MySQLError as e:
        #st.subheader(f"Error MySQL terjadi: {e}")
        st.error("Oops! Terjadi kesalahan pada koneksi DB, ulangi kembali atau ganti perintah", icon="🚨")
    except pd.io.sql.DatabaseError as e:
        #st.subheader(f"Error pada query atau database: {e}")
        st.error("Oops! Terjadi kesalahan query, ulangi kembali atau ganti perintah", icon="🚨")
    except Exception as e:
        #st.subheader(f"Terjadi kesalahan: {e}")
        st.error("Oops! Terjadi kesalahan, ulangi kembali atau ganti perintah", icon="🚨")
    finally:
        db_connection.close()

def run_task_khusus(question,prompt):
    response=get_gemini_response(question,prompt)
    response = str(response).replace("```", "").replace("sql", "").replace("`", "").replace(";", "").replace("\n", " ")
    print(response)
    query = response  
    try:
        df = pd.read_sql_query(query, db_connection)
        sum_data = len(df)
        exi = 0
        fail = 0
        thres = 5
        while exi == 0:
            if sum_data == 0:
                fail += 1
            else:
                if debug_mode:
                    print(df)
                exi = 1
                stat = "success"
            if fail > thres:
                stat = "fail"
                exi = 1
        return query, df, disclaimer, stat
    
    except pymysql.MySQLError as e:
        st.error("Oops! Terjadi kesalahan pada koneksi DB, ulangi kembali atau ganti perintah", icon="🚨")
    except pd.io.sql.DatabaseError as e:
        st.error("Oops! Terjadi kesalahan query, ulangi kembali atau ganti perintah", icon="🚨")
    except Exception as e:
        st.error("Oops! Terjadi kesalahan, ulangi kembali atau ganti perintah", icon="🚨")
    finally:
        db_connection.close()

def run_task_umum(question,prompt):
    response=get_gemini_response(question,prompt)
    return response

def cek_kata_terkandung(kalimat, kata_list):
    pattern = "|".join(kata_list)  # Gabungkan kata dengan operator OR
    hasil = re.search(pattern, kalimat)  # Cari salah satu kata
    return bool(hasil)

# Main chat interface
def eksekusi_utama(prompt):
    st.session_state.ulangi = False
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    p_khusus = ["data pegawai", "tampilkan", "buatkan", "siapa pegawai", "siapa saja", "berapa jumlah pegawai", 
    "siapa pegawai yang", "sebutkan pegawai yang"]
    p_grafik = ["buatkan grafik", "grafik"]

    if cek_kata_terkandung(prompt, p_grafik):
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
                    st.error("Siap Salah !!!, saya belum bisa menjawabnya, saya akan belajar lebih giat lagi")
            if debug_mode:
                st.session_state.messages.append({"role": "assistant", "content": prompt, "qu": q, "dataframe": d, "figure": fi, "disclaimer": disc})
            else:
                if s == "success":
                    st.session_state.messages.append({"role": "assistant", "content": prompt, "dataframe": d, "figure": fi, "disclaimer": disc})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": prompt, "gagal": "Sistem Gagal Menjawab!"})
        except TypeError as e:
            pass
            

    elif cek_kata_terkandung(prompt, p_khusus):
        try:
            q,d,disc,s = run_task_khusus(prompt, aturan)
            with st.chat_message("assistant", avatar=BOT_AVATAR):
                if debug_mode:
                    st.code(q, language="sql")
                if s == "success":
                    st.dataframe(d)
                    st.markdown(disc)
                else:
                    st.error("Siap Salah !!!, saya belum bisa menjawabnya, saya akan belajar lebih giat lagi")
            if debug_mode:
                st.session_state.messages.append({"role": "assistant", "content": prompt, "qu": q, "dataframe": d, "disclaimer": disc})
            else:
                if s == "success":
                    st.session_state.messages.append({"role": "assistant", "content": prompt, "dataframe": d, "disclaimer": disc})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": prompt, "gagal": "Sistem Gagal Menjawab!"})
        except TypeError as e:
            pass
        
    else:
        q = run_task_umum(prompt, umum)
        with st.chat_message("assistant", avatar=BOT_AVATAR):
            st.markdown(q)
        st.session_state.messages.append({"role": "assistant", "content": prompt, "respon": q})

prompt = st.chat_input("Contoh perintah : Tampilkan data ... / Buatkan grafik ... / Siapa pegawai yang ... / dll ")
if prompt:
    st.session_state.perintah = prompt
    eksekusi_utama(prompt)    

if st.session_state.ulangi:
    #print(st.session_state.perintah)
    eksekusi_utama(st.session_state.perintah)

if st.session_state.perintah is not None:
    if st.button("Jika jawaban tidak sesuai, klik disini untuk mengulangi !"):
        st.session_state.ulangi = True

save_chat_history(st.session_state.messages)
