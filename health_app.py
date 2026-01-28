import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# 1. 페이지 설정
st.set_page_config(page_title="아율·아인·혁 건강기록", page_icon="🌡️")
st.title("🌡️ 우리 아이 건강 관리")

# 2. 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. 데이터 불러오기
try:
    df = conn.read(ttl=0)
except Exception:
    df = pd.DataFrame(columns=["시간", "이름", "체온", "약 종류", "용량", "특이사항"])

# 4. 입력 폼
with st.form("health_form", clear_on_submit=True):
    st.subheader("📝 새로운 기록 입력")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.selectbox("아이 선택", ["아율", "아인", "혁"])
        # 소수점 한자리까지 입력 설정 (step=0.1)
        temp = st.number_input("현재 체온 (℃)", min_value=34.0, max_value=42.0, value=36.5, step=0.1, format="%.1f")
    
    with col2:
        # 약 종류 선택 메뉴
        med_type = st.selectbox("복용한 약", [
            "선택 안 함", 
            "맥시부펜(부루펜 계열)", 
            "세토펜현탁(타이레놀 계열)", 
            "아침약", "점심약", "저녁약", 
            "기타"
        ])
        # 용량 입력
        med_volume = st.text_input("용량 (예: 5ml, 1포)", placeholder="용량을 입력하세요")

    # 특이사항 입력
    note = st.text_area("특이사항 (증상이나 메모)", placeholder="예: 기침이 심함, 약 먹고 바로 잠듦")
    
    submit = st.form_submit_button("💾 기록 저장 및 공유")

# 5. 저장 로직
if submit:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    new_data = pd.DataFrame([{
        "시간": now, 
        "이름": name, 
        "체온": temp, 
        "약 종류": med_type, 
        "용량": med_volume, 
        "특이사항": note
    }])
    
    # 기존 데이터에 추가
    updated_df = pd.concat([df, new_data], ignore_index=True)
    
    # 구글 시트 업데이트
    try:
        conn.update(data=updated_df)
        st.success(f"✅ {name}의 기록이 저장되었습니다!")
        st.rerun()
    except Exception as e:
        st.error("저장에 실패했습니다. 구글 시트 권한을 확인해주세요.")

# 6. 기록 목록 표시
st.divider()
st.subheader("📋 최근 기록 (최신순)")
if not df.empty:
    display_df = df.sort_values(by="시간", ascending=False)
    # 아래 줄 맨 끝에 )가 있는지 확인하세요!
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("기록이 없습니다.")
