import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide", page_title="Antigravity Dashboard")
st.title("Antigravity Coffee Dashboard")

try:
    s = st.secrets.connections.gsheets
    
    # --- 論理修正：元データに含まれる \n 文字を本物の改行コードへ復元 ---
    # raw_key = "-----BEGIN...\n..." という1行の文字列
    raw_key = s.get("private_key", "")
    # \\n (文字) を \n (改行) に置換
    fixed_key = raw_key.replace("\\n", "\n")
    
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

    # 2. Google公式ライブラリで認証
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(credentials)

    # 3. スプレッドシートを開く
    sh = gc.open_by_url(s.get("spreadsheet"))
    worksheet = sh.get_worksheet(0)

    # 4. データの読み込み
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        st.warning("スプレッドシートにデータがありません。")
    else:
        st.success("接続成功。知見のプールを開きます。")
        st.dataframe(df, use_container_width=True)
        
        # 編集・プール機能（スプレッドシートへの直接書き込み）
        cols = df.columns.tolist()
        for i, row in df.iterrows():
            with st.container(border=True):
                display_date = row.get('date', f"Row {i+1}")
                st.markdown(f"### 📅 {display_date}")
                
                current_insight = row.get('insight', "")
                new_insight = st.text_area("知見の編集・蓄積", value=str(current_insight), key=f"ed_{i}")
                
                if st.button("💾 この内容をプールする", key=f"btn_{i}"):
                    if 'insight' in cols:
                        col_idx = cols.index('insight') + 1
                        # i+2 はヘッダーの分(1)と0始まりのインデックスの分(1)
                        worksheet.update_cell(i + 2, col_idx, new_insight)
                        st.success("Googleスプレッドシートに永続保存されました。")
                        st.rerun()

except Exception as e:
    st.error(f"【論理エラー継続】: {e}")
