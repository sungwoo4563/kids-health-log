import streamlit as st
import pandas as pd
import datetime
import os

# 1. 페이지 설정
st.set_page_config(page_title="아율·아인·혁 건강기록", page_icon="🌡️")
st.title("🌡️ 우리 아이 건강 관리")

# 2. 파일 경로 설정
DATA_FILE = "health_data.csv"

# 3. 데이터 불러오기 및 저장 함수
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # '일시' 제거, 날짜/시간을 앞쪽으로, 특이사항을 뒤쪽으로 구성
        return pd.DataFrame(columns=["날짜", "시간", "이름", "체온", "약 종류", "용량", "특이사항"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# 초기 데이터 로드
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# 4. 입력 폼
with st.form("health_form", clear_on_submit=True):
    st.subheader("📝 새로운 기록 입력")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.selectbox("아이 선택", ["아율", "아인", "혁"])
    with col2:
        selected_date = st.date_input("날짜 선택", datetime.date.today())
        # 성우님이 요청하신 26년 01월 28일 형식
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

if submit:
    new_row = {
        "날짜": formatted_date, "시간": formatted_time, "이름": name,
        "체온": temp, "약 종류": med_type, "용량": med_volume, "특이사항": note
    }
    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(st.session_state.df)
    st.success("✅ 저장되었습니다!")
    st.rerun()

# 5. 기록 관리 (체크박스 삭제 포함)
st.divider()
st.subheader("📋 기록 관리 및 삭제")

if not st.session_state.df.empty:
    # 엑셀 다운로드 버튼
    csv = st.session_state.df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="📥 전체 기록 엑셀 내려받기",
        data=csv,
        file_name=f"건강기록_{datetime.date.today()}.csv",
        mime="text/csv",
    )
    
    st.write("💡 삭제할 항목을 왼쪽 체크박스에서 선택하고 아래 '선택 항목 삭제' 버튼을 누르세요.")
    
    # 표시용 데이터프레임 구성 (날짜, 시간 순서 및 선택 박스 추가)
    display_df = st.session_state.df.copy()
    display_df.insert(0, '선택', False) # 맨 앞에 체크박스용 열 추가

    # 컬럼 순서 강제 지정 (선택, 날짜, 시간, 이름, 체온, 약 종류, 용량, 특이사항)
    cols = ['선택', '날짜', '시간', '이름', '체온', '약 종류', '용량', '특이사항']
    display_df = display_df[cols]

    # 데이터 에디터 실행
    edited_df = st.data_editor(
        display_df.iloc[::-1], # 최신 기록이 위로 오게 역순 표시
        hide_index=True,
        use_container_width=True,
        column_config={
            "선택": st.column_config.CheckboxColumn("선택", default=False),
            "특이사항": st.column_config.TextColumn("특이사항", width="large")
        },
        disabled=[c for c in cols if c != '선택'] # 선택 열만 수정 가능하게 설정
    )

    # 삭제 버튼 로직
    if st.button("🗑️ 선택한 항목 삭제"):
        selected_rows = edited_df[edited_df['선택'] == True]
        if not selected_rows.empty:
            # 선택된 행들을 원본 데이터에서 제외
            for _, row in selected_rows.iterrows():
                st.session_state.df = st.session_state.df[
                    ~((st.session_state.df['날짜'] == row['날짜']) & 
                      (st.session_state.df['시간'] == row['시간']) & 
                      (st.session_state.df['이름'] == row['이름']) &
                      (st.session_state.df['체온'] == row['체온']) &
                      (st.session_state.df['특이사항'] == row['특이사항']))
                ]
            save_data(st.session_state.df)
            st.warning("선택한 기록이 삭제되었습니다.")
            st.rerun()
        else:
            st.info("삭제할 항목을 먼저 선택해주세요.")
else:
    st.info("아직 기록이 없습니다.")
