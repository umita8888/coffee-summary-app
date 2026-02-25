import streamlit as st
import json
import os

# ページ設定：ワイドモードで視認性を確保
st.set_page_config(page_title="Antigravity Coffee Dashboard", layout="wide")

# データ保存用ファイル
FILE_PATH = "data.json"

def load_data():
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(data):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# データの読み込み
data = load_data()

st.title("Antigravity Coffee Dashboard")
st.header("深掘り考察の蓄積")

# 考察一覧のループ表示
for i, item in enumerate(data):
    # 1件ごとに枠（コンテナ）で区切る
    with st.container(border=True):
        
        # --- レイアウト上部：ヘッダーと直接リンクボタン ---
        col_info, col_link = st.columns([0.7, 0.3])
        with col_info:
            st.subheader(f"📅 {item.get('date', 'Date')} | ID: {item.get('id', 'N/A')}")
        with col_link:
            if item.get('x_url'):
                # Xの投稿へ直接飛べるボタン
                st.link_button("🚀 元の投稿(X)を開く", item['x_url'], use_container_width=True)

        # --- 重要：プレビュー表示枠（ここでURLがリンク化される） ---
        if item.get('insight'):
            st.info("📝 考察プレビュー（リンクが有効なエリア）")
            # 考察内容をMarkdownとして描画。これでURLがクリック可能になります。
            st.markdown(item['insight'])
            st.divider()

        # --- 編集用エリア ---
        # Geminiの回答を貼り付ける場所
        new_insight = st.text_area(
            "✍️ 深掘り考察の編集（ここにGeminiの回答を貼り付けて保存）",
            value=item.get('insight', ''),
            key=f"area_{i}",
            height=300
        )
        
        # --- 操作ボタン ---
        save_col, del_col = st.columns([1, 1])
        if save_col.button("💾 この内容で保存", key=f"save_{i}"):
            data[i]['insight'] = new_insight
            save_data(data)
            st.success("保存しました。プレビューを確認してください。")
            st.rerun()
            
        if del_col.button("🗑 項目を削除", key=f"del_{i}"):
            data.pop(i)
            save_data(data)
            st.rerun()

st.divider()
st.caption("Antigravity Coffee Dashboard | System Version: 2.0 (Stable)")
