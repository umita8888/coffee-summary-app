import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ページ設定
st.set_page_config(page_title="Coffee Insight Dashboard", layout="wide")

st.title("☕️ Coffee Insight Dashboard")
st.write("日々のコーヒーニュースと深層考察を蓄積する資産管理ツールです。")

# Google Sheets への接続設定
conn = st.connection("gsheets", type=GSheetsConnection)

# データの読み込み
try:
    df = conn.read()
except Exception:
    df = pd.DataFrame(columns=["タイトル", "ソース", "考察内容"])

# 入力フォーム
with st.form("insight_form"):
    st.subheader("📝 新しい考察を登録")
    title = st.text_input("タイトル")
    source = st.text_input("ソース (URLなど)")
    content_input = st.text_area("Geminiの出力（コピー内容をここにペースト）", height=300)
    submit_button = st.form_submit_button("スプレッドシートへ保存")

if submit_button:
    if title and content_input:
        new_row = pd.DataFrame([{
            "タイトル": title,
            "ソース": source,
            "考察内容": content_input
        }])
        
        # 既存のデータと新しいデータを結合
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        try:
            # データを一括更新
            conn.update(data=updated_df)
            st.success("スプレッドシートに保存しました！")
            st.rerun()
        except Exception as e:
            st.error(f"保存中にエラーが発生しました: {e}")
    else:
        st.warning("タイトルと考察内容は必須です。")

# 蓄積されたデータの表示
st.divider()
st.subheader("🗂 蓄積された考察一覧")

# ↓ ここからインデント（字下げ）を厳密に修正しました
if not df.empty:
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
else:
    st.write("まだデータがありません。")
