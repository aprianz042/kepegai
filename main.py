import streamlit as st

main_page = st.Page("app.py", title="Main App", icon=":material/add_circle:")
delete_page = st.Page("train_knn.py", title="Classification", icon=":material/delete:")

pg = st.navigation([main_page, 
                    delete_page])


st.set_page_config(page_title="PNS BOT", 
                   page_icon=":material/edit:")

pg.run()
