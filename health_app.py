import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# 1. 페이지 설정
st.set_page_config(page_title="아율·아인·혁 건강기록", page_icon="🌡️")
st.title("🌡️ 우리 아이 건강 관리 (공유형)")

# 2. 구글 시트 연결 (가장 단순한 방식으로 변경)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. 데이터 불러오기 (에러 방지 처리를 강화했습니다)
try:
    # worksheet 이름을 지정하지 않으면 자동으로 첫 번째 시트를 가져옵니다.
    df = conn.read(ttl=0) 
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다. (Secrets 설정을 확인해주세요)")
    df = pd.DataFrame(columns=["시간", "이름", "체온", "복약내용"])

# 4. 입력 화면
with st.form("health_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.selectbox("아이 선택", ["아율", "아인", "혁"])
        temp = st.number_input("현재 체온 (℃)", min_value=34.0, max_value=42.0, value=36.5, step=0.1)
    with col2:
        medicine = st.text_input("복용한 약 / 특이사항", placeholder="예: 맥시부펜 5ml")
        submit = st.form_submit_button("💾 기록 저장")

# 5. 저장 로직
if submit:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    new_data = pd.DataFrame([{"시간": now, "이름": name, "체온": temp, "복약내용": medicine}])
    
    # 기존 데이터와 합치기
    updated_df = pd.concat([df, new_data], ignore_index=True)
    
    # 구글 시트 업데이트
    try:
        conn.update(data=updated_df)
        st.success(f"✅ {name}의 기록이 저장되었습니다!")
        st.rerun()
    except Exception as e:
        st.error("저장에 실패했습니다. 공유 권한이 '편집자'인지 확인해주세요.")

# 6. 목록 표시
st.divider()
st.subheader("📋 최근 기록 확인")
if not df.empty:
    st.dataframe(df.sort_values(by="시간", ascending=False), use_container_width=True)
else:
    st.info("아직 기록이 없습니다.")
