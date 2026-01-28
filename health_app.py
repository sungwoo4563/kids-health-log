import streamlit as st
import pandas as pd
import datetime
import os
import plotly.graph_objects as go

# 1. 페이지 설정 및 디자인 (그래프 중앙 정렬 + 모든 디자인 통합)
st.set_page_config(page_title="우리 아이 건강기록", page_icon="🌡️", layout="wide")

st.markdown("""
    <style>
    /* 1. 기본 다크 모드 설정 */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0d1117 !important;
        color: #ffffff !important;
    }

    /* 2. [핵심 수정] 그래프(Plotly) 테두리 및 중앙 정렬 
       - display: flex와 justify-content: center로 내부 그래프를 강제 중앙 정렬
    */
    [data-testid="stPlotlyChart"] {
        border: 2px solid #ffffff !important;
        border-radius: 15px !important;
        padding: 5px !important; /* 패딩을 약간 줄여서 꽉 차게 */
        background-color: #0d1117 !important;
        margin-bottom: 10px !important;
        display: flex !important;       /* 플렉스 박스 적용 */
        justify-content: center !important; /* 가로 중앙 정렬 */
        align-items: center !important;     /* 세로 중앙 정렬 */
    }
    /* 그래프 내부 컨테이너도 꽉 차게 */
    [data-testid="stPlotlyChart"] > div {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
    }

    /* 3. 선택창 텍스트 가독성 (흰색 강제) */
    div[data-baseweb="select"] span, 
    div[data-baseweb="select"] div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    div[data-baseweb="select"] svg { fill: #ffffff !important; }

    /* 4. 커서 박멸 (검색창 숨김 + 입력창 투명화 트릭) */
    div[data-baseweb="select"] input { opacity: 0 !important; width: 0px !important; }
    
    input[type="text"], textarea {
        color: transparent !important;
        text-shadow: 0 0 0 #ffffff !important;
        caret-color: transparent !important;
        cursor: pointer !important;
    }

    /* 5. 입력창 디자인 (검은 배경 + 흰색 테두리) */
    div[data-baseweb="select"], 
    div[data-baseweb="input"], 
    div[data-baseweb="textarea"] {
        background-color: #0d1117 !important;
        border: 2px solid #ffffff !important;
        border-radius: 8px !important;
    }

    /* 6. 내부 중복 테두리 제거 */
    div[data-baseweb="base-input"], 
    div[data-baseweb="select"] > div {
        border: none !important;
        background-color: transparent !important;
    }

    /* 7. 기록 저장 버튼 */
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #0d1117 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    
    /* 8. 체온 입력기 통합 테두리 */
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {
        background-color: #0d1117 !important;
        border: 2px solid #ffffff !important;
        padding-right: 0 !important;
    }
    div[data-testid="stNumberInput"] input {
        border: none !important;
        background-color: #0d1117 !important;
        text-shadow: 0 0 0 #ffffff !important;
        color: transparent !important;
    }
    div[data-testid="stNumberInputStepDown"], 
    div[data-testid="stNumberInputStepUp"] {
        background-color: #0d1117 !important;
        border-left: 1px solid rgba(255,255,255,0.3) !important;
        color: #ffffff !important;
    }

    /* 9. 표 및 라벨 스타일 */
    [data-testid="stDataFrame"], [data-testid="stTable"], .stDataFrame {
        border: 1px solid #ffffff !important;
        background-color: #0d1117 !important;
    }
    [data-testid="stTable"] td, [data-testid="stTable"] th {
        color: #ffffff !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important;
        background-color: #0d1117 !important;
    }
    label, p, span, [data-testid="stWidgetLabel"] p, h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    hr { border-color: #ffffff !important; opacity: 0.3 !important; }

    * { -webkit-tap-highlight-color: transparent !important; }
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

        if med in ["맥시부펜", "세토펜"]:
            child_history = st.session_state.df[st.session_state.df['이름'] == name]
            if not child_history.empty:
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
st.divider()
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
            
            # [수정] 좌우 여백(l, r)을 15로 똑같이 맞춰서 물리적 중앙 정렬
            fig.update_layout(
                title=dict(text=f"<b>{c_name}</b>", font=dict(size=18, color="white"), x=0.5, xanchor='center'),
                height=200, 
                margin=dict(l=15, r=15, t=40, b=10), # 좌우 여백 균일화
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                showlegend=False, 
                xaxis=dict(showgrid=False, color='white', tickfont=dict(size=9)), 
                yaxis=dict(range=[34, 42], visible=False)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"chart_{c_name}")

# 6. 상세 기록 리스트
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
