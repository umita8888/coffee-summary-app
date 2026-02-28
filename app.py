import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ページ設定
st.set_page_config(page_title="Coffee Insight Dashboard", layout="wide")

st.title("☕️ Coffee Insight Dashboard")
st.write("日々のコーヒーニュースと深層考察を蓄積する資産管理ツールです。")

# Google Sheets への接続設定
# secrets.toml に [connections.gsheets] の設定が必要です
conn = st.connection("gsheets", type=GSheetsConnection)

# データの読み込み（スプレッドシートの1枚目のシートを読み込む想定）
try:
    df = conn.read()
except Exception:
    # シートが空の場合や初回実行時のための空のデータフレーム
    df = pd.DataFrame(columns=["タイトル", "ソース", "投稿案", "考察内容"])

# 入力フォーム
with st.form("insight_form"):
    st.subheader("📝 新しい考察を登録")
    title = st.text_input("タイトル")
    source = st.text_input("ソース (URLなど)")
    
    # 考察内容（Geminiの出力をここに貼り付ける）
    content_input = st.text_area("Geminiの出力（コピー内容をここにペースト）", height=300)
    
    submit_button = st.form_submit_button("スプレッドシートへ保存")

if submit_button:
    if title and content_input:
        # 新しい行のデータ作成
        new_row = pd.DataFrame([{
            "タイトル": title,
            "ソース": source,
            "考察内容": content_input
        }])
        
        # 既存のデータと新しいデータを結合
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        try:
            # データをスプレッドシートに反映（上書き更新）
            # もしここでもエラーが出る場合は、スプレッドシートの共有設定（編集者権限）を確認してください
            conn.update(data=updated_df)
            st.success("スプレッドシートに保存しました！")
            # 画面を更新して最新の状態を表示
            st.rerun()
        except Exception as e:
            st.error(f"保存中にエラーが発生しました: {e}")
            st.info("Googleスプレッドシートにサービスアカウントが『編集者』として共有されているか確認してください。")
    else:
        st.warning("タイトルと考察内容は必須です。")

# 蓄積されたデータの表示
st.divider()
st.subheader("🗂 蓄積された考察一覧")
if not df.empty:
