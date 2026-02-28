import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide", page_title="Antigravity Dashboard")
st.title("Antigravity Coffee Dashboard")

try:
    s = st.secrets.connections.gsheets
    
    # --- 論理修正：\n を「文字」から「改行コード」へ物理的に変換 ---
    raw_key = s.get("private_key", "")
    # 一度バイナリに直してエスケープを解除する魔法の処理
    fixed_key = raw_key.encode('utf-8').decode('unicode_escape')
    
    creds_dict = {
        "type": "service_account",
        "project_id": s.get("project_id"),
        "private_key_id": s.get("private_key_id"),
        "private_key": fixed_key, # 変換後の鍵
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
    worksheet = sh.get_worksheet(0)

    # 4. データの読み込み
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        st.warning("スプレッドシートが空です。記事を投稿してデータを蓄積しましょう。")
    else:
        st.success("接続成功。過去の考察データを読み込みました。")
        st.dataframe(df, use_container_width=True)
        
        # 編集・プール機能
        cols = df.columns.tolist()
        for i, row in df.iterrows():
            with st.container(border=True):
                display_date = row.get('date', f"Row {i+1}")
                st.markdown(f"### 📅 {display_date}")
                
                current_insight = row.get('insight', "")
                new_insight = st.text_area("深層インサイト（蓄積用）", value=str(current_insight), key=f"ed_{i}")
                
                if st.button("💾 この考察をプールする", key=f"btn_{i}"):
                    if 'insight' in cols:
                        col_idx = cols.index('insight') + 1
                        worksheet.update_cell(i + 2, col_idx, new_insight)
                        st.success("Googleスプレッドシートに永続保存しました。")
                        st.rerun()

except Exception as e:
    st.error(f"【根本エラー発生】: {e}")
    st.info("このエラーが出る場合、Secretsの private_key の前後の引用符を確認してください。")
