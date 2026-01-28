import streamlit as st
import pandas as pd
import datetime
import os

# 1. 페이지 설정 및 디자인 테마
st.set_page_config(page_title="아율·아인·혁 건강기록", page_icon="🌡️", layout="wide")

# CSS를 이용한 커스텀 디자인 적용
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
        gap: 1px;
        padding: 10px;
    }
    .stTabs [aria-selected="true"] { background-color: #007bff !important; color: white !important; }
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

# 3. 입력 폼 (섹션 분리)
with st.expander("➕ 새로운 기록 추가하기", expanded=False):
    with st.form("health_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1: name = st.selectbox("아이 이름", ["아율", "아인", "혁"])
        with c2: 
            d = st.date_input("날짜", datetime.date.today())
            f_date = d.strftime("%y.%m.%d")
        with c3:
            ampm = st.selectbox("오전/오후", ["오전", "오후"])
            t = st.selectbox("시간", [f"{i}:00" for i in range(1, 13)] + [f"{i}:30" for i in range(1, 13)])
            f_time = f"{ampm} {t}"

        c4, c5, c6 = st.columns(3)
        with c4: temp = st.number_input("체온 (℃)", 34.0, 42.0, 36.5, 0.1)
        with c5: med = st.selectbox("약 종류", ["선택 안 함", "맥시부펜", "세토펜", "감기약", "기타"])
        with c6: vol = st.text_input("용량", placeholder="5ml")
        
        note = st.text_area("특이사항")
        if st.form_submit_button("💾 기록 저장"):
            new = pd.DataFrame([{"날짜": f_date, "시간": f_time, "이름": name, "체온": temp, "약 종류": med, "용량": vol, "특이사항": note}])
            st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)
            save_data(st.session_state.df)
            st.success("저장되었습니다!")
            st.rerun()

# 4. 현황 대시보드 (직관적인 요약)
st.subheader("📊 현재 아이들 상태")
cols = st.columns(3)
child_icons = {"아율": "👧", "아인": "👧", "혁": "👶"}

for i, c_name in enumerate(["아율", "아인", "혁"]):
    child_df = st.session_state.df[st.session_state.df['이름'] == c_name]
    with cols[i]:
        if not child_df.empty:
            latest = child_df.iloc[-1]
            prev_temp = child_df.iloc[-2]['체온'] if len(child_df) > 1 else latest['체온']
            diff = round(latest['체온'] - prev_temp, 1)
            
            # 온도에 따른 색상 강조
            status = "정상" if latest['체온'] <= 37.5 else "미열" if latest['체온'] <= 38.9 else "고열"
            st.metric(label=f"{child_icons[c_name]} {c_name} ({status})", value=f"{latest['체온']}℃", delta=f"{diff}℃", delta_color="inverse")
            st.caption(f"최근: {latest['날짜']} {latest['시간']}")
        else:
            st.info(f"{c_name} 기록 없음")

# 5. 상세 기록 (탭 디자인)
st.divider()
tab_all, tab1, tab2, tab3 = st.tabs(["📋 전체 로그", "💖 아율", "💛 아인", "💙 혁"])

def color_temp(val):
    color = '#28a745' if val <= 37.5 else '#fd7e14' if val <= 38.9 else '#dc3545'
    return f'color: {color}; font-weight: bold;'

for i, tab in enumerate([tab_all, tab1, tab2, tab3]):
    name_filter = [None, "아율", "아인", "혁"][i]
    with tab:
        f_df = st.session_state.df if name_filter is None else st.session_state.df[st.session_state.df['이름'] == name_filter]
        
        if not f_df.empty:
            # 상단 버튼 구성
            b1, b2 = st.columns([4, 1])
            with b2:
                csv = f_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button("📥 엑셀", csv, f"{name_filter or '전체'}.csv", "text/csv", key=f"dl_{i}")
            
            # 표 디자인
            d_df = f_df.copy()
            d_df.insert(0, '선택', False)
            styled = d_df.iloc[::-1].style.map(color_temp, subset=['체온'])
            
            edited = st.data_editor(styled, hide_index=True, use_container_width=True, key=f"ed_{i}",
                                   column_config={"선택": st.column_config.CheckboxColumn("삭제", default=False),
                                                 "특이사항": st.column_config.TextColumn("특이사항", width="large")})
            
            if st.button("🗑️ 선택 항목 삭제", key=f"del_{i}"):
                indices_to_drop = edited[edited['선택'] == True].index
                # 실제 원본 인덱스를 찾아 삭제 (역순 표시 고려)
                orig_indices = f_df.iloc[::-1].iloc[indices_to_drop].index
                st.session_state.df = st.session_state.df.drop(orig_indices)
                save_data(st.session_state.df)
                st.rerun()
