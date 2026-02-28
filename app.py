import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ページ設定
st.set_page_config(page_title="Antigravity Insight Dashboard", layout="wide")

st.title("Antigravity 蓄積ダッシュボード")

# スプレッドシート接続
conn = st.connection("gsheets", type=GSheetsConnection)

# データの読み込み
def load_data():
    return conn.read(ttl="0s")

df = load_data()

# 入力フォーム
with st.form("insight_form"):
    st.subheader("新規考察の追加")
    x_url = st.text_input("X（旧Twitter）ポストのURL")
    insight_text = st.text_area("考察内容（umita風案＋深層インサイト）", height=300)
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
            
            # スプレッドシートへ自動書き込み
            conn.update(data=updated_df)
            
            st.success("スプレッドシートへ保存しました！")
            st.rerun()
        else:
            st.error("URLと考察を入力してください。")

# 蓄積済みデータの表示（新しい順）
st.divider()
st.subheader("過去に確定した考察・資産リスト")

if not df.empty:
    # 日付でソートして表示
    display_df = df.sort_values(by="date", ascending=False)
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("まだ蓄積されたデータがありません。最初の考察を入力してください。")
