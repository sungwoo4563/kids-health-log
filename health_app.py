import streamlit as st
import pandas as pd
import datetime
import os

# 1. 페이지 설정
st.set_page_config(page_title="아율·아인·혁 건강기록", page_icon="🌡️", layout="wide")
st.title("🌡️ 우리 아이 건강 관리")

# 2. 파일 경로 설정
DATA_FILE = "health_data.csv"

# 3. 데이터 불러오기 및 저장 함수
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["날짜", "시간", "이름", "체온", "약 종류", "용량", "특이사항"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# 초기 데이터 로드
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# 4. 입력 폼 (들여쓰기 주의!)
with st.expander("📝 새로운 기록 입력하기", expanded=True):
    with st.form("health_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.selectbox("아이 선택", ["아율", "아인", "혁"])
        with col2:
            selected_date = st.date_input("날짜 선택", datetime.date.today())
            formatted_date = selected_date.strftime("%y.%m.%d")

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
        
        formatted_time = f"{ampm} {hour}:{minute}"

        col3, col4, col5 = st.columns(3)
        with col3:
            temp = st.number_input("체온 (℃)", min_value=34.0, max_value=42.0, value=36.5, step=0.1, format="%.1f")
        with col4:
            med_type = st.selectbox("복용한 약", ["선택 안 함", "맥시부펜(부루펜)", "세토펜(타이레놀)", "아침약", "점심약", "저녁약", "기타"])
        with col5:
            med_volume = st.text_input("용량", placeholder="예: 5ml")

        # ⚠️ 특이사항과 버튼이 st.form 안에 잘 들어와 있어야 합니다.
        note = st.text_area("특이사항", placeholder="증상이나 메모를 남겨주세요")
        submit = st.form_submit_button("💾 기록 저장")

# 5. 저장 로직 (폼 제출 시 실행)
if submit:
    new_row = {
        "날짜": formatted_date, "시간": formatted_time, "이름": name,
        "체온": temp, "약 종류": med_type, "용량": med_volume, "특이사항": note
    }
    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(st.session_state.df)
    st.success(f"✅ {name}의 기록이 저장되었습니다!")
    st.rerun()

# 6. 기록 관리 및 아이별 탭 분리
st.divider()
st.subheader("📋 기록 확인 및 관리")

def color_temp_text(val):
    if val <= 37.5: color = '#28a745' # 초록
    elif 37.6 <= val <= 38.9: color = '#fd7e14' # 주황
    else: color = '#dc3545' # 빨강
    return f'color: {color}; font-weight: bold;'

if not st.session_state.df.empty:
    tab_all, tab1, tab2, tab3 = st.tabs(["전체보기", "아율", "아인", "혁"])
    
    tabs = [tab_all, tab1, tab2, tab3]
    names = [None, "아율", "아인", "혁"]

    for i, tab in enumerate(tabs):
        with tab:
            if names[i] is None:
                filtered_df = st.session_state.df.copy()
            else:
                filtered_df = st.session_state.df[st.session_state.df['이름'] == names[i]].copy()

            if filtered_df.empty:
                st.info(f"{names[i] if names[i] else '전체'} 기록이 아직 없습니다.")
            else:
                csv = filtered_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(label=f"📥 {names[i] if names[i] else '전체'} 기록 내려받기", data=csv, file_name=f"건강기록_{names[i] if names[i] else '전체'}_{datetime.date.today()}.csv", key=f"dl_{i}")

                display_df = filtered_df.copy()
                display_df.insert(0, '선택', False)
                
                cols = ['선택', '날짜', '시간', '이름', '체온', '약 종류', '용량', '특이사항']
                display_df = display_df[cols]

                styled_df = display_df.iloc[::-1].style.map(color_temp_text, subset=['체온'])

                edited_df = st.data_editor(
                    styled_df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "선택": st.column_config.CheckboxColumn("선택", default=False),
                        "체온": st.column_config.NumberColumn("체온 (℃)", format="%.1f"),
                        "특이사항": st.column_config.TextColumn("특이사항", width="large")
                    },
                    disabled=[c for c in cols if c != '선택'],
                    key=f"editor_{i}"
                )

                if st.button(f"🗑️ {names[i] if names[i] else '전체'} 선택 항목 삭제", key=f"del_{i}"):
                    selected_rows = edited_df[edited_df['선택'] == True]
                    if not selected_rows.empty:
                        for _, row in selected_rows.iterrows():
                            st.session_state.df = st.session_state.df[
                                ~((st.session_state.df['날짜'] == row['날짜']) & 
                                  (st.session_state.df['시간'] == row['시간']) & 
                                  (st.session_state.df['이름'] == row['이름']) &
                                  (st.session_state.df['체온'] == row['체온']))
                            ]
                        save_data(st.session_state.df)
                        st.warning("선택한 기록이 삭제되었습니다.")
                        st.rerun()
else:
    st.info("아직 기록이 없습니다.")
