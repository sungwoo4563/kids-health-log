import streamlit as st
import pandas as pd
import datetime
import os
import plotly.graph_objects as go

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="우리 아이 건강기록", page_icon="🌡️", layout="wide")

# 아이들 아이콘 정의
CHILD_ICONS = {"아율": "👧", "아인": "👧", "혁": "👶"}

st.markdown("""
    <style>
    /* 1. 기본 다크 모드 설정 */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0d1117 !important;
        color: #ffffff !important;
    }

    /* 2. [복구] 그래프 디자인 - 흰색 테두리 & 그림자 부활 */
    [data-testid="stPlotlyChart"] {
        border: 2px solid #ffffff !important; /* 흰색 테두리 복구 */
        background-color: #0d1117 !important; /* 배경색 본래대로 */
        border-radius: 15px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important; /* 그림자 복구 */
    }

    /* 3. [복구] 선택창 및 입력창 디자인 - 흰색 테두리 부활 */
    div[data-baseweb="select"] span, 
    div[data-baseweb="select"] div {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    div[data-baseweb="select"] input { opacity: 0 !important; width: 0px !important; }
    
    div[data-baseweb="select"], 
    div[data-baseweb="input"], 
    div[data-baseweb="textarea"] {
        background-color: #0d1117 !important; /* 배경색 본래대로 */
        border: 2px solid #ffffff !important; /* 흰색 테두리 복구 */
        border-radius: 8px !important;
    }
    
    input[type="text"], textarea {
        color: transparent !important;
        text-shadow: 0 0 0 #ffffff !important;
    }
    
    div[data-baseweb="base-input"], 
    div[data-baseweb="select"] > div {
        border: none !important;
        background-color: transparent !important;
    }

    /* 4. [복구] 기록 저장 버튼 - 흰색 테두리 검정 버튼으로 복귀 */
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #0d1117 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important; /* 흰색 테두리 복구 */
        font-weight: bold !important;
        border-radius: 8px !important;
    }

    /* 5. [복구] 체온 입력기 */
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {
        background-color: #0d1117 !important;
        border: 2px solid #ffffff !important; /* 흰색 테두리 복구 */
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
        border-left: 2px solid #ffffff !important; /* 흰색 선 복구 */
        color: #ffffff !important;
    }

    /* 6. [복구] 표(DataFrame) 스타일 - 흰색 테두리 복구 */
    div[data-testid="stDataFrame"] div[role="columnheader"] {
        background-color: #161b22 !important;
        color: #ffffff !important; /* 글자색 흰색 복구 */
        font-weight: bold !important;
        border-bottom: 2px solid #ffffff !important; /* 흰색 헤더 선 복구 */
    }
    div[data-testid="stDataFrame"] div[role="gridcell"] {
        border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important; /* 셀 구분선 흰색(반투명) 복구 */
        color: #ffffff !important;
        background-color: #0d1117 !important;
    }
    [data-testid="stDataFrame"] {
        background-color: #0d1117 !important;
    }
    
    /* 툴바 숨김 유지 */
    [data-testid="stElementToolbar"] { display: none !important; }

    label, p, span, h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    /* [복구] 구분선 흰색 복구 */
    hr { border-color: #ffffff !important; opacity: 0.3 !important; }

    button[data-baseweb="tab"] div p {
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 1rem !important;
    }
    
    div[data-testid="stCheckbox"] label span { color: #fbbf24 !important; }

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
        with c1: 
            name = st.selectbox(
                "아이 이름", 
                ["아율", "아인", "혁"], 
                format_func=lambda x: f"{CHILD_ICONS[x]} {x}"
            )
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
                        st.warning(f"⚠️ 주의: {CHILD_ICONS[name]} {name}가 마지막으로 복용한 약도 **{last_med}**입니다!")

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

for i, c_name in enumerate(child_names):
    child_df = st.session_state.df[st.session_state.df['이름'] == c_name]
    with cols[i]:
        if not child_df.empty:
            latest = child_df.iloc[-1]; t = latest["체온"]
            d_limit = 38.0 if c_name == "혁" else 39.0
            bg = "#1e3a2a" if t <= 37.5 else "#4a3a1a" if t < d_limit else "#3e1a1a"
            st.markdown(f'<div style="background-color:{bg}; padding:15px; border:2px solid #ffffff; border-radius:15px; color:white;"><div style="font-weight:bold;">{CHILD_ICONS[c_name]} {c_name}</div><div style="font-size:2rem; font-weight:800;">{t}°C</div><div style="font-size:0.8rem; opacity:0.8;">🕒 {latest["시간"]}</div></div>', unsafe_allow_html=True)
        else: st.info(f"{CHILD_ICONS[c_name]} {c_name}: 기록 없음")

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
            
            fig.update_layout(
                title=dict(text=f"<b>{CHILD_ICONS[c_name]} {c_name}</b>", font=dict(size=18, color="white"), x=0.5, xanchor='center'),
                height=250, 
                margin=dict(l=10, r=10, t=50, b=60), 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                showlegend=False, 
                dragmode=False,
                xaxis=dict(
                    showgrid=False, 
                    color='white', 
                    tickfont=dict(size=12, weight='bold'),
                    fixedrange=True,
                    range=[-0.5, 6.5]
                ), 
                yaxis=dict(range=[34, 42], visible=False, fixedrange=True, showticklabels=False)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False}, key=f"chart_{c_name}")

# 6. 상세 기록 리스트
st.divider()
st.subheader("📋 상세 기록")

edit_mode = st.toggle("🗑️ 기록 삭제/수정 모드 (클릭하여 활성화)", value=False)

def color_rows(row):
    # 모바일 배경 강제 다크모드 유지
    bg_color = "background-color: #0d1117;"
    
    text_color = "color: white;"
    font_weight = "font-weight: normal;"

    name = str(row['이름'])
    if "아율" in name: 
        text_color = "color: #ff99cc;"
        font_weight = "font-weight: bold;"
    elif "아인" in name: 
        text_color = "color: #a3e635;"
        font_weight = "font-weight: bold;"
    elif "혁" in name:   
        text_color = "color: #60a5fa;"
        font_weight = "font-weight: bold;"
    
    final_style = f"{bg_color} {text_color} {font_weight}"
    return [final_style] * len(row)

if not st.session_state.df.empty:
    if edit_mode:
        st.info("💡 행을 선택하고 Delete 키를 누르거나, 휴지통 아이콘을 눌러 삭제하세요.")
        editor_df = st.session_state.df.copy()
        editor_df = editor_df.fillna("")
        
        cols_order = ["이름", "날짜", "시간", "체온", "약 종류", "용량", "특이사항"]
        final_cols = [c for c in cols_order if c in editor_df.columns]
        editor_df = editor_df[final_cols]
        
        edited_df = st.data_editor(
            editor_df,
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            key="data_editor"
        )
        if not edited_df.equals(st.session_state.df[final_cols]):
            st.session_state.df = edited_df
            save_data(st.session_state.df)
            st.rerun()
    else:
        # 보기 모드
        tabs = st.tabs(["전체", f"👧 아율", f"👧 아인", f"👶 혁"])
        for i, tab in enumerate(tabs):
            n_filter = [None, "아율", "아인", "혁"][i]
            with tab:
                display_df = st.session_state.df if n_filter is None else st.session_state.df[st.session_state.df['이름'] == n_filter]
                if not display_df.empty:
                    show_df = display_df.copy().iloc[::-1]
                    show_df = show_df.fillna("") 
                    
                    if '약 종류' in show_df.columns:
                        show_df['약 종류'] = show_df['약 종류'].replace("선택 안 함", "")

                    show_df['체온'] = show_df['체온'].apply(lambda x: f"{float(x):.1f}" if x else "")
                    
                    def format_vol(x):
                        try:
                            val = float(str(x).replace('ml', '').strip())
                            return f"{val:.1f}"
                        except: return x
                    
                    if '용량' in show_df.columns:
                        show_df['용량'] = show_df['용량'].apply(format_vol)

                    cols_order = ["이름", "날짜", "시간", "체온", "약 종류", "용량", "특이사항"]
                    final_cols = [c for c in cols_order if c in show_df.columns]
                    show_df = show_df[final_cols]
                    
                    styled_df = show_df.style.apply(color_rows, axis=1)
                    
                    dynamic_height = (len(show_df) + 1) * 35 + 3

                    st.dataframe(
                        styled_df, 
                        use_container_width=True, 
                        hide_index=True,
                        height=dynamic_height
                    )
