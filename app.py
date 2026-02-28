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

    # --- 【物理洗浄】あらゆる不純物を除去し、PEM形式をゼロから組み立て直す ---
    # 1. すべての改行文字(\\n, \n, \r)と引用符、余計なスペースを完全に排除
    clean_body = raw_key.replace("\\n", "").replace("\n", "").replace("\r", "").replace('"', '').replace("'", "").strip()
    
    # 2. ヘッダーとフッターを強制的に定義（入力ミスがあっても上書きする）
    header = "-----BEGIN PRIVATE KEY-----"
    footer = "-----END PRIVATE KEY-----"
    
    # 3. 既にあるヘッダー/フッターを一旦消して、純粋なBase64データのみにする
    pure_base64 = clean_body.replace(header, "").replace(footer, "")
    
    # 4. 64文字ごとに物理改行を入れ、完璧なPEM規格をメモリ上で生成
    formatted_body = "\n".join([pure_base64[i:i+64] for i in range(0, len(pure_base64), 64)])
    final_pem = f"{header}\n{formatted_body}\n{footer}\n"
    # ------------------------------------------------------------------

    creds_dict = {
        "type": "service_account",
        "project_id": s.get("project_id"),
        "private_key_id": s.get("private_key_id"),
        "private_key": final_pem,
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
    
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    if not df.empty:
        st.success("知見のプールに接続成功。永続的な蓄積が可能です。")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("データが読み込めましたが、中身が空です。")

except Exception as e:
    # これでエラーが出る場合は、Secretsの 'private_key' という名前自体が間違っている可能性があります
    st.error(f"【最終物理洗浄結果】: {e}")
