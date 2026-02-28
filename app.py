import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import re

st.set_page_config(layout="wide", page_title="Antigravity Dashboard")
st.title("Antigravity Coffee Dashboard")

try:
    s = st.secrets.connections.gsheets
    
    # --- 論理再構築：1行の文字列から PEM 規格の複数行を生成 ---
    raw_key = s.get("private_key", "")
    
    # 1. 文字としての '\n' や実際の改行コードをすべて除去し、純粋なデータのみを抽出
    clean_key = raw_key.replace("\\n", "").replace("\n", "").replace("\r", "")
    
    # 2. ヘッダーとフッターを一旦切り離す
    header = "-----BEGIN PRIVATE KEY-----"
    footer = "-----END PRIVATE KEY-----"
    # 本体のデータのみを取り出す
    body = clean_key.replace(header, "").replace(footer, "").strip()
    
    # 3. 本体のデータを 64文字ごとに改行する（PEM規格の厳格なルール）
    lines = [body[i:i+64] for i in range(0, len(body), 64)]
    
    # 4. ヘッダー、64文字ごとの行、フッターを「本物の改行コード」で連結
    final_pem_key = header + "\n" + "\n".join(lines) + "\n" + footer + "\n"

    creds_dict = {
        "type": "service_account",
        "project_id": s.get("project_id"),
        "private_key_id": s.get("private_key_id"),
        "private_key": final_pem_key, # 規格通りに再構築された鍵
        "client_email": s.get("client_email"),
        "client_id": s.get("client_id"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": s.get("client_x509_cert_url")
    }

    # 認証とスプレッドシートへの接続
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(credentials)
    
    sh = gc.open_by_url(s.get("spreadsheet"))
    worksheet = sh.get_worksheet(0)
    df = pd.DataFrame(worksheet.get_all_records())

    st.success("接続成功。知見のプールが可能です。")
    st.dataframe(df, use_container_width=True)

    # (蓄積・保存機能は前述のロジックを継続)

except Exception as e:
    st.error(f"【論理エラー再検証中】: {e}")
