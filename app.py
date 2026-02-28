import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide", page_title="Antigravity Dashboard")
st.title("Antigravity Coffee Dashboard")

# --- 根本解決：認証プロセスの自力構築 ---
try:
    s = st.secrets.connections.gsheets
    
    # 1. 認証情報の辞書を作成（\n を本物の改行に置換）
    creds_dict = {
        "type": "service_account",
        "project_id": s.get("project_id"),
        "private_key_id": s.get("private_key_id"),
        "private_key": s.get("private_key", "").replace("\\n", "\n"), # 文字としての\nを改行に変換
        "client_email": s.get("client_email"),
        "client_id": s.get("client_id"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": s.get("client_x509_cert_url")
    }

    # 2. Google公式ライブラリで直接認証
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(credentials)

    # 3. スプレッドシートを開く
    sh = gc.open_by_url(s.get("spreadsheet"))
    worksheet = sh.get_worksheet(0) # 最初のシート

    # 4. データの読み込みと表示
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        st.warning("スプレッドシートが空です。")
    else:
        # データの表示
        st.dataframe(df, use_container_width=True)
        
        # 編集機能
        cols = df.columns.tolist()
        for i, row in df.iterrows():
            with st.container(border=True):
                display_date = row.get('date', f"Row {i+1}")
                display_id = row.get('id', "No ID")
                st.markdown(f"### 📅 {display_date} | ID: {display_id}")
                
                current_insight = row.get('insight', "")
                new_insight = st.text_area("深層インサイト編集", value=str(current_insight), key=f"ed_{i}")
                
                if st.button("💾 この行を保存", key=f"btn_{i}"):
                    # 特定のセルを更新（gspreadは1始まり。ヘッダーの分+1、0始まりインデックスの分+1）
                    col_idx = cols.index('insight') + 1
                    worksheet.update_cell(i + 2, col_idx, new_insight)
                    st.success(f"行 {i+1} のインサイトを保存しました。")
                    st.rerun()

except Exception as e:
    st.error(f"【根本エラー発生】: {e}")
    st.info("Secretsの設定またはGoogleシートの共有設定（編集者権限）を確認してください。")
