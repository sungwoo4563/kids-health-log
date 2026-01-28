import streamlit as st
import pandas as pd
import datetime
import os
import plotly.graph_objects as go

# 1. 페이지 설정 및 강화된 스타일
st.set_page_config(page_title="아율·아인·혁 건강기록", page_icon="🌡️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    /* 입력 섹션 강조 스타일 */
    .stExpander {
        border: 2px solid #4e5d6c !important;
        border-radius: 15px !important;
        background-color: #161b22 !important;
    }
    .status-card {
        padding: 20px; border-radius: 15px; margin-bottom: 10px; color: white;
        min-height: 180px; display: flex; flex-direction: column; justify-content: space-between;
    }
    .status-normal { background-color: #1e3a2a; border: 1px solid #2e5a3a; }
    .status-caution { background-color: #4a3a1a; border: 1px solid #6a5a2a; }
    .status-danger { background-color: #3e1a1a; border: 1px solid #5e2a2a; }
    
    .card-header { font-size: 1.1rem; font-weight: bold; display: flex; align-items: center; gap: 5px; }
    .card-temp { font-size: 3rem; font-weight: 800; margin: 10px 0; }
    .card-delta { font-size: 1rem; background-color: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 20px; display: inline-block; }
    .card-footer { font-size: 0.85rem; opacity: 0.7; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌡️ 우리 아이 건강 관리 센터")

# 2. 데이터 관리
DATA_FILE = "health_data.csv"
def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["날짜", "시간", "이름", "체온", "약 종류", "용량", "특이사항"])

def save_data(df): df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

if 'df' not in st.session_state: st.session_state.df = load_data()

# 3. 새로운 기록 추가하기 (디자인 강화)
now = datetime.datetime.now()
st.subheader("📝 퀵 기록 센터") # 제목을 밖으로 빼서 강조
with st.expander("✨ 여기에 새로운 건강 기록을 입력하세요 (클릭)", expanded=True): # 기본으로 열어둠
    with st.form("health_form", clear_on_submit=True):
        f_c1, f_c2, f_c3 = st.columns([1, 1, 1])
        with f_c1: 
            name = st.selectbox("아이 이름", ["아율", "아인", "혁"])
        with f_c2: 
            d = st.date_input("측정 날짜", now.date())
            f_date = d.strftime("%y.%m.%d")
        with f_c3:
            st.write("🕒 측정 시간")
            t_col1, t_col2 = st.columns(2)
            with t_col1: ampm = st.selectbox("오전/오후", ["오전", "오후"], index=(0 if now.hour < 12 else 1), label_visibility="collapsed")
            with t_col2: 
                h12 = 12 if now.hour % 12 == 0 else now.hour % 12
                hour = st.selectbox("시", [i for i in range(1, 13)], index=h12-1, label_visibility="collapsed")
        
        st.divider()
        
        f_c4, f_c5, f_c6 = st.columns(3)
        with f_c4: temp = st.number_input("🌡️ 현재 체온 (℃)", 30.0, 42.0, 36.5, 0.1)
        with f_c5: med = st.selectbox("💊 복용한 약", ["선택 안 함", "맥시부펜", "세토펜", "아침약", "점심약", "저녁약", "기타"])
        with f_c6: vol = st.text_input("💉 복용 용량", placeholder="예: 5ml")
        
        note = st.text_area("🗒️ 특이사항 (증상 등)")
        
        # 저장 버튼 강조
        submit_btn = st.form_submit_button("💾 기록 저장하기", use_container_width=True)
        
        if submit_btn:
            # 분 정보는 현재 분(5분 단위) 자동 계산
            minute = f"{ (now.minute // 5) * 5:02d}"
            f_time = f"{ampm} {hour}:{minute}"
            new_row = {"날짜": f_date, "시간": f_time, "이름": name, "체온": temp, "약 종류": med, "용량": vol, "특이사항": note}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.success(f"{name}의 기록이 저장되었습니다!")
            st.rerun()

# 4. 현황 대시보드 (기존 유지)
st.divider()
st.subheader("📊 현재 상태 요약")
cols = st.columns(3)
child_names = ["아율", "아인", "혁"]
child_icons = {"아율": "👧", "아인": "👧", "혁": "👶"}

for i, c_name in enumerate(child_names):
    child_df = st.session_state.df[st.session_state.df['이름'] == c_name]
    with cols[i]:
        if not child_df.empty:
            latest = child_df.iloc[-1]
            t = latest["체온"]
            prev_temp = child_df.iloc[-2]['체온'] if len(child_df) > 1 else t
            diff = round(t - prev_temp, 1)
            d_limit = 38.0 if c_name == "혁" else 39.0
            if t <= 37.5: bg = "status-normal"; icon = "🟢"; txt = "정상"
            elif t < d_limit: bg = "status-caution"; icon = "🟠"; txt = "미열"
            else: bg = "status-danger"; icon = "🔴"; txt = "고열"
            delta_prefix = "↑" if diff > 0 else "↓" if diff < 0 else ""
            st.markdown(f'<div class="status-card {bg}"><div><div class="card-header">{child_icons[c_name]} {c_name} | {icon} {txt}</div><div class="card-temp">{t}°C</div><div class="card-delta">{delta_prefix} {abs(diff)}°C</div></div><div class="card-footer">🕒 {latest["날짜"]} {latest["시간"]}</div></div>', unsafe_allow_html=True)
        else: st.info(f"{c_name}: 기록 없음")

# 5. 아이별 그래프 (기존 유지)
st.subheader("📈 최근 체온 흐름")
g_cols = st.columns(3)
for i, c_name in enumerate(child_names):
    with g_cols[i]:
        f_df = st.session_state.df[st.session_state.df['이름'] == c_name].tail(7)
        if not f_df.empty:
            f_df['시간축'] = f_df['날짜'].str[3:] + "<br>" + f_df['시간'].str.split(' ').str[-1]
            d_limit = 38.0 if c_name == "혁" else 39.0
            colors = ['#28a745' if t <= 37.5 else '#fd7e14' if t < d_limit else '#dc3545' for t in f_df['체온']]
            fig = go.Figure()
            fig.add_hrect(y0=30, y1=37.5, fillcolor="#28a745", opacity=0.1, line_width=0)
            fig.add_hrect(y0=37.5, y1=d_limit, fillcolor="#fd7e14", opacity=0.1, line_width=0)
            fig.add_hrect(y0=d_limit, y1=42, fillcolor="#dc3545", opacity=0.1, line_width=0)
            fig.add_trace(go.Scatter(x=f_df['시간축'], y=f_df['체온'], mode='lines+markers+text', line=dict(color='white', width=2), marker=dict(color=colors, size=12, line=dict(color='white', width=1)), text=f_df['체온'], textposition="top center", textfont=dict(color="white", size=14, family="Arial Black")))
            fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(showgrid=False, zeroline=False, color='white', tickfont=dict(size=10)), yaxis=dict(range=[34, 42], showgrid=False, zeroline=False, visible=False))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"chart_{c_name}")
        else: st.info(f"{c_name} 데이터 없음")

# 6. 상세 기록 탭
st.divider()
tabs = st.tabs(["📋 전체 기록", "💖 아율", "💛 아인", "💙 혁"])
for i, tab in enumerate(tabs):
    n_filter = [None, "아율", "아인", "혁"][i]
    with tab:
        f_df = st.session_state.df if n_filter is None else st.session_state.df[st.session_state.df['이름'] == n_filter]
        if not f_df.empty:
            d_df = f_df.copy().iloc[::-1]
            d_df.insert(0, '선택', False)
            def style_temp(val):
                limit = 38.0 if n_filter == "혁" else 39.0
                color = '#28a745' if val <= 37.5 else '#fd7e14' if val < limit else '#dc3545'
                return f'color: {color}; font-weight: bold;'
            edited = st.data_editor(d_df.style.map(style_temp, subset=['체온']), hide_index=True, use_container_width=True, key=f"ed_{i}", column_config={"선택": st.column_config.CheckboxColumn("삭제")})
            if st.button(f"🗑️ 항목 삭제", key=f"del_{i}"):
                to_del = edited[edited['선택'] == True]
                for _, r in to_del.iterrows():
                    target_name = r['이름'] if n_filter is None else n_filter
                    st.session_state.df = st.session_state.df[~((st.session_state.df['날짜'] == r['날짜']) & (st.session_state.df['시간'] == r['시간']) & (st.session_state.df['이름'] == target_name))]
                save_data(st.session_state.df)
                st.rerun()
