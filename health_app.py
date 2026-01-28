import streamlit as st
import pandas as pd
import datetime
import os

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="아율·아인·혁 건강기록", page_icon="🌡️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
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

# 2. 데이터 로드 및 저장
DATA_FILE = "health_data.csv"
def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["날짜", "시간", "이름", "체온", "약 종류", "용량", "특이사항"])

def save_data(df): df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

if 'df' not in st.session_state: st.session_state.df = load_data()

# 3. 입력 폼 (생략 - 기존 유지)
now = datetime.datetime.now()
with st.expander("📝 새로운 기록 추가하기", expanded=False):
    with st.form("health_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: name = st.selectbox("아이 이름", ["아율", "아인", "혁"])
        with c2: 
            d = st.date_input("날짜", now.date())
            f_date = d.strftime("%y.%m.%d")
        
        st.write("🕒 복용 시간")
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            ampm_idx = 0 if now.hour < 12 else 1
            ampm = st.selectbox("오전/오후", ["오전", "오후"], index=ampm_idx)
        with t_col2:
            h12 = now.hour % 12
            h12 = 12 if h12 == 0 else h12
            hour = st.selectbox("시", [i for i in range(1, 13)], index=h12-1)
        with t_col3:
            m_idx = (now.minute // 5)
            minute = st.selectbox("분", [f"{i:02d}" for i in range(0, 60, 5)], index=m_idx)
        
        f_time = f"{ampm} {hour}:{minute}"

        c4, c5, c6 = st.columns(3)
        with c4: temp = st.number_input("체온 (℃)", 30.0, 42.0, 36.5, 0.1)
        with c5: med = st.selectbox("약 종류", ["선택 안 함", "맥시부펜", "세토펜", "아침약", "점심약", "저녁약", "기타"])
        with c6: vol = st.text_input("용량", placeholder="예: 5ml")
        
        note = st.text_area("특이사항")
        if st.form_submit_button("💾 기록 저장"):
            new_row = {"날짜": f_date, "시간": f_time, "이름": name, "체온": temp, "약 종류": med, "용량": vol, "특이사항": note}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.rerun()

# 4. 현황 대시보드
st.subheader("📊 현재 상태 요약")
cols = st.columns(3)
child_names = ["아율", "아인", "혁"]
child_icons = {"아율": "👧", "아인": "👧", "혁": "👶"}

for i, c_name in enumerate(child_names):
    child_df = st.session_state.df[st.session_state.df['이름'] == c_name]
    with cols[i]:
        if not child_df.empty:
            latest = child_df.iloc[-1]
            prev_temp = child_df.iloc[-2]['체온'] if len(child_df) > 1 else latest['체온']
            diff = round(latest['체온'] - prev_temp, 1)
            if latest['체온'] <= 37.5: st_txt, st_icon, bg = "정상", "🟢", "status-normal"
            elif latest['체온'] <= 38.9: st_txt, st_icon, bg = "미열", "🟠", "status-caution"
            else: st_txt, st_icon, bg = "고열", "🔴", "status-danger"
            delta_prefix = "↑" if diff > 0 else "↓" if diff < 0 else ""
            st.markdown(f'<div class="status-card {bg}"><div><div class="card-header">{child_icons[c_name]} {c_name} {st_icon} {st_txt}</div><div class="card-temp">{latest["체온"]}°C</div><div class="card-delta">{delta_prefix} {abs(diff)}°C</div></div><div class="card-footer">🕒 {latest["날짜"]} {latest["시간"]}</div></div>', unsafe_allow_html=True)
        else: st.info(f"{c_name}: 기록 없음")

# 5. 아이별 그래프 (날짜/시간 2줄 표시)
st.subheader("📈 최근 체온 흐름")
g_cols = st.columns(3)

def prepare_chart_data(df):
    if df.empty: return df
    chart_df = df.tail(7).copy()
    # 날짜와 시간을 리스트 형태로 넣어 Vega-Lite에서 자동으로 줄바꿈 처리되게 함
    chart_df['심플날짜'] = chart_df['날짜'].str.split('.').str[1:].str.join('.') + "일"
    chart_df['심플시간'] = chart_df['시간'].str.split(' ').str[-1]
    
    # 2줄로 표시하기 위해 [날짜, 시간] 리스트 생성
    chart_df['시간축'] = chart_df[['심플날짜', '심플시간']].values.tolist()
    return chart_df

for i, c_name in enumerate(child_names):
    with g_cols[i]:
        f_df = st.session_state.df[st.session_state.df['이름'] == c_name]
        if not f_df.empty:
            st.markdown(f"**{child_icons[c_name]} {c_name}**")
            chart_data = prepare_chart_data(f_df)
            
            st.vega_lite_chart(chart_data, {
                'height': 220,
                'layer': [
                    {
                        'mark': {'type': 'line', 'point': {'size': 80, 'color': '#ff4b4b'}, 'color': '#ff4b4b', 'strokeWidth': 3},
                        'encoding': {
                            'x': {'field': '시간축', 'type': 'nominal', 'axis': {'title': None, 'labelAngle': 0}},
                            'y': {'field': '체온', 'type': 'quantitative', 'scale': {'domain': [30, 42]}, 'axis': None}
                        }
                    },
                    {
                        'mark': {'type': 'text', 'dy': -15, 'fontSize': 13, 'fontWeight': 'bold', 'color': 'white'},
                        'encoding': {
                            'x': {'field': '시간축', 'type': 'nominal'},
                            'y': {'field': '체온', 'type': 'quantitative'},
                            'text': {'field': '체온', 'type': 'quantitative', 'format': '.1f'}
                        }
                    }
                ],
                'config': {'view': {'stroke': 'transparent'}}
            }, use_container_width=True)
        else:
            st.info(f"{c_name} 데이터 없음")

# 6. 상세 기록 탭
st.divider()
tabs = st.tabs(["📋 전체 기록", "💖 아율", "💛 아인", "💙 혁"])
# ... [상세 기록 및 삭제 로직 포함된 표 코드는 동일]
