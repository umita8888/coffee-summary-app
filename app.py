import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ページ設定
st.set_page_config(page_title="Antigravity Insight Dashboard", layout="wide")

# スプレッドシート接続
conn = st.connection("gsheets", type=GSheetsConnection)

# データの読み込み
def load_data():
    return conn.read(worksheet="Sheet1", ttl="0s")

df = load_data()

st.title("Antigravity 蓄積ダッシュボード")

# 入力フォーム
with st.form("insight_form"):
    x_url = st.text_input("X（旧Twitter）ポストのURL")
    insight_text = st.text_area("考察内容（umita風案＋深層インサイト）", height=300)
    submit_button = st.form_submit_button("スプレッドシートへ自動転送・保存")

    if submit_button:
        if x_url and insight_text:
            # 新しい行の作成
            new_id = len(df) + 1
            new_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame([{
                "id": new_id,
                "date": new_date,
                "x_url": x_url,
                "insight": insight_text,
                "status": "stored"
            }])
            
            # スプレッドシートへ追記（自動転送）
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            
            st.success("スプレッドシートへ正常に自動転送されました！蓄積完了です。")
            st.rerun()
        else:
            st.error("URLと考察の両方を入力してください。")

# 蓄積済みデータの表示
st.subheader("現在の蓄積資産（NotebookLM同期対象）")
st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True)
