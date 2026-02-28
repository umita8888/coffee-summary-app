import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ページ設定
st.set_page_config(page_title="Coffee Insight Dashboard", layout="wide")

st.title("☕️ Coffee Insight Dashboard")
st.write("日々のコーヒーニュースと深層考察を蓄積する資産管理ツールです。")

# Google Sheets への接続設定
# ※公開URLではなく、サービスアカウント認証が必須です
conn = st.connection("gsheets", type=GSheetsConnection)

# データの読み込み
try:
    # 常に最新を読み込むため ttl=0
    df = conn.read(ttl=0)
except Exception:
    # 読み込めない場合は空のDFを作成
    df = pd.DataFrame(columns=["タイトル", "ソース", "考察内容"])

# 入力フォーム（画像のデザインに完全準拠）
with st.form("insight_form"):
    st.subheader("📝 新しい考察を登録")
    title = st.text_input("タイトル")
    source = st.text_input("ソース (URLなど)")
    
    # Geminiから一発コピーした内容をそのまま貼り付ける場所
    content_input = st.text_area("Geminiの出力（コピー内容をここにペースト）", height=400)
    
    submit_button = st.form_submit_button("スプレッドシートへ保存")

if submit_button:
    if title and content_input:
        # 新しいデータの作成
        new_row = pd.DataFrame([{
            "タイトル": title,
            "ソース": source,
            "考察内容": content_input
        }])
        
        # 既存データと結合（最新が上に来るように表示は制御、保存は末尾へ）
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        try:
            # サービスアカウント認証が通っていれば書き込み可能
            conn.update(data=updated_df)
            st.success("スプレッドシートへの保存に成功しました！")
            st.rerun()
        except Exception as e:
            st.error(f"保存中にエラーが発生しました: {e}")
            st.info("【確認】スプレッドシートの右上の『共有』ボタンから、サービスアカウントのメールアドレスを『編集者』として追加していますか？")
    else:
        st.warning("タイトルと考察内容は必須です。")

# 蓄積されたデータの表示
st.divider()
st.subheader("🗂 蓄積された考察一覧")
if not df.empty:
    # 最新のものが一番上に表示されるように index を逆順にして表示
    st.dataframe(df.iloc[::-1], use_container_width=True)
else:
    st.write("まだデータがありません。")
