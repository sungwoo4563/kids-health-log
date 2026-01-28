import streamlit as st
from streamlit_gsheets import GSheetConnection
import pandas as pd
import datetime

# 페이지 설정
st.set_page_config(page_title="아이들 건강 관리", page_icon="🌡️")
st.title("🌡️ 실시간 아이 건강 기록 (공유형)")

# 구글 스프레드시트 연결 설정
conn = st.connection("gsheets", type=GSheetConnection)

# 기존 데이터 불러오기
data = conn.read(worksheet="Sheet1", ttl="0s") # 실시간 반영을 위해 캐시 해제

# 입력 폼
with st.form("health_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.selectbox("아이 이름", ["아율", "아인", "혁"])
        temp = st.number_input("현재 체온", min_value=35.0, max_value=42.0, value=36.5, step=0.1)
    with col2:
        medicine = st.text_input("복용한 약", placeholder="예: 맥시부펜 5ml")
        submit = st.form_submit_button("기록 저장 및 공유")

if submit:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    new_entry = pd.DataFrame([[now, name, temp, medicine]], columns=["시간", "이름", "체온", "복약내용"])
    
    # 데이터 합치기 및 구글 시트 업데이트
    updated_df = pd.concat([data, new_entry], ignore_index=True)
    conn.update(worksheet="Sheet1", data=updated_df)
    st.success("구글 시트에 성공적으로 저장되었습니다!")
    st.rerun()

# 기록 보기
st.divider()
st.subheader("📋 우리 아이 최근 기록")
st.dataframe(data.sort_values(by="시간", ascending=False), use_container_width=True)