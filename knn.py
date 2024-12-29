from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.pipeline import Pipeline
import seaborn as sns
import pandas as pd
import streamlit as st
import joblib
import numpy as np

st.title('Klasifikasi Perintah')
st.markdown('''ChatBot kepegawaian ini memiliki 4 jenis task.
            \n\n- **Pertama** adalah ***perintah umum***,
            yaitu menjawab pertanyaan umum seputar kepegawain ASN Indonesia yang diterjemahkan ke Prompt Gemini.
            \n- **Kedua** adalah ***perintah khusus***, yaitu menerjemahkan perintah text menjadi Query SQL yang akan dilanjutkan 
            dengan menampilkan data sesuai Query SQL tersebut dan memberikan analisis singkat terhadap data yang 
            ditampilkan. Data hasil perintah ini bersumber pada data instansi yang terbatas.
            \n- **Ketiga** adalah ***perintah membuat grafik***. Mirip dengan perintah khusus namun dengan tambahan pembuatan 
            grafik otomatis memanfaatkan data yang dihasilkan Query SQL.
            \n- **Keempat** adalah ***perintah membuat grafik dengan Prompt Gemini***. Mirip dengan task ketiga, namun semuanya 
            dieksekusi penuh oleh mesin Gemini
            ''')

st.subheader('''Semua perintah akan diklasifikan terlebih dahulu terhadap 4 task di atas dengan metode KNN''', divider=True)

st.write("Berikut dataset yang dipakai untuk dilatih dengan metode KNN")

df = pd.read_csv("master_datasetknn_kotor.csv")

st.dataframe(df)

dfr=df

st.subheader('''Data Preparation''', divider=True)
#cek ukuran data
ukuran_data = f"Ukuran datasetnya adalah : {dfr.shape}"
st.code(ukuran_data, language="python")

# Memeriksa apakah ada nilai null
has_null = dfr.isnull().any().any()
data_null = f"Terdapat data null : {has_null}"
st.code(data_null, language="python")

#hapus data nan kalau ada
dfr = dfr.dropna()
st.code("#eksekusi\ndf = df.dropna()\ndf.shape", language="python")
ukuran_data = f"Ukuran datasetnya menjadi : {dfr.shape}"
st.code(ukuran_data, language="python")

# Memeriksa apakah masih ada nilai null
has_null = dfr.isnull().any().any()
st.code("# Memeriksa apakah masih ada nilai null\nhas_null = df.isnull().any().any()", language="python")
data_kosong = f"Masih ada data kosong : {has_null}"
st.code(data_kosong, language="python")

# Apakah ada duplikat di DataFrame?
st.code("# Apakah ada duplikat di DataFrame?\nada_duplikat = df.duplicated().any()", language="python")
ada_duplikat = dfr.duplicated().any()
dupli = f"Ada duplikat: {ada_duplikat}"
st.code(dupli, language="python")

#hapus duplikat
dfr = dfr.drop_duplicates()
st.code("# hapus duplikat\ndf = df.drop_duplicates()\ndf.shape", 
        language="python")
st.code(dfr.shape, language="python")

kalimat = dfr['text'].tolist()
label = dfr['label'].tolist()

#lihat sebaran data
value_counts = dfr['label'].value_counts()

import matplotlib.pyplot as plt

# Memisahkan menjadi dua list
labels = value_counts.index.tolist()  # List label
values = value_counts.values.tolist()  # List value

# Membuat bar chart
plt.figure(figsize=(16, 9))
plt.bar(labels, values, color=['blue', 'orange', 'green', 'purple'], alpha=0.7, edgecolor='black')

# Menambahkan judul dan label
plt.title('Distribusi Data', fontsize=14)
plt.xlabel('Jenis Perintah', fontsize=12)
plt.ylabel('Nilai', fontsize=12)

# Menambahkan nilai di atas setiap batang
for i, v in enumerate(values):
    plt.text(i, v + 1, str(v), ha='center', fontsize=10, color='black')

# Menampilkan grafik
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.show()
st.pyplot(plt)

st.subheader('''Split Train 80% & Test 20%''', divider=True)
# Membagi data menjadi data latih dan uji
X_train, X_test, y_train, y_test = train_test_split(kalimat, label, test_size=0.2, random_state=42)
st.code("kalimat = dfr['text'].tolist()\nlabel = dfr['label'].tolist()\nX_train, X_test, y_train, y_test = train_test_split(kalimat, label, test_size=0.2, random_state=42)", language="python")

st.subheader('''Transformasi teks menjadi vektor numerik menggunakan TF-IDF''', divider=True)
vectorizer = TfidfVectorizer()
X_train_tfidf = vectorizer.fit_transform(X_train)   # Fit dan transformasi data train
X_test_tfidf = vectorizer.transform(X_test)
st.code('''vectorizer = TfidfVectorizer()
        \nX_train_tfidf = vectorizer.fit_transform(X_train) # Fit dan transformasi data train
        \nX_test_tfidf = vectorizer.transform(X_test) # Transformasi data test''', 
        language="python")

st.subheader('''Membuat dan melatih model KNN''', divider=True)
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train_tfidf, y_train)
st.code('''knn = KNeighborsClassifier(n_neighbors=3)
        \nknn.fit(X_train_tfidf, y_train)''', 
        language="python")

st.subheader('''Confusion matrix hasil prediksi''', divider=True)
y_pred = knn.predict(X_test_tfidf)
conf_matrix = confusion_matrix(y_test, y_pred)

# Menampilkan Heatmap
plt.figure(figsize=(16, 9))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)

plt.xlabel('Predicted Labels', fontsize=12)
plt.ylabel('True Labels', fontsize=12)
st.pyplot(plt)

st.subheader('''Evaluasi Model''', divider=True)
#st.markdown(classification_report(y_test, y_pred))
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

####################################################################
#Simpan model dan vectorizer
#joblib.dump(knn, 'knn_model.pkl')                 # Simpan model KNN
#joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')   # Simpan TF-IDF vectorizer