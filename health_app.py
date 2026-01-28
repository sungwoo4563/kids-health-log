import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import json

# 1. 페이지 설정
st.set_page_config(page_title="아율·아인·혁 건강기록", page_icon="🌡️")
st.title("🌡️ 우리 아이 건강 관리")

# 2. 구글 시트 연결 (가장 안전한 방식)
try:
    # Secrets에서 설정값 가져오기
    conf = st.secrets["connections"]["gsheets"]
    
    # service_account가 문자열로 들어왔을 경우를 대비한 처리
    if isinstance(conf["service_account"], str):
        creds = json.loads(conf["service_account"])
    else:
        creds = conf["service_account"]
    
    # 정식 서비스 계정 권한으로 연결
    conn = st.connection("gsheets", type=GSheetsConnection, service_account=creds)
except Exception as e:
    st.error(f"⚠️ 설정 로드 실패: {e}")
    # 실패 시 기본 연결 시도
    conn = st.connection("gsheets", type=GSheetsConnection)

# 3. 데이터 불러오기
try:
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
        # 기존 데이터에 추가
        updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        # 구글 시트에 업데이트
        conn.update(data=updated_df)
        
        st.success(f"✅ {name}의 기록이 저장되었습니다! ({full_datetime})")
        st.rerun()
    except Exception as e:
        st.error(f"❌ 저장 실패: {e}")
        st.info("구글 시트에서 '서비스 계정 이메일'이 [편집자]로 초대되어 있는지 다시 확인해주세요!")

# 6. 최근 기록 표시
st.divider()
st.subheader("📋 최근 기록 (최신순)")
if not df.empty:
    display_df = df.sort_values(by="일시", ascending=False)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("아직 기록이 없습니다.")
