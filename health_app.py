import streamlit as st
import pandas as pd
import datetime
import os
import plotly.graph_objects as go

# 1. 페이지 설정 및 모바일 최적화 CSS
st.set_page_config(page_title="건강기록", page_icon="🌡️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    /* 모바일에서 텍스트가 너무 크지 않게 조절 */
    @media (max-width: 640px) {
        .card-temp { font-size: 2.2rem !important; }
        .card-header { font-size: 0.9rem !important; }
        h1 { font-size: 1.5rem !important; }
    }
    .stExpander {
        border: 2px solid #4e5d6c !important;
        border-radius: 12px !important;
        background-color: #161b22 !important;
    }
    .status-card {
        padding: 15px; border-radius: 15px; margin-bottom: 10px; color: white;
        min-height: 160px; display: flex; flex-direction: column; justify-content: space-between;
    }
    .status-normal { background-color: #1e3a2a; border: 1px solid #2e5a3a; }
    .status-caution { background-color: #4a3a1a; border: 1px solid #6a5a2a; }
    .status-danger { background-color: #3e1a1a; border: 1px solid #5e2a2a; }
    
    .card-header { font-size: 1.1rem; font-weight: bold; }
    .card-temp { font-size: 2.8rem; font-weight: 800; margin: 5px 0; }
    .card-delta { font-size: 0.9rem; background-color: rgba(255,255,255,0.1); padding: 3px 8px; border-radius: 15px; }
    .card-footer { font-size: 0.8rem; opacity: 0.6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌡️ 우리 아이 건강 관리 센터")

# 2. 데이터 관리 로직 (기존 유지)
DATA_FILE = "health_data.csv"
def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["날짜", "시간", "이름", "체온", "약 종류", "용량", "특이사항"])

def save_data(df): df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

if 'df' not in st.session_state: st.session_state.df = load_data()

# 3. 퀵 기록 센터 (모바일에서는 열별 배치가 자동으로 수직 정렬됨)
now = datetime.datetime.now()
with st.expander("📝 새로운 건강 기록 입력 (클릭)", expanded=True):
    with st.form("health_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: name = st.selectbox("아이 이름", ["아율", "아인", "혁"])
        with c2: 
            d = st.date_input("측정 날짜", now.date())
            f_date = d.strftime("%y.%m.%d")
        
        # 시간 선택을 더 간소화 (모바일 터치 최적화)
        st.write("🕒 측정 시간")
        t1, t2, t3 = st.columns(3)
        with t1: ampm = st.selectbox("오전/오후", ["오전", "오후"], index=(0 if now.hour < 12 else 1))
        with t2: 
            h12 = 12 if now.hour % 12 == 0 else now.hour % 12
            hour = st.selectbox("시", [i for i in range(1, 13)], index=h12-1)
        with t3:
            minute = st.selectbox("분", [f"{i:02d}" for i in range(0, 60, 5)], index=(now.minute // 5))
        
        st.divider()
        
        c3, c4, c5 = st.columns(3)
        with c3: temp = st.number_input("🌡️ 체온", 30.0, 42.0, 36.5, 0.1)
        with c4: med = st.selectbox("💊 약 종류", ["선택 안 함", "맥시부펜", "세토펜", "아침약", "점심약", "저녁약", "기타"])
        with c5: vol = st.text_input("💉 용량", placeholder="5ml")
        
        note = st.text_area("🗒️ 특이사항")
        
        if st.form_submit_button("💾 기록 저장", use_container_width=True):
            f_time = f"{ampm} {hour}:{minute}"
            new_row = {"날짜": f_date, "시간": f_time, "이름": name, "체온": temp, "약 종류": med, "용량": vol, "특이사항": note}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.rerun()

# 4. 현황 대시보드
st.divider()
st.subheader("📊 현재 상태")
cols = st.columns(3)
child_names = ["아율", "아인", "혁"]
child_icons = {"아율": "👧", "아인": "👧", "혁": "👶"}

for i, c_name in enumerate(child_names):
    child_df = st.session_state.df[st.session_state.df['이름'] == c_name]
    with cols[i]:
        if not child_df.empty:
            latest = child_df.iloc[-1]
            t = latest["체온"]
            prev_t = child_df.iloc[-2]['체온'] if len(child_df) > 1 else t
            diff = round(t - prev_t, 1)
            d_limit = 38.0 if c_name == "혁" else 39.0
            
            if t <= 37.5: bg = "status-normal"; icon = "🟢"
            elif t < d_limit: bg = "status-caution"; icon = "🟠"
            else: bg = "status-danger"; icon = "🔴"
            
            diff_text = f"{'↑' if diff > 0 else '↓' if diff < 0 else ''} {abs(diff)}°C"
            st.markdown(f'<div class="status-card {bg}"><div><div class="card-header">{child_icons[c_name]} {c_name} {icon}</div><div class="card-temp">{t}°C</div><div class="card-delta">{diff_text}</div></div><div class="card-footer">🕒 {latest["시간"]}</div></div>', unsafe_allow_html=True)
        else: st.info(f"{c_name} 없음")

# 5. 아이별 그래프
st.subheader("📈 최근 추이")
for c_name in child_names:
    f_df = st.session_state.df[st.session_state.df['이름'] == c_name].tail(6)
    if not f_df.empty:
        with st.container():
            st.write(f"**{child_icons[c_name]} {c_name}**")
            f_df['축'] = f_df['날짜'].str[3:] + "<br>" + f_df['시간'].str.split(' ').str[-1]
            d_limit = 38.0 if c_name == "혁" else 39.0
            colors = ['#28a745' if t <= 37.5 else '#fd7e14' if t < d_limit else '#dc3545' for t in f_df['체온']]
            
            fig = go.Figure()
            fig.add_hrect(y0=34, y1=37.5, fillcolor="#28a745", opacity=0.08, line_width=0)
            fig.add_hrect(y0=37.5, y1=d_limit, fillcolor="#fd7e14", opacity=0.08, line_width=0)
            fig.add_hrect(y0=d_limit, y1=42, fillcolor="#dc3545", opacity=0.08, line_width=0)
            fig.add_trace(go.Scatter(x=f_df['축'], y=f_df['체온'], mode='lines+markers+text', line=dict(color='white', width=2), marker=dict(color=colors, size=10), text=f_df['체온'], textposition="top center", textfont=dict(color="white", size=12)))
            fig.update_layout(height=200, margin=dict(l=5, r=5, t=25, b=5), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(showgrid=False, color='white', tickfont=dict(size=9)), yaxis=dict(range=[34, 42], visible=False))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"m_chart_{c_name}")
