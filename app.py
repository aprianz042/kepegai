import streamlit as st

#main_page = st.Page("chat.py", title="Main App", icon=":material/add_circle:")

main_page = st.Page("main.py", title="🤖 Main App")
knn = st.Page("knn.py", title="♻️ Prompt Classification")
backend = st.Page("backend.py", title="⚙️ Back-End")
guide = st.Page("guide.py", title="📔 Prompt Guide")

pg = st.navigation([main_page, 
                    knn,
                    backend,
                    guide])

st.set_page_config(page_title="PNS BOT", 
                   page_icon="🤖",
                   layout="wide")
pg.run()

# Footer di Sidebar menggunakan HTML dan CSS
footer = """
<style>
.sidebar .sidebar-content {
    padding-bottom: 50px;
}
.footer {
    position: relative;
    bottom: 0;
    width: 100%;
    text-align: left;
    padding: 10px;
    font-size: 12px;
    color: #555;
}

.footer img {
    margin: 0 5px 0 5px;
}

</style>
<div class="footer">
    <img src="https://setjen.kemendagri.go.id/_nuxt/img/logo@2x.53f3a6e.png" alt="Kemendagri" width="50px" height="auto">
    <img src="https://upload.wikimedia.org/wikipedia/commons/1/15/Logo_Kementerian_Perhubungan_Indonesia_%28Kemenhub%29.png" alt="Kemenhub" width="50px" height="auto">
        <img src="https://dti.itb.ac.id/wp-content/uploads/2020/09/logo_itb_1024.png" alt="ITB" width="60px" height="auto">
</div>
"""
st.sidebar.markdown(footer, unsafe_allow_html=True)
