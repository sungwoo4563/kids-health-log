import streamlit as st
import pandas as pd
import datetime
import os

# 1. 페이지 설정
st.set_page_config(page_title="아율·아인·혁 건강기록", page_icon="🌡️")
st.title("🌡️ 우리 아이 건강 관리 (로컬 저장 모드)")

# 2. 파일 경로 설정 (앱 폴더 안에 저장)
DATA_FILE = "health_data.csv"

# 3. 데이터 불러오기 함수
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # 파일이 없으면 제목줄만 있는 데이터프레임 생성
        return pd.DataFrame(columns=["일시", "이름", "체온", "약 종류", "용량", "특이사항"])

df = load_data()

# 4. 입력 폼
with st.form("health_form", clear_on_submit=True):
    st.subheader("📝 새로운 기록 입력")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.selectbox("아이 선택", ["아율", "아인", "혁"])
        recorded_at = st.datetime_input("언제 먹였나요?", datetime.datetime.now())
        
    with col2:
        temp = st.number_input("현재 체온 (℃)", min_value=34.0, max_value=42.0, value=36.5, step=0.1, format="%.1f")
        med_type = st.selectbox("복용한 약", [
            "선택 안 함", "맥시부펜(부루펜)", "세토펜(타이레놀)", 
            "아침약", "점심약", "저녁약", "기타"
        ])
        med_volume = st.text_input("용량 (예: 5ml, 1포)", placeholder="용량을 입력하세요")

    note = st.text_area("특이사항", placeholder="증상이나 메모를 남겨주세요")
    submit = st.form_submit_button("💾 기록 저장")

# 5. 저장 로직 (로컬 파일에 쓰기)
if submit:
    full_datetime = recorded_at.strftime('%Y-%m-%d %H:%M')
    new_row = {
        "일시": full_datetime, "이름": name, "체온": temp, 
        "약 종류": med_type, "용량": med_volume, "특이사항": note
    }
    
    # 데이터 추가
    new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    # CSV 파일로 저장
    new_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
    
    st.success(f"✅ {name}의 기록이 로컬에 저장되었습니다!")
    st.rerun()

# 6. 최근 기록 표시
st.divider()
st.subheader("📋 최근 기록 (최신순)")
if not df.empty:
    # 최신순 정렬
    display_df = df.sort_values(by="일시", ascending=False)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("아직 기록이 없습니다.")
