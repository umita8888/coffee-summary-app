import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ページ設定
st.set_page_config(page_title="Antigravity Insight Dashboard", layout="wide")

st.title("Antigravity 蓄積ダッシュボード")

# スプレッドシート接続（ここが自動転送の要）
conn = st.connection("gsheets", type=GSheetsConnection)

# データの読み込み
def load_data():
    return conn.read(ttl="0s")

df = load_data()

# 入力フォーム
with st.form("insight_form"):
    x_url = st.text_input("X（旧Twitter）ポストのURL")
    insight_text = st.text_area("考察内容", height=300)
    submit_button = st.form_submit_button("スプレッドシートへ保存")

    if submit_button:
        if x_url and insight_text:
            # 新しい行のデータ作成
            new_row = pd.DataFrame([{
                "id": len(df) + 1,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "x_url": x_url,
                "insight": insight_text,
                "status": "stored"
            }])
            
            # スプレッドシートの既存データに結合
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            # 【重要】スプレッドシートへ自動書き込み（上書き更新）
            conn.update(data=updated_df)
            
            st.success("スプレッドシートへ保存しました！")
            st.rerun()
        else:
            st.error("URLと考察を入力してください。")

st.subheader("現在の蓄積データ")
st.dataframe(df.sort_values(by="date", ascending=False), use
