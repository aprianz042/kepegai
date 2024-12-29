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
