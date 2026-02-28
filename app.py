import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import codecs

st.set_page_config(layout="wide", page_title="Antigravity Dashboard")
st.title("Antigravity Coffee Dashboard")

try:
    s = st.secrets.connections.gsheets
    
    # --- 論理再構築：隠れたエスケープ文字を物理的な改行へ復元 ---
    raw_key = s.get("private_key", "")
    # codecsを使い、文字列内の '\\n' を本物の '改行' に強制変換する
    fixed_key = codecs.escape_decode(bytes(raw_key, "utf-8"))[0].decode("utf-8")
    
    creds_dict = {
        "type": "service_account",
        "project_id": s.get("project_id"),
        "private_key_id": s.get("private_key_id"),
        "private_key": fixed_key, 
        "client_email": s.get("client_email"),
        "client_id": s.get("client_id"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": s.get("client_x509_cert_url")
    }

    # 2. 認証と接続
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(credentials)

    # 3. スプレッドシートの取得
    sh = gc.open_by_url(s.get("spreadsheet"))
    worksheet = sh.get_worksheet(0)

    # 4. データの読み込みと一覧表示
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        st.warning("スプレッドシートにデータがありません。")
    else:
        st.success("接続成功。知見のプールが稼働しました。")
        st.dataframe(df, use_container_width=True)
        
        # 編集・プール機能（リセットされない自分専用の書庫）
        cols = df.columns.tolist()
        for i, row in df.iterrows():
            with st.container(border=True):
                st.markdown(f"### 📅 {row.get('date', f'Row {i+1}')}")
                
                current_insight = row.get('insight', "")
                new_insight = st.text_area("深層インサイト（編集して保存）", value=str(current_insight), key=f"ed_{i}")
                
                if st
