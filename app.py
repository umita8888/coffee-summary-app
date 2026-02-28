import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide", page_title="Antigravity Dashboard")

st.title("Antigravity Coffee Dashboard")

try:
    # 1. 接続の確立
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. データの読み込み
    df = conn.read(ttl=0)
    
    if df.empty:
        st.warning("スプレッドシートが空です。データを確認してください。")
    else:
        # 3. 列名の存在チェック
        cols = df.columns.tolist()
        
        for i, row in df.iterrows():
            with st.container(border=True):
                # 列名が存在するか確認しながら表示
                display_date = row['date'] if 'date' in cols else "No Date"
                display_id = row['id'] if 'id' in cols else f"Row {i}"
                
                st.markdown(f"### 📅 {display_date} | ID: {display_id}")
                
                # insight列の処理
                current_insight = row['insight'] if 'insight' in cols else ""
                
                new_insight = st.text_area(
                    "深層インサイトを編集", 
                    value=current_insight if pd.notna(current_insight) else "", 
                    key=f"ed_{i}",
                    height=200
                )
                
                if st.button("💾 この行を保存", key=f"btn_{i}"):
                    if 'insight' in cols:
                        df.at[i, 'insight'] = new_insight
                        conn.update(data=df)
                        st.success("保存に成功しました！")
                        st.rerun()
                    else:
                        st.error("シートに 'insight' 列がありません。")

except Exception as e:
    st.error(f"【論理エラー発生】: {e}")
    with st.expander("解決のためのチェックリスト"):
        st.write("""
        1. **Secretsの確認**: [connections.gsheets] 見出しがあるか。
        2. **URLの確認**: spreadsheet = "..." が正しいか。
        3. **共有設定**: client_email を「編集者」として招待したか。
        4. **列名**: シートの1行目が date, id, insight か。
        """)
