import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ページ設定
st.set_page_config(layout="wide", page_title="Antigravity Coffee Dashboard")

# 1. 接続設定：secrets.toml の [connections.gsheets] を使用
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    # スプレッドシートから全データを読み込む
    return conn.read(ttl="0") # キャッシュを無効化して常に最新を取得

def update_spreadsheet(df):
    # スプレッドシートの内容を現在のデータフレームで上書き
    conn.update(data=df)

st.title("Antigravity Coffee Dashboard")

try:
    # データの取得
    df = get_data()

    # 既存のデータをループで表示
    for i, row in df.iterrows():
        with st.container(border=True):
            # 表示用：日付とID
            st.markdown(f"### 📅 {row['date']} | ID: {row['id']}")
            
            # プレビュー（Markdownとしてリンク等を有効化）
            if pd.notna(row['insight']) and row['insight'] != "":
                st.info("📝 現在のプレビュー（リンク有効）")
                st.markdown(row['insight'])
            
            st.divider()
            
            # 編集用：テキストエリア
            new_insight = st.text_area(
                "編集用（Geminiの回答をここに貼る）", 
                value=row['insight'] if pd.notna(row['insight']) else "", 
                key=f"edit_{i}", 
                height=250
            )
            
            # 保存ボタン
            if st.button("💾 スプレッドシートへ保存", key=f"save_{i}"):
                df.at[i, 'insight'] = new_insight
                update_spreadsheet(df)
                st.success(f"ID: {row['id']} の保存に成功しました！")
                st.rerun()

except Exception as e:
    st.error(f"接続エラーが発生しました。secrets.toml の設定を確認してください: {e}")
