import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide", page_title="Antigravity Dashboard")

st.title("Antigravity Coffee Dashboard")

try:
    # --- 論理修正：Secretsの \n を本物の改行に置換 ---
    if "connections" in st.secrets and "gsheets" in st.secrets.connections:
        # private_key 内の文字としての "\n" を実際の改行コードに置換
        raw_key = st.secrets.connections.gsheets.get("private_key", "")
        fixed_key = raw_key.replace("\\n", "\n")
        # 置換した鍵を一時的に上書き（メモリ上のみ）
        st.secrets.connections.gsheets["private_key"] = fixed_key

    # 1. 接続の確立
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. データの読み込み
    df = conn.read(ttl=0)
    
    if df.empty:
        st.warning("スプレッドシートが空です。")
    else:
        cols = df.columns.tolist()
        for i, row in df.iterrows():
            with st.container(border=True):
                display_date = row['date'] if 'date' in cols else "No Date"
                display_id = row['id'] if 'id' in cols else f"Row {i}"
                st.markdown(f"### 📅 {display_date} | ID: {display_id}")
                
                current_insight = row['insight'] if 'insight' in cols else ""
                new_insight = st.text_area("編集", value=current_insight if pd.notna(current_insight) else "", key=f"ed_{i}")
                
                if st.button("💾 保存", key=f"btn_{i}"):
                    if 'insight' in cols:
                        df.at[i, 'insight'] = new_insight
                        conn.update(data=df)
                        st.success("保存完了")
                        st.rerun()

except Exception as e:
    st.error(f"【論理エラー発生】: {e}")
