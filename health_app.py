import streamlit as st
import pandas as pd
import datetime
import os
import plotly.graph_objects as go

# 1. 페이지 설정 및 디자인 고도화 (강력한 다크 모드 고정 및 커서 제거)
st.set_page_config(page_title="우리 아이 건강기록", page_icon="🌡️", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경 강제 고정 */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
    }

    /* 모든 입력창의 흰색 배경 제거 및 테두리 스타일 강제 적용 */
    div[data-baseweb="select"], 
    div[data-baseweb="input"], 
    div[data-baseweb="textarea"],
    input, textarea, select {
        background-color: transparent !important;
        background: transparent !important;
        color: #ffffff !important;
        border: 1px solid #4e5d6c !important;
        border-radius: 8px !important;
    }

    /* 입력창 내부의 배경색까지 추적하여 제거 */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="base-input"] {
        background-color: transparent !important;
    }

    /* 커서(Caret) 박멸 */
    input, textarea, [contenteditable="true"] {
        caret-color: transparent !important;
    }

    /* 드롭다운 리스트(선택 팝업) 가독성 */
    div[role="listbox"] {
        background-color: #161b22 !important;
        color: #ffffff !important;
    }

    /* 라벨 및 텍스트 시인성 */
    label, p, span, .stMarkdown, [data-testid="stWidgetLabel"] p {
        color: #e6edf3 !important;
        font-weight: 500 !important;
    }

    /* 입력 섹션 박스 스타일 */
    .stExpander {
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        background-color: #161b22 !important;
    }

    /* 상태 카드 디자인 */
    .status-card {
        padding: 15px; border-radius: 15px; margin-bottom: 10px; color: white !important;
        min-height: 160px; display: flex; flex-direction: column; justify-content: space-between;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .status-normal { background-color: #1e3a2a !important; border: 1px solid #2e5a3a; }
    .status-caution { background-color: #4a3a1a !important; border: 1px solid #6a5a2a; }
    .status-danger { background-color: #3e1a1a !important; border: 1px solid #5e2a2a; }
    
    .card-temp { color: #ffffff !important; font-weight: 800; }

    /* 버튼 스타일 */
    .stButton > button {
        background-color: #238636 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 8px !important;
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

# 3. 퀵 기록 센터 (KST 반영)
now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
with st.expander("📝 새로운 건강 기록 입력 (클릭)", expanded=True):
    with st.form("health_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: name = st.selectbox("아이 이름", ["아율", "아인", "혁"])
        with c2: d = st.date_input("측정 날짜", now.date())
        
        st.markdown(f"🕒 **측정 시간** (현재 한국 시각: `{now.strftime('%H:%M')}`)")
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

        if st.form_submit_button("💾 기록 저장", use_container_width=True):
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
            prev_t = child_df.iloc[-2]['체온'] if len(child_df) > 1 else t
            diff = round(t - prev_t, 1)
            d_limit = 38.0 if c_name == "혁" else 39.0
            if t <= 37.5: bg, icon, txt = "status-normal", "🟢", "정상"
            elif t < d_limit: bg, icon, txt = "status-caution", "🟠", "미열"
            else: bg, icon, txt = "status-danger", "🔴", "고열"
            diff_text = f"{'↑' if diff > 0 else '↓' if diff < 0 else ''} {abs(diff)}°C"
            st.markdown(f'<div class="status-card {bg}"><div><div class="card-header">{child_icons[c_name]} {c_name} | {icon} {txt}</div><div class="card-temp">{t}°C</div><div class="card-delta">{diff_text}</div></div><div class="card-footer">🕒 {latest["날짜"]} {latest["시간"]}</div></div>', unsafe_allow_html=True)
        else: st.info(f"{c_name}: 기록 없음")

# 5. 아이별 그래프 추이 (Plotly)
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
            fig.add_trace(go.Scatter(x=f_df['축'], y=f_df['체온'], mode='lines+markers+text', line=dict(color='white', width=2.5), marker=dict(color=colors, size=12, line=dict(color='white', width=1.5)), text=f_df['체온'], textposition="top center", textfont=dict(color="white", size=13)))
            fig.update_layout(height=220, margin=dict(l=5, r=5, t=25, b=5), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(showgrid=False, color='white', tickfont=dict(size=9)), yaxis=dict(range=[34, 42], visible=False))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"chart_{c_name}")

# 6. 상세 기록
st.divider()
st.subheader("📋 상세 기록 리스트")
if not st.session_state.df.empty:
    tabs = st.tabs(["전체", "💖 아율", "💛 아인", "💙 혁"])
    for i, tab in enumerate(tabs):
        n_filter = [None, "아율", "아인", "혁"][i]
        with tab:
            display_df = st.session_state.df if n_filter is None else st.session_state.df[st.session_state.df['이름'] == n_filter]
            if not display_df.empty:
                d_df = display_df.copy().iloc[::-1]; d_df.insert(0, '선택', False)
                def style_temp(val):
                    limit = 38.0 if n_filter == "혁" else 39.0
                    color = '#4ade80' if val <= 37.5 else '#fbbf24' if val < limit else '#f87171'
                    return f'color: {color}; font-weight: bold;'
                st.data_editor(d_df.style.map(style_temp, subset=['체온']), hide_index=True, use_container_width=True, key=f"ed_{i}")
