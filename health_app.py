import streamlit as st
import pandas as pd
import datetime
import os

# 1. 페이지 설정
st.set_page_config(page_title="아율·아인·혁 건강기록", page_icon="🌡️")
st.title("🌡️ 우리 아이 건강 관리")

# 2. 파일 경로 설정
DATA_FILE = "health_data.csv"

# 3. 데이터 불러오기 함수
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["날짜", "시간", "이름", "체온", "약 종류", "용량", "특이사항"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

df = load_data()

# 4. 입력 폼
with st.form("health_form", clear_on_submit=True):
    st.subheader("📝 새로운 기록 입력")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.selectbox("아이 선택", ["아율", "아인", "혁"])
    with col2:
        selected_date = st.date_input("날짜 선택", datetime.date.today())
        formatted_date = selected_date.strftime("%y년 %m월 %d일")

    st.write("🕒 복용 시간")
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        ampm = st.selectbox("오전/오후", ["오전", "오후"])
    with t_col2:
        current_hour = datetime.datetime.now().hour
        default_hour = current_hour % 12 if current_hour % 12 != 0 else 12
        hour = st.selectbox("시", [i for i in range(1, 13)], index=default_hour - 1)
    with t_col3:
        minute = st.selectbox("분", [f"{i:02d}" for i in range(0, 60, 5)])
    
    formatted_time = f"{ampm} {hour}시 {minute}분"

    col3, col4, col5 = st.columns(3)
    with col3:
        temp = st.number_input("체온 (℃)", min_value=34.0, max_value=42.0, value=36.5, step=0.1, format="%.1f")
    with col4:
        med_type = st.selectbox("복용한 약", ["선택 안 함", "맥시부펜(부루펜)", "세토펜(타이레놀)", "아침약", "점심약", "저녁약", "기타"])
    with col5:
        med_volume = st.text_input("용량", placeholder="예: 5ml")

    note = st.text_area("특이사항", placeholder="증상이나 메모를 남겨주세요")
    submit = st.form_submit_button("💾 기록 저장")

# 5. 저장 로직
if submit:
    new_row = {
        "날짜": formatted_date, "시간": formatted_time, "이름": name,
        "체온": temp, "약 종류": med_type, "용량": med_volume, "특이사항": note
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)
    st.success(f"✅ 저장 완료!")
    st.rerun()

# 6. 전체 기록 확인 및 삭제 기능
st.divider()
st.subheader("📋 전체 기록 확인")

if not df.empty:
    # 상단 버튼 레이아웃
    btn_col1, btn_col2 = st.columns([1, 1])
    
    with btn_col1:
        # 엑셀 다운로드 버튼
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 전체 기록 엑셀 내려받기",
            data=csv,
            file_name=f"건강기록_{datetime.date.today()}.csv",
            mime="text/csv",
        )
    
    with btn_col2:
        # 최근 기록 1개 삭제 버튼
        if st.button("🗑️ 방금 입력한 기록 삭제"):
            if len(df) > 0:
                df = df.drop(df.index[-1])
                save_data(df)
                st.warning("마지막 기록이 삭제되었습니다.")
                st.rerun()

    # 데이터 표시 (최신순)
    st.write("💡 표에서 내용을 확인하세요 (최신순)")
    st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
    
    # 선택 삭제 기능 (고급)
    with st.expander("⚠️ 특정 기록 골라서 삭제하기"):
        delete_idx = st.number_input("삭제할 행 번호 입력 (표의 순서가 아님)", min_value=0, max_value=len(df)-1, step=1)
        if st.button("선택한 번호 삭제"):
            df = df.drop(df.index[delete_idx])
            save_data(df)
            st.error(f"{delete_idx}번 기록이 삭제되었습니다.")
            st.rerun()
else:
    st.info("아직 기록이 없습니다.")
