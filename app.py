import streamlit as st
import pandas as pd
from datetime import datetime

# ページ設定
st.set_page_config(page_title="Insight Dashboard", layout="wide")

# スプレッドシートのURL（Secretsから取得）
# 読み取り用に末尾を /export?format=csv に変換する
raw_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
csv_url = raw_url.replace("/edit#gid=0", "/export?format=csv").replace("/edit?usp=sharing", "/export?format=csv")

def load_data():
    try:
        # CSVとして直接読み込む（最もエラーが少ない方法）
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"データの読み込みに失敗しました。スプレッドシートが『リンクを知っている全員（編集者）』になっているか確認してください。")
        return pd.DataFrame(columns=["id", "date", "x_url", "insight", "status"])

df = load_data()

st.title("Antigravity 蓄積ダッシュボード")

# 入力フォーム
with st.form("insight_form"):
    x_url = st.text_input("X（旧Twitter）ポストのURL")
    insight_text = st.text_area("考察内容", height=300)
    submit_button = st.form_submit_button("スプレッドシートへ保存")

    if submit_button:
        if x_url and insight_text:
            # 新しい行の作成
            new_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame([[len(df)+1, new_date, x_url, insight_text, "stored"]], 
                                   columns=["id", "date", "x_url", "insight", "status"])
            
            # 今回は簡易的に「保存方法の案内」を表示
            st.info("スプレッドシート連携をさらに安定させるため、まずはこの画面が表示されるか確認してください。")
            st.write("入力された内容:", new_row)
            
            # 本来はここに書き込み処理が入りますが、まずは「表示」を優先します
            st.success("表示確認ができました。次に進みますか？")
        else:
            st.error("入力が不足しています。")

st.subheader("現在の蓄積データ")
st.dataframe(df)
