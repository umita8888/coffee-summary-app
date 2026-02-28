import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide", page_title="Antigravity Dashboard")

st.title("Antigravity Coffee Dashboard")

try:
    # 1. Secretsからデータを取得し、Googleが求める形式に整える
    s = st.secrets.connections.gsheets
    
    # 秘密鍵の \n を本物の改行に変換し、認証に必要な構造を作成
    service_account_info = {
        "type": "service_account",
        "project_id": s.get("project_id"),
        "private_key_id": s.get("private_key_id"),
        "private_key": s.get("private_key", "").replace("\\n", "\n"),
        "client_email": s.get("client_email"),
        "client_id": s.get("client_id"),
        "auth_uri": s.get("auth_uri"),
        "token_uri": s.get("token_uri"),
        "auth_provider_x509_cert_url": s.get("auth_provider_x509_cert_url"),
        "client_x509_cert_url": s.get("client_x509_cert_url")
    }

    # 2. 正しい引数名（service_account_info）で接続を確立
    conn = st.connection(
        "gsheets", 
        type=GSheetsConnection, 
        service_account_info=service_account_info,
        spreadsheet=s.get("spreadsheet")
    )
    
    # 3. データの読み込み
    df = conn.read(ttl=0)
    
    if df.empty:
        st.warning("スプレッドシートが空です。")
    else:
        cols = df.columns.tolist()
        # スプレッドシートを表示
        st.dataframe(df)
        
        # 編集エリア
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
