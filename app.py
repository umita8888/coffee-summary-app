import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import re

st.set_page_config(layout="wide", page_title="Antigravity Dashboard")
st.title("Antigravity Coffee Dashboard")

def get_gspread_client():
    s = st.secrets.connections.gsheets
    raw_key = s.get("private_key", "")
    
    # --- 【論理強制】どんな形式の鍵でも PEM 規格に叩き直すロジック ---
    # 1. 余計な文字（\n, \r, スペース）をすべて排除して純粋なデータのみにする
    clean_body = raw_key.replace("\\n", "").replace("\n", "").replace("\r", "").replace(" ", "")
    header = "-----BEGIN PRIVATE KEY-----"
    footer = "-----END PRIVATE KEY-----"
    
    # 2. 中身だけを取り出し、64文字ごとに物理改行を入れる
    inner_data = clean_body.replace(header, "").replace(footer, "")
    formatted_body = "\n".join([inner_data[i:i+64] for i in range(0, len(inner_data), 64)])
    
    # 3. 完璧な PEM 形式を再構築
    fixed_key = f"{header}\n{formatted_body}\n{footer}\n"
    # ---------------------------------------------------------

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
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=scopes))

try:
    gc = get_gspread_client()
    sh = gc.open_by_url(st.secrets.connections.gsheets.get("spreadsheet"))
    worksheet = sh.get_worksheet(0)
    
    # 知見のプールを表示
    df = pd.DataFrame(worksheet.get_all_records())
    if not df.empty:
        st.success("接続成功。知見の永続化が可能です。")
        st.dataframe(df, use_container_width=True)
        # (以下、保存・編集ロジック)
    else:
        st.info("データが空です。")

except Exception as e:
    st.error(f"【最終論理チェック中】: {e}")
