import streamlit as st
import pandas as pd
import datetime
import os

# 1. 페이지 설정 및 디자인 보강
st.set_page_config(page_title="아율·아인·혁 건강기록", page_icon="🌡️", layout="wide")

# 가독성을 위한 커스텀 CSS (카드 배경색 및 텍스트 강조)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    /* 상태 카드 디자인 보강 */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    [data-testid="stMetricLabel"] { font-size: 1.2rem !important; font-weight: bold !important; color: #333 !important; }
    [data-testid="stMetricValue"] { font-size: 2rem !important; }
    
    /* 탭 디자인 */
    .stTabs [data-baseweb="tab"] { font-weight: bold; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌡️ 우리 아이 건강 관리 센터")

# 2. 파일 및 데이터 로드
DATA_FILE = "health_data.csv"

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["날짜", "시간", "이름", "체온", "약 종류", "용량", "특이사항"])

def save_data(df): df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

if 'df' not in st.session_state: st.session_state.df = load_data()

# 3. 입력 폼 (현재 시간 자동 반영)
now = datetime.datetime.now()
with st.expander("➕ 새로운 기록 추가하기 (현재 시간 자동 세팅)", expanded=True):
    with st.form("health_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: name = st.selectbox("아이 이름", ["아율", "아인", "혁"])
        with c2: 
            # 날짜를 현재 날짜로 자동 기본값 설정
            d = st.date_input("날짜", now.date())
            f_date = d.strftime("%y.%m.%d")

        st.write("🕒 복용 시간")
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            # 현재 시간에 맞춰 오전/오후 자동 선택
            current_ampm = "오후" if now.hour >= 12 else "오전"
            ampm = st.selectbox("오전/오후", ["오전", "오후"], index=0 if current_ampm == "오전" else 1)
        with t_col2:
            # 12시간제 변환 후 현재 시 자동 선택
            h12 = now.hour % 12
            h12 = 12 if h12 == 0 else h12
            hour = st.selectbox("시", [i for i in range(1, 13)], index=h12-1)
        with t_col3:
            # 현재 분에 가장 가까운 5분 단위 자동 선택
            m_idx = (now.minute // 5)
            minute = st.selectbox("분", [f"{i:02d}" for i in range(0, 60, 5)], index=m_idx)
        
        f_time = f"{ampm} {hour}:{minute}"

        c4, c5, c6 = st.columns(3)
        with c4: temp = st.number_input("체온 (℃)", 34.0, 42.0, 36.5, 0.1)
        with c5: med = st.selectbox("약 종류", ["선택 안 함", "맥시부펜", "세토펜", "아침약", "점심약", "저녁약", "기타"])
        with c6: vol = st.text_input("용량", placeholder="예: 5ml")
        
        note = st.text_area("특이사항 (증상 등)")
        
        if st.form_submit_button("💾 기록 저장 및 업데이트"):
            new_row = {"날짜": f_date, "시간": f_time, "이름": name, "체온": temp, "약 종류": med, "용량": vol, "특이사항": note}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.success(f"✅ {name}의 기록이 저장되었습니다!")
            st.rerun()

# 4. 현황 대시보드 (가독성 강화 카드)
st.subheader("📊 현재 아이들 상태 (최근 기록 기준)")
cols = st.columns(3)
child_icons = {"아율": "👧", "아인": "👧", "혁": "👶"}

for i, c_name in enumerate(["아율", "아인", "혁"]):
    child_df = st.session_state.df[st.session_state.df['이름'] == c_name]
    with cols[i]:
        if not child_df.empty:
            latest = child_df.iloc[-1]
            prev_temp = child_df.iloc[-2]['체온'] if len(child_df) > 1 else latest['체온']
            diff = round(latest['체온'] - prev_temp, 1)
            
            # 상태 메시지
            if latest['체온'] <= 37.5: status = "🟢 정상"
            elif latest['체온'] <= 38.9: status = "🟠 미열"
            else: status = "🔴 고열"
            
            # 카드 내부 가독성 높인 메트릭
            st.metric(label=f"{child_icons[c_name]} {c_name} | {status}", 
                      value=f"{latest['체온']}℃", 
                      delta=f"{diff}℃", 
                      delta_color="inverse")
            st.caption(f"📅 기록 시점: {latest['날짜']} {latest['시간']}")
        else:
            st.info(f"{child_icons[c_name]} {c_name}: 기록 없음")

# 5. 상세 기록 탭
st.divider()
tabs = st.tabs(["📋 전체", "💖 아율", "💛 아인", "💙 혁"])

def style_temp(val):
    if val <= 37.5: color = '#28a745'
    elif val <= 38.9: color = '#fd7e14'
    else: color = '#dc3545'
    return f'color: {color}; font-weight: bold;'

for i, tab in enumerate(tabs):
    name_filter = [None, "아율", "아인", "혁"][i]
    with tab:
        f_df = st.session_state.df if name_filter is None else st.session_state.df[st.session_state.df['이름'] == name_filter]
        if not f_df.empty:
            # 표와 다운로드 버튼
            csv = f_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(f"📥 {name_filter or '전체'} 엑셀 받기", csv, f"{name_filter or 'all'}.csv", "text/csv", key=f"dl_{i}")
            
            d_df = f_df.copy()
            d_df.insert(0, '선택', False)
            styled = d_df.iloc[::-1].style.map(style_temp, subset=['체온'])
            
            edited = st.data_editor(styled, hide_index=True, use_container_width=True, key=f"ed_{i}",
                                   column_config={"선택": st.column_config.CheckboxColumn("삭제", default=False)})
            
            if st.button("🗑️ 선택 항목 삭제", key=f"del_{i}"):
                # 선택된 행의 실제 인덱스 추출 후 삭제
                to_delete = edited[edited['선택'] == True]
                if not to_delete.empty:
                    # 데이터 매칭을 통한 안전한 삭제
                    for _, r in to_delete.iterrows():
                        st.session_state.df = st.session_state.df[
                            ~((st.session_state.df['날짜'] == r['날짜']) & 
                              (st.session_state.df['시간'] == r['시간']) & 
                              (st.session_state.df['체온'] == r['체온']))
                        ]
                    save_data(st.session_state.df)
                    st.rerun()
