import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide", page_title="Antigravity Dashboard")

st.title("Antigravity Coffee Dashboard")

try:
    # 1. Secretsからデータを取得し、\n を本物の改行に置換した辞書を作成
    s = st.secrets.connections.gsheets
    credentials = {
        "type": s.get("type"),
        "project_id": s.get("project_id"),
        "private_key_id": s.get("private_key_id"),
        "private_key": s.get("private_key", "").replace("\\n", "\n"), # ここで置換
        "client_email": s.get("client_email"),
        "client_id": s.get("client_id"),
        "auth_uri": s.get("auth_uri"),
        "token_uri": s.get("token_uri"),
        "auth_provider_x509_cert_url": s.get("auth_provider_x509_cert_url"),
        "client_x509_cert_url": s.get("client_x509_cert_url"),
        "spreadsheet": s.get("spreadsheet")
    }

    # 2. 置換済みの credentials を使って接続（Secrets自体は汚さない）
    conn = st.connection("gsheets", type=GSheetsConnection, **credentials)
    
    # 3. データの読み込み
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
