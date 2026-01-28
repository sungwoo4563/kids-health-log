import streamlit as st
import pandas as pd
import datetime
import os
import plotly.graph_objects as go

# 1. 페이지 설정 및 디자인 고도화
st.set_page_config(page_title="우리 아이 건강기록", page_icon="🌡️", layout="wide")

st.markdown("""
    <style>
    /* 1. 전체 배경 및 기본 텍스트: 다크 모드 강제 */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0d1117 !important;
        color: #ffffff !important;
    }

    /* -----------------------------------------------------------
       [기록 저장 버튼 수정] 
       폼 제출 버튼(stFormSubmitButton)을 직접 타격하여 배경 제거
    ----------------------------------------------------------- */
    div[data-testid="stFormSubmitButton"] > button {
        background-color: transparent !important; /* 배경 투명 */
        color: #ffffff !important; /* 글자 흰색 */
        border: 1px solid #ffffff !important; /* 흰색 테두리 */
        font-weight: bold !important;
        border-radius: 8px !important;
        width: 100% !important;
        height: 3.5em !important;
        box-shadow: none !important;
        text-shadow: none !important;
    }
    
    /* 버튼 눌렀을 때(Active) 효과 */
    div[data-testid="stFormSubmitButton"] > button:active,
    div[data-testid="stFormSubmitButton"] > button:focus:not(:active) {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-color: #4ade80 !important;
        color: #4ade80 !important;
    }

    /* -----------------------------------------------------------
       [체온 기록 (Number Input) 통합 테두리]
    ----------------------------------------------------------- */
    /* 1. 숫자 입력창의 전체 컨테이너(껍데기)에만 테두리를 줍니다. */
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {
        border: 1px solid #ffffff !important;
        border-radius: 8px !important;
        background-color: transparent !important;
        padding-right: 0px !important; /* 버튼과 간격 없애기 */
    }

    /* 2. 내부의 실제 입력칸(input)은 테두리 제거 */
    div[data-testid="stNumberInput"] input {
        border: none !important;
        background-color: transparent !important;
    }

    /* 3. +/- 버튼들이 들어있는 컨테이너 배경/테두리 제거 */
    div[data-testid="stNumberInput"] div[data-baseweb="input"] > div {
        border: none !important;
        background-color: transparent !important;
    }

    /* 4. +/- 개별 버튼 디자인: 배경 투명, 글자 흰색, 왼쪽 선만 살짝(구분용) */
    div[data-testid="stNumberInputStepDown"], 
    div[data-testid="stNumberInputStepUp"] {
        background-color: transparent !important;
        border: none !important;
        color: #ffffff !important;
        margin: 0 !important;
    }
    
    /* +/- 버튼 사이의 구분선도 제거하여 완전 통일감 */
    div[data-testid="stNumberInputStepDown"] {
        border-right: 1px solid rgba(255,255,255,0.2) !important; /* 버튼끼리만 살짝 구분 */
    }

    /* -----------------------------------------------------------
       [나머지 입력창 디자인 유지]
    ----------------------------------------------------------- */
    div[data-baseweb="select"], 
    div[data-baseweb="input"], 
    div[data-baseweb="textarea"] {
        background-color: transparent !important;
        border: 1px solid #ffffff !important; 
        border-radius: 8px !important;
        box-shadow: none !important;
    }
    
    /* 중복 테두리 방지 */
    div[data-baseweb="base-input"], 
    input, textarea, select {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }

    /* -----------------------------------------------------------
       [커서 박멸 유지]
    ----------------------------------------------------------- */
    input, textarea { caret-color: transparent !important; }
    div[data-baseweb="select"] input { opacity: 0 !important; width: 1px !important; }
    * { -webkit-tap-highlight-color: transparent !important; }

    /* 텍스트 색상 및 라벨 */
    input, textarea, div[data-baseweb="select"] span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    label, p, span, [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    /* 상세 기록 표 */
    [data-testid="stDataFrame"], [data-testid="stTable"], .stDataFrame {
        border: 1px solid #ffffff !important;
        background-color: transparent !important;
    }
    [data-testid="stTable"] td, [data-testid="stTable"] th {
        border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌡️ 우리 아이 건강 관리 센터")

# 2. 데이터 관리
DATA_FILE = "health_data.csv"
def load_data():
    if os.path.exists(DATA_FILE):
        try: return pd.read_csv(DATA_FILE)
        except: return pd.DataFrame(columns=["날짜", "시간", "이름", "체온", "약 종류", "용량", "특이사항"])
    return pd.DataFrame(columns=["날짜", "시간", "이름", "체온", "약 종류", "용량", "특이사항"])

def save_data(df): df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

if 'df' not in st.session_state: st.session_state.df = load_data()

# 3. 퀵 기록 센터
now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
with st.expander("📝 새로운 건강 기록 입력", expanded=True):
    with st.form("health_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: name = st.selectbox("아이 이름", ["아율", "아인", "혁"])
        with c2: d = st.date_input("측정 날짜", now.date())
        
        st.markdown(f"🕒 **측정 시간** (KST: `{now.strftime('%H:%M')}`)")
        t1, t2, t3 = st.columns(3)
        with t1: ampm = st.selectbox("오전/오후", ["오전", "오후"], index=(0 if now.hour < 12 else 1))
        with t2: 
            h12_val = 12 if now.hour % 12 == 0 else now.hour % 12
            hour = st.selectbox("시", [i for i in range(1, 13)], index=h12_val-1)
        with t3: minute = st.selectbox("분", [f"{i:02d}" for i in range(60)], index=now.minute)
        
        st.divider()
        c3, c4, c5 = st.columns(3)
        with c3: temp = st.number_input("🌡️ 체온", 30.0, 42.0, 36.5, 0.1)
        with c4: med = st.selectbox("💊 약 종류", ["선택 안 함", "맥시부펜", "세토펜", "아침약", "점심약", "저녁약", "기타"])
        with c5: vol = st.text_input("💉 용량", placeholder="예: 5ml")
        note = st.text_area("🗒️ 특이사항")

        # 교차 복용 체크
        child_history = st.session_state.df[st.session_state.df['이름'] == name]
        if not child_history.empty and med in ["맥시부펜", "세토펜"]:
            med_history = child_history[child_history['약 종류'] != "선택 안 함"]
            if not med_history.empty:
                last_med = med_history.iloc[-1]['약 종류']
                if last_med == med:
                    st.warning(f"⚠️ 주의: {name}가 마지막으로 복용한 약도 **{last_med}**입니다!")

        if st.form_submit_button("💾 기록 저장"):
            f_date = d.strftime("%y.%m.%d")
            f_time = f"{ampm} {hour}:{minute}"
            new_row = {"날짜": f_date, "시간": f_time, "이름": name, "체온": temp, "약 종류": med, "용량": vol, "특이사항": note}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.rerun()

# 4. 현황 대시보드
st.divider()
st.subheader("📊 현재 상태 요약")
cols = st.columns(3)
child_names = ["아율", "아인", "혁"]
child_icons = {"아율": "👧", "아인": "👧", "혁": "👶"}

for i, c_name in enumerate(child_names):
    child_df = st.session_state.df[st.session_state.df['이름'] == c_name]
    with cols[i]:
        if not child_df.empty:
            latest = child_df.iloc[-1]; t = latest["체온"]
            d_limit = 38.0 if c_name == "혁" else 39.0
            bg = "#1e3a2a" if t <= 37.5 else "#4a3a1a" if t < d_limit else "#3e1a1a"
            st.markdown(f'<div style="background-color:{bg}; padding:15px; border:1px solid #ffffff; border-radius:15px; color:white;"><div style="font-weight:bold;">{child_icons[c_name]} {c_name}</div><div style="font-size:2rem; font-weight:800;">{t}°C</div><div style="font-size:0.8rem; opacity:0.8;">🕒 {latest["시간"]}</div></div>', unsafe_allow_html=True)
        else: st.info(f"{c_name}: 기록 없음")

# 5. 아이별 그래프 (Plotly)
st.subheader("📈 최근 체온 흐름")
g_cols = st.columns(3)
for i, c_name in enumerate(child_names):
    with g_cols[i]:
        f_df = st.session_state.df[st.session_state.df['이름'] == c_name].tail(7)
        if not f_df.empty:
            f_df['축'] = f_df['날짜'].str[3:] + "<br>" + f_df['시간'].str.split(' ').str[-1]
            d_limit = 38.0 if c_name == "혁" else 39.0
            colors = ['#4ade80' if t <= 37.5 else '#fbbf24' if t < d_limit else '#f87171' for t in f_df['체온']]
            fig = go.Figure()
            fig.add_hrect(y0=34, y1=37.5, fillcolor="#28a745", opacity=0.15, line_width=0)
            fig.add_hrect(y0=37.5, y1=d_limit, fillcolor="#fd7e14", opacity=0.15, line_width=0)
            fig.add_hrect(y0=d_limit, y1=42, fillcolor="#dc3545", opacity=0.15, line_width=0)
            fig.add_trace(go.Scatter(x=f_df['축'], y=f_df['체온'], mode='lines+markers+text', line=dict(color='white', width=2), marker=dict(color=colors, size=10, line=dict(color='white', width=1)), text=f_df['체온'], textposition="top center", textfont=dict(color="white", size=11)))
            fig.update_layout(height=180, margin=dict(l=5, r=5, t=25, b=5), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(showgrid=False, color='white', tickfont=dict(size=9)), yaxis=dict(range=[34, 42], visible=False))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"chart_{c_name}")

# 6. 상세 기록 리스트 (소수점 정리 & 단일 테두리)
st.divider()
st.subheader("📋 상세 기록")
if not st.session_state.df.empty:
    tabs = st.tabs(["전체", "💖 아율", "💛 아인", "💙 혁"])
    for i, tab in enumerate(tabs):
        n_filter = [None, "아율", "아인", "혁"][i]
        with tab:
            display_df = st.session_state.df if n_filter is None else st.session_state.df[st.session_state.df['이름'] == n_filter]
            if not display_df.empty:
                show_df = display_df.copy().iloc[::-1]
                show_df['체온'] = show_df['체온'].apply(lambda x: f"{float(x):.1f}")
                st.table(show_df)
