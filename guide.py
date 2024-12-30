import streamlit as st

st.title("Prompt Guide")
st.subheader("***Perintah khusus***", divider=True)
st.markdown("***Perintah untuk menampilkan data terbatas pada database yang dimiliki (Private)***")
st.code('''#contoh :
        \nBerapa jumlah pegawai yang beragama Islam?
        \nBerapa jumlah pegawai yang belum menikah?
        \nSiapa saja pegawai yang tugas belajar dengan beasiswa?
        \nSiapa saja pegawai yang berusia lebih dari 40 tahun?
        \nTampilkan data pegawai yang memiliki spesialisasi IT.
        \nTampilkan data pegawai yang berasal dari kota Bandung.
        ''')

st.subheader("***Perintah membuat grafik***", divider=True)
st.markdown("***Perintah untuk membuat grafik data terbatas pada database yang dimiliki (Private)***")
st.code('''#contoh :
        \nBuatkan grafik data pegawai berdasarkan pendidikan.
        \nBuatkan grafik pegawai berdasarkan pangkat
        \nBuatkan grafik data pegawai tugas belajar berdasarkan universitas.
        \nBuatkan grafik data pegawai berdasarkan status pernikahan
        \nBuatkan grafik pegawai berdasarkan umur
        ''')

st.subheader("***Perintah umum***", divider=True)
st.markdown("***Perintah untuk mendapatkan informasi umum tentang ASN/PNS di Indonesia yang dieksekusi langsung menggunakan Gemini***")
st.code('''#contoh :
        \nBagaimana proses seleksi penerimaan PNS?
        \nApa saja kriteria yang digunakan dalam ujian PNS?
        \nApakah PNS mendapatkan tunjangan?
        \nApa itu sistem merit dalam seleksi PNS?
        \nApa hak PNS dalam hal pendidikan dan pelatihan?
        \nBagaimana cara PNS mengajukan cuti?
        ''')

st.subheader("***Perintah membuat grafik dengan gemini (beta)***", divider=True)
st.markdown("***Perintah untuk membuat grafik data terbatas pada database yang dimiliki (Private), namun sepenuhnya di atur oleh gemini***")
st.code('''#contoh :
        \nBuatkan grafik jumlah pegawai per status_kepegawaian dengan gemini
        \nBuatkan grafik status_pernikahan pegawai dengan gemini
        \nDengan gemini, buatkan grafik jumlah pegawai berdasarkan kota_lahir
        \nBuatkan grafik tingkat pendidikan pegawai dengan gemini
        \nDengan gemini, buatkan grafik distribusi grade pegawai
        \nBuatkan grafik perguruan_tinggi favorit dalam tugas_belajar dengan gemini
        \n#NB : masih dalam pengembangan
        ''')
