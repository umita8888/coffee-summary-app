import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide")

# 接続の試行
try:
    # connections.gsheets セクションを明示的に参照
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
    
    st.title("Antigravity Coffee Dashboard")
    
    for i, row in df.iterrows():
        with st.container(border=True):
            st.markdown(f"### 📅 {row['date']} | ID: {row['id']}")
            if pd.notna(row['insight']):
                st.markdown(row['insight'])
            
            new_insight = st.text_area("編集", value=row['insight'] if pd.notna(row['insight']) else "", key=f"ed_{i}")
            
            if st.button("💾 保存", key=f"btn_{i}"):
                df.at[i, 'insight'] = new_insight
                conn.update(data=df)
                st.success("保存完了")
                st.rerun()

except Exception as e:
    st.error(f"論理エラー: {e}")
    st.info("Secretsの [connections.gsheets] セクションを確認してください。")
