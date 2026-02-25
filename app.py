import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Antigravity Coffee Dashboard", layout="wide")
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

data = load_data()

# --- サイドバー：新規枠の作成エリア ---
with st.sidebar:
    st.header("📝 新規追加")
    new_url = st.text_input("Xの投稿URLを入力", key="new_url_input")
    if st.button("枠を作成する"):
        if new_url:
            # IDを重複させないための抽出
            new_id = new_url.split('/')[-1].split('?')[0]
            
            # 新しいデータ構造を作成（ここを空に固定）
            new_item = {
                "id": new_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "x_url": new_url,
                "insight": "", # ここを確実に空にする
                "status": "draft"
            }
            data.insert(0, new_item) 
            save_data(data)
            st.success("新しい枠を作成しました")
            st.rerun()

# --- メインエリア ---
st.title("Antigravity Coffee Dashboard")
st.header("深掘り考察の蓄積")

for i, item in enumerate(data):
    # 各枠に固有のKeyを割り当てて、混同を防ぐ
    with st.container(border=True):
        col_info, col_link = st.columns([0.7, 0.3])
        with col_info:
            st.subheader(f"📅 {item.get('date')} | ID: {item.get('id')}")
        with col_link:
            if item.get('x_url'):
                st.link_button("🚀 元の投稿(X)を開く", item['x_url'], use_container_width=True)

        if item.get('insight'):
            st.info("📝 考察プレビュー（リンク有効）")
            st.markdown(item['insight'])
            st.divider()

        # 編集枠：valueにitemの内容を紐付け、一意のkeyを持たせる
        new_insight = st.text_area(
            "✍️ 深掘り考察の編集",
            value=item.get('insight', ''),
            key=f"editor_{item.get('id')}_{i}", # IDを含めることで複製バグを防止
            height=300
        )
        
        save_col, del_col = st.columns(2)
        if save_col.button("💾 保存", key=f"save_btn_{i}"):
            data[i]['insight'] = new_insight
            save_data(data)
            st.success("保存しました")
            st.rerun()
            
        if del_col.button("🗑 削除", key=f"del_btn_{i}"):
            data.pop(i)
            save_data(data)
            st.rerun()
