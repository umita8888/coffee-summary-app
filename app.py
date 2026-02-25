import streamlit as st
import json
import os
from datetime import datetime

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE): return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="Coffee Insights", layout="wide")
data = load_data()

# --- サイドバー ---
st.sidebar.header("🤖 Gemini連携")
gemini_url = "https://gemini.google.com/app/44fc448c9f9f8e77?hl=ja" 
st.sidebar.markdown(f"**[💬 Geminiを開いて考察を依頼]({gemini_url})**")

with st.sidebar.form("input"):
    u = st.text_input("新規記事URL")
    if st.form_submit_button("1. 下書き作成"):
        data.append({"date": datetime.now().strftime("%Y-%m-%d"), "x_url": u, "insight": "", "status": "draft"})
        save_data(data)
        st.rerun()

# --- メイン：蓄積データ表示 ---
st.title("☕ Coffee Insights Dashboard")

# データの並び順を新しい順にする
for idx, entry in enumerate(reversed(data)):
    # 元のリストのインデックスを計算
    original_idx = len(data) - 1 - idx
    
    with st.expander(f"📅 {entry['date']} | {entry['x_url']}", expanded=(entry['status'] == 'draft')):
        # 編集エリア
        text = st.text_area("考察内容（Geminiの回答をここに貼り付け）", value=entry['insight'], height=200, key=f"edit_{idx}")
        
        col1, col2 = st.columns([1, 5])
        if col1.button("💾 保存", key=f"save_{idx}"):
            data[original_idx]['insight'] = text
            data[original_idx]['status'] = 'published'
            save_data(data)
            st.rerun()
        if col2.button("🗑️ 削除", key=f"del_{idx}"):
            data.pop(original_idx)
            save_data(data)
            st.rerun()