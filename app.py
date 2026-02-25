import streamlit as st
import json
import requests
import base64
from datetime import datetime

# --- 設定 ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["GITHUB_REPO"]
FILE_PATH = "data.json"

st.set_page_config(page_title="Coffee Insights Dashboard", layout="wide")

def get_data():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {TOKEN}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        content = res.json()
        decoded = base64.b64decode(content['content']).decode('utf-8')
        return json.loads(decoded), content['sha']
    return [], None

def save_data(data, sha):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {TOKEN}"}
    updated_content = json.dumps(data, indent=2, ensure_ascii=False)
    payload = {
        "message": f"Update insight at {datetime.now()}",
        "content": base64.b64encode(updated_content.encode('utf-8')).decode('utf-8'),
        "sha": sha
    }
    res = requests.put(url, headers=headers, json=payload)
    return res.status_code == 200

# --- メイン画面 ---
st.title("☕ Coffee Insights Dashboard")

data, sha = get_data()

# 新規投稿の下書き作成
with st.sidebar:
    st.header("👁 Gemini連携")
    new_url = st.text_input("新規記事URL")
    if st.button("下書き作成"):
        new_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "x_url": new_url,
            "insight": "",
            "status": "draft"
        }
        data.insert(0, new_entry)
        save_data(data, sha)
        st.rerun()

# 考察一覧の表示
for i, item in enumerate(data):
    with st.expander(f"📅 {item['date']} | {item['x_url']}", expanded=(item['status'] == 'draft')):
        new_insight = st.text_area("考察内容", item['insight'], key=f"area_{i}", height=200)
        
        col1, col2 = st.columns(2)
        if col1.button("💾 保存して全端末に同期", key=f"save_{i}"):
            data[i]['insight'] = new_insight
            data[i]['status'] = 'published'
            if save_data(data, sha):
                st.success("GitHubと同期しました！スマホでも確認できます。")
                st.rerun()
        
        if col2.button("🗑 削除", key=f"del_{i}"):
            data.pop(i)
            save_data(data, sha)
            st.rerun()
