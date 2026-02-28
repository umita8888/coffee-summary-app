import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import codecs

st.set_page_config(layout="wide", page_title="Antigravity Dashboard")
st.title("Antigravity Coffee Dashboard")

def get_gspread_client():
    # クラウドでもローカルでも共通のSecretsを参照
    s = st.secrets.connections.gsheets
    raw_key = s.get("private_key", "")
    
    # 【論理修正】環境に依存する \n の解釈を物理的に統一する
    # 文字列内の \\n を本物の改行コードへ強制デコード
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
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(credentials)

try:
    gc = get_gspread_client()
    sh = gc.open_by_url(st.secrets.connections.gsheets.get("spreadsheet"))
    worksheet = sh.get_worksheet(0)
    
    # 知見の読み込み
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    if not df.empty:
        st.success("知見のプールに接続しました。過去の考察が資産として蓄積されています。")
        
        # 逆順（新しい順）で表示
        for i, row in df.iloc[::-1].iterrows():
            with st.container(border=True):
                st.markdown(f"### 📅 {row.get('date', '不明')} | ID: {row.get('id', 'なし')}")
                
                # Geminiの考察をここに貼り付けて保存する
                current_insight = str(row.get('insight', ''))
                new_insight = st.text_area("深層インサイト・ポスト案の編集", value=current_insight, key=f"area_{i}", height=250)
                
                if st.button("💾 この知見を永続保存する", key=f"save_{i}"):
                    # Google Sheetsの 'insight' 列を特定（1始まりのインデックス）
                    col_idx = list(df.columns).index('insight') + 1
                    worksheet.update_cell(i + 2, col_idx, new_insight)
                    st.success("Googleスプレッドシートへの蓄積が完了しました。")
                    st.rerun()
    else:
        st.info("まだプールされている知見はありません。")

except Exception as e:
    st.error(f"【論理エラー再検証結果】: {e}")
    st.info("Streamlit CloudのSettings > Secrets の設定がPC側と一致しているか確認してください。")
