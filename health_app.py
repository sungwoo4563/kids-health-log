import streamlit as st
import pandas as pd
import datetime
import os

# 1. 페이지 설정 및 다크 모드 스타일 디자인
st.set_page_config(page_title="아율·아인·혁 건강기록", page_icon="🌡️", layout="wide")

# 보여주신 이미지와 유사한 카드 디자인 CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; } /* 다크 배경 */
    
    .status-card {
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 10px;
        color: white;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .status-normal { background-color: #1e3a2a; border: 1px solid #2e5a3a; } /* 진한 초록 */
    .status-caution { background-color: #4a3a1a; border: 1px solid #6a5a2a; } /* 진한 주황 */
    .status-danger { background-color: #3e1a1a; border: 1px solid #5e2a2a; }  /* 진한 빨강 */
    
    .card-header { font-size: 1.1rem; font-weight: bold; margin-bottom: 10px; display: flex; align-items: center; gap: 5px; }
    .card-temp { font-size: 3rem; font-weight: 800; margin: 10px 0; }
    .card-delta { 
        font-size: 1rem; 
        background-color: rgba(255,255,255,0.1); 
        padding: 4px 10px; 
        border-radius: 20px; 
        display: inline-block;
        width: fit-content;
    }
    .card-footer { font-size: 0.85rem; opacity: 0.7; margin-top: 15px; display: flex; align-items: center; gap: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌡️ 우리 아이 건강 관리 센터")

# 2. 데이터 로드
DATA_FILE = "health_data.csv"
def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["날짜", "시간", "이름", "체온", "약 종류", "용량", "특이사항"])

def save_data(df): df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

if 'df' not in st.session_state: st.session_state.df = load_data()

# 3. 입력 폼 (접어두기)
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
            current_ampm = "오후" if now.hour >= 12 else "오전"
            ampm = st.selectbox("오전/오후", ["오전", "오후"], index=0 if current_ampm == "오전" else 1)
        with t_col2:
            h12 = now.hour % 12
            h12 = 12 if h12 == 0 else h12
            hour = st.selectbox("시", [i for i in range(1, 13)], index=h12-1)
        with t_col3:
            m_idx = (now.minute // 5)
            minute = st.selectbox("분", [f"{i:02d}" for i in range(0, 60, 5)], index=m_idx)
        
        f_time = f"{ampm} {hour}:{minute}"

        c4, c5, c6 = st.columns(3)
        with c4: temp = st.number_input("체온 (℃)", 34.0, 42.0, 36.5, 0.1)
        with c5: med = st.selectbox("약 종류", ["선택 안 함", "맥시부펜", "세토펜", "아침약", "점심약", "저녁약", "기타"])
        with c6: vol = st.text_input("용량", placeholder="예: 5ml")
        
        note = st.text_area("특이사항")
        
        if st.form_submit_button("💾 기록 저장"):
            new_row = {"날짜": f_date, "시간": f_time, "이름": name, "체온": temp, "약 종류": med, "용량": vol, "특이사항": note}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.rerun()

# 4. 현황 대시보드 (보여주신 이미지 스타일 카드)
st.subheader("📊 현재 상태 요약")
cols = st.columns(3)
child_icons = {"아율": "👧", "아인": "👧", "혁": "👶"}

for i, c_name in enumerate(["아율", "아인", "혁"]):
    child_df = st.session_state.df[st.session_state.df['이름'] == c_name]
    with cols[i]:
        if not child_df.empty:
            latest = child_df.iloc[-1]
            prev_temp = child_df.iloc[-2]['체온'] if len(child_df) > 1 else latest['체온']
            diff = round(latest['체온'] - prev_temp, 1)
            
            # 상태에 따른 배경 클래스 및 아이콘
            if latest['체온'] <= 37.5: 
                status_txt, status_icon, bg_class = "정상", "🟢", "status-normal"
            elif latest['체온'] <= 38.9: 
                status_txt, status_icon, bg_class = "미열", "🟠", "status-caution"
            else: 
                status_txt, status_icon, bg_class = "고열", "🔴", "status-danger"
            
            delta_prefix = "↑" if diff > 0 else "↓" if diff < 0 else ""
            
            # HTML 커스텀 카드 렌더링
            st.markdown(f"""
                <div class="status-card {bg_class}">
                    <div>
                        <div class="card-header">{child_icons[c_name]} {c_name} {status_icon} {status_txt}</div>
                        <div class="card-temp">{latest['체온']}°C</div>
                        <div class="card-delta">{delta_prefix} {abs(diff)}°C</div>
                    </div>
                    <div class="card-footer">🕒 {latest['날짜']} {latest['시간']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"{c_name}: 기록 없음")

# 5. 아이별 탭 & 그래프
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
            st.subheader("📈 체온 추이")
            chart_data = f_df.copy()
            chart_data['기록시간'] = chart_data['날짜'] + " " + chart_data['시간']
            st.line_chart(data=chart_data, x='기록시간', y='체온', color="#ff4b4b" if name_filter else "이름")
            
            st.subheader("📄 상세 기록")
            csv = f_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(f"📥 {name_filter or '전체'} 엑셀 받기", csv, f"{name_filter or 'all'}.csv", "text/csv", key=f"dl_{i}")
            
            d_df = f_df.copy()
            d_df.insert(0, '선택', False)
            styled = d_df.iloc[::-1].style.map(style_temp, subset=['체온'])
            
            edited = st.data_editor(styled, hide_index=True, use_container_width=True, key=f"ed_{i}",
                                   column_config={"선택": st.column_config.CheckboxColumn("삭제", default=False)})
            
            if st.button("🗑️ 선택 삭제", key=f"del_{i}"):
                to_delete = edited[edited['선택'] == True]
                if not to_delete.empty:
                    for _, r in to_delete.iterrows():
                        st.session_state.df = st.session_state.df[~((st.session_state.df['날짜'] == r['날짜']) & (st.session_state.df['시간'] == r['시간']) & (st.session_state.df['체온'] == r['체온']))]
                    save_data(st.session_state.df)
                    st.rerun()
