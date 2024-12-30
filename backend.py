import os
import pymysql
import streamlit as st
import pandas as pd

#host=os.getenv("DB_HOST")       
#user=os.getenv("DB_USER")       
#password=os.getenv("DB_GEMBOK")   
#database=os.getenv("DB_NYA")

host=st.secrets["DB_HOST"]       
user=st.secrets["DB_USER"]          
password=st.secrets["DB_GEMBOK"] 
database=st.secrets["DB_NYA"]


conn = pymysql.connect(host=host, user=user, password=password, database=database)

st.title("Main Back-end")

st.subheader("**Arsitektur Sistem**", divider=True)
st.image("arsitektur_trans.png", use_container_width=True)
st.markdown(""" - ***Database*** menggunakan ***MySQL***
            \n- ***Model Gemini*** menggunakan ***gemini-pro*** 
            \n- ***UX/UI*** menggunakan ***Streamlit***
            \n- ***Back-End*** menggunakan ***Python 3.11.7***
            \n- ***Grafik*** menggunakan ***Libs Matplotlib & Seaborn***
            """)

st.subheader("**Daftar Tabel Database**", divider=True)

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
    gab = f"- Tabel : {table_name} ({text})"
    st.subheader(f"*{table_name}*")
    st.success(f"*{text}*")
    hasil.append(gab)
    kolom = []


prompt_db = '\n'.join([f"{item}" for item in hasil])

for_k = []
for fk in foreign_keys:
    for_k.append(f"- {fk[0]}({fk[1]}) REFERENCES {fk[2]}({fk[3]})")

prompt_fk = '\n'.join([f"{item}" for item in for_k])
conn.close()

# Streamlit UI
st.subheader("**Foreign Key**", divider=True)
st.warning(prompt_fk)

aturan = f"""
    Tugas:
    Tuliskan query SQL menggunakan JOIN untuk mendapatkan hasil sesuai instruksi.

    \nSkema Database: 
    \n{prompt_db}

    \nForeign Key:
    \n{prompt_fk}

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

st.subheader("**Prompt Engineering**", divider=True)
st.error(aturan)

st.subheader("**Dataset**", divider=True)
df = pd.read_csv('rouge.csv')
st.markdown(f'''Dataset didapatkan dengan mencoba pertanyaan yang ada pada kolom ***questions*** 
        dengan aturan ***prompt*** pada poin 3 dan hasilnya adalah pada kolom ***query***. 
        Sedangkan kolom ***references*** adalah kumpulan query yang semestinya, 
        dan dibuat berdasarkan pengetahuan ahli''')
st.dataframe(df)

dfr = df

st.code(f'''#cek ukuran data\ndfr.shape\n(86, 3)''', 
        language="python")

st.code(f'''#Memeriksa apakah ada nilai null\nhas_null = dfr.isnull().any().any()\nhas_null\nFalse''', 
        language="python")

#hapus data nan kalau ada
dfr = dfr.dropna()
#dfr.shape
st.code(f'''#hapus data nan kalau ada\ndfr = dfr.dropna()\ndfr.shape\n(86, 3)''', 
        language="python")

st.code(f'''# Apakah ada duplikat di DataFrame?\nada_duplikat = dfr.duplicated().any()\nada_duplikat\nFalse''', 
        language="python")

#hapus duplikat jika ada
dfr = dfr.drop_duplicates()

st.code(f'''#hapus duplikat jika ada\ndfr = dfr.drop_duplicates()\ndfr.shape\n(86, 3)''', 
        language="python")

st.subheader("**6. Evaluasi Prompt Engineering**")
st.markdown(f'''Evaluasi aturan ***prompt engineering*** dilakukan menggunakan ***ROUGE***, 
            dimana ROUGE (Recall-Oriented Understudy for Gisting Evaluation) adalah sebuah metrik evaluasi 
            yang digunakan untuk mengukur kualitas hasil summarization (peringkasan teks) atau hasil 
            dari model NLP lainnya, terutama untuk tugas seperti machine translation atau text generation. 
            ROUGE menghitung kemiripan antara teks hasil peringkasan/model dengan teks referensi (biasanya buatan manusia). 
            ROUGE berfokus pada seberapa baik elemen-elemen penting dari teks referensi berhasil dihasilkan kembali oleh model.''')

from rouge_score import rouge_scorer
import numpy as np

# Inisialisasi ROUGE scorer
scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

# Variabel untuk menyimpan skor
rouge1_scores, rouge2_scores, rougeL_scores = [], [], []

# Hitung skor untuk setiap pasangan teks
for _, row in df.iterrows():
    generated_text = row['query']
    reference_text = row['reference']

    scores = scorer.score(reference_text, generated_text)

    rouge1_scores.append(scores['rouge1'].fmeasure)
    rouge2_scores.append(scores['rouge2'].fmeasure)
    rougeL_scores.append(scores['rougeL'].fmeasure)

# Hitung rata-rata skor
avg_rouge1 = np.mean(rouge1_scores)
avg_rouge2 = np.mean(rouge2_scores)
avg_rougeL = np.mean(rougeL_scores)

# Tampilkan hasil
st.markdown("***Hasil Evaluasi:***")
st.code(f"ROUGE-1: {avg_rouge1:.2f}", language="python")
st.code(f"ROUGE-2: {avg_rouge2:.2f}", language="python")
st.code(f"ROUGE-L: {avg_rougeL:.2f}", language="python")

st.markdown(f'''***dimana :***
            \n- ROUGE-1: Mengukur kemiripan pada tingkat unigram (kata tunggal).
            \n- ROUGE-2: Mengukur kemiripan pada tingkat bigram (dua kata berurutan).
            \n- ROUGE-L (Longest Common Subsequence): Mengukur kesamaan berdasarkan subsekuensi kata terpanjang yang berurutan (longest common subsequence). 
            ROUGE-L menangkap urutan kata yang dipertahankan antara keluaran model dan referensi.''')
