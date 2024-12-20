from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.pipeline import Pipeline
import pandas as pd
import streamlit as st
import joblib

st.title('Klasifikasi Perintah')
st.markdown('''ChatBot kepegawaian ini memiliki 4 jenis task.
            \n\nPertama adalah perintah umum,
            yaitu menjawab pertanyaan umum seputar kepegawain ASN Indonesia yang diterjemahkan ke Prompt Gemini.
            \nKedua adalah perintah khusus, yaitu menerjemahkan perintah text menjadi Query SQL yang akan dilanjutkan 
            dengan menampilkan data sesuai Query SQL tersebut dan memberikan analisis singkat terhadap data yang 
            ditampilkan. Data hasil perintah ini bersumber pada data instansi yang terbatas.
            \nKetiga adalah perintah membuat grafik. Mirip dengan perintah khusus namun dengan tambahan pembuatan 
            grafik otomatis memanfaatkan data yang dihasilkan Query SQL.
            \nKeempat adalah perintah membuat grafik dengan Prompt Gemini. Mirip dengan task ketiga, namun semuanya 
            dieksekusi penuh oleh mesin Gemini
            ''')

st.subheader('''Semua perintah akan diklasifikan terlebih dahulu terhadap 4 task di atas dengan metode KNN''', divider=True)

st.write("Berikut dataset yang dipakai untuk dilatih dengan metode KNN")

df = pd.read_csv("master_datasetknn.csv")
kalimat = df['text'].tolist()
label = df['label'].tolist()
st.dataframe(df)

st.subheader('''Data Preparation''', divider=True)
#cek ukuran data
ukuran_data = f"Ukuran datasetnya adalah : {df.shape}"
st.code(ukuran_data, language="python")

# Memeriksa apakah ada nilai null
has_null = df.isnull().any().any()
data_null = f"Terdapat data null : {has_null}"
st.code(data_null, language="python")

#hapus data nan kalau ada
df = df.dropna()
st.code("#eksekusi\ndf = df.dropna()", language="python")

#lihat sebaran data
df['label'].value_counts()

X = kalimat
y = label

st.subheader('''Split Train 80% & Test 20%''', divider=True)
# Membagi data menjadi data latih dan uji
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
st.code("train_test_split(X, y, test_size=0.2, random_state=42)", language="python")

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),  # TF-IDF untuk ekstraksi fitur
    ('knn', KNeighborsClassifier(n_neighbors=3))  # KNN untuk klasifikasi
])
pipeline.fit(X_train, y_train)

st.subheader('''Train & Fit''', divider=True)
st.image('model.jpg')

# Prediksi
y_pred = pipeline.predict(X_test)

# Evaluasi
st.subheader('''Evaluasi''', divider=True)
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average=None)
precision = [f"{a:.2f}" for a in precision]
recall = recall_score(y_test, y_pred, average=None)
recall = [f"{b:.2f}" for b in recall]
f1 = f1_score(y_test, y_pred, average=None)
f1 = [f"{c:.2f}" for c in f1]


st.code(f"Accuracy : {accuracy:.2f}", language="python")
st.code(f"Precision : {precision}", language="python")
st.code(f"Recall : {recall}", language="python")
st.code(f"F1 : {f1}", language="python")

#st.code(f'''Accuracy : {accuracy:.2f} \n''', language="python")
####################################################################
# Simpan pipeline ke file
#joblib.dump(pipeline, 'tfidf_knn_pipeline.pkl')
#print("Pipeline telah disimpan ke file 'tfidf_knn_pipeline.pkl'.")

# eksekusi
#loaded_pipeline = joblib.load('tfidf_knn_pipeline.pkl')
#new_texts = ["buatkan grafik data pegawai berdasarkan status pernikahan"]
#predictions = loaded_pipeline.predict(new_texts)
#print(predictions[0])
