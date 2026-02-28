import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide", page_title="Antigravity Dashboard")

st.title("Antigravity Coffee Dashboard")

try:
    # 1. Secretsからデータを取得し、\n を置換した「純粋な認証辞書」を作成
    s = st.secrets.connections.gsheets
    
    # 接続関数が混乱しないよう、認証に必要な項目だけを抽出・変換
    cred_dict = {
        "project_id": s.get("project_id"),
        "private_key_id": s.get("private_key_id"),
        "private_key": s.get("private_key", "").replace("\\n", "\n"),
        "client_email": s.get("client_email"),
        "client_id": s.get("client_id"),
        "auth_uri": s.get("auth_uri"),
        "token_uri": s.get("token_uri"),
        "auth_provider_x509_cert_url": s.get("auth_provider_x509_cert_url"),
        "client_x509_cert_url": s.get("client_x509_cert_url"),
        "spreadsheet": s.get("spreadsheet")
    }

    # 2. 接続の確立（type引数の重複を避ける）
    conn = st.connection("gsheets", type=GSheetsConnection, **cred_dict)
    
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
