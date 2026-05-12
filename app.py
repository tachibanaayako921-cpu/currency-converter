import streamlit as st
import datetime

# アプリの設定（タイトルなど）
st.set_page_config(page_title="外貨換算アプリ", layout="centered")

st.title("💴 外貨 → 円 換算アプリ")

# --- セッション状態で履歴を保持（リロードしても消えにくい設定） ---
if 'log_list' not in st.session_state:
    st.session_state.log_list = []

# --- 入力エリア ---
st.info("レートと外貨金額を入力して「計算」ボタンを押してください。")

col1, col2 = st.columns(2)

with col1:
    date = st.date_input("日付", datetime.date.today())
    currency = st.selectbox("通貨", ["USD (ドル)", "EUR (ユーロ)", "GBP (ポンド)", "AUD (豪ドル)"])
    
with col2:
    # 小数点第4位まで入力可能に設定
    rate = st.number_input("為替レート (1通貨あたり何円か)", min_value=0.0, step=0.0001, format="%.4f")
    amount = st.number_input("外貨金額", min_value=0.0, step=0.01)

# 丸め処理の選択
rounding = st.radio("端数処理", ["四捨五入", "切り上げ", "切り捨て"], horizontal=True)

# --- 計算ロジック ---
if st.button("計算する", type="primary"):
    if rate > 0 and amount > 0:
        raw_result = rate * amount
        
        # 計算（Pythonの組み込み関数やロジックを使用）
        if rounding == "切り上げ":
            import math
            result = math.ceil(raw_result)
        elif rounding == "切り捨て":
            result = int(raw_result)
        else:
            # 四捨五入
            result = int(raw_result + 0.5)
            
        # 結果表示
        st.success(f"結果: {result:,} 円")
        
        # 履歴に追加（最新が上に来るようにinsert）
        log_entry = f"{date} | {currency} {amount:,.2f} × レート{rate} = {result:,} 円"
        st.session_state.log_list.insert(0, log_entry)
    else:
        st.error("レートと金額を0より大きい数字で入力してください。")

# --- 履歴表示セクション ---
st.divider()
st.subheader("📝 計算履歴")

if st.session_state.log_list:
    if st.button("履歴をすべてクリア"):
        st.session_state.log_list = []
        st.rerun()

    for item in st.session_state.log_list:
        st.text(item)
else:
    st.write("履歴はありません。")

# --- 補足リンク ---
st.sidebar.markdown("### リンク")
st.sidebar.write("[三菱UFJリサーチ&コンサルティング 外貨相場](https://www.murc-kawasesouba.jp/fx/past/index.php)")
