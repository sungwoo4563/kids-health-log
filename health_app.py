import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# 1. 페이지 설정
st.set_page_config(page_title="아율·아인·혁 건강기록", page_icon="🌡️")
st.title("🌡️ 우리 아이 건강 관리")

# 2. 구글 시트 연결
# 라이브러리 버전에 상관없이 가장 안정적인 기본 연결 방식을 사용합니다.
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. 데이터 불러오기
try:
    # 실시간 반영을 위해 캐시(ttl)를 0으로 설정
    df = conn.read(ttl=0)
    if df is None or df.empty:
        df = pd.DataFrame(columns=["일시", "이름", "체온", "약 종류", "용량", "특이사항"])
except Exception:
    df = pd.DataFrame(columns=["일시", "이름", "체온", "약 종류", "용량", "특이사항"])

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
    submit = st.form_submit_button("💾 기록 저장 및 공유")

# 5. 저장 로직
if submit:
    full_datetime = recorded_at.strftime('%Y-%m-%d %H:%M')
    new_row = {
        "일시": full_datetime, "이름": name, "체온": temp, 
        "약 종류": med_type, "용량": med_volume, "특이사항": note
    }
    
    try:
        # 새로운 행을 추가하여 업데이트
        new_data = pd.DataFrame([new_row])
        updated_df = pd.concat([df, new_data], ignore_index=True)
        conn.update(data=updated_df)
        
        st.success(f"✅ {name}의 기록이 저장되었습니다!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ 저장 실패: {e}")
        st.info("Secrets에 [connections.gsheets] 설정이 잘 되어있는지 확인해주세요.")

# 6. 최근 기록 표시
st.divider()
st.subheader("📋 최근 기록 (최신순)")
if not df.empty:
    if "일시" in df.columns:
        display_df = df.sort_values(by="일시", ascending=False)
    else:
        display_df = df
    st.dataframe(display_df, use_container_width=True, hide_index=True)
