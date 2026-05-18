import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from matplotlib import font_manager, rc
import random
import platform
import time
import sqlite3
import json
import hashlib
from datetime import datetime

st.set_page_config(page_title="Future Universe", page_icon="🚀", layout="wide")

# ── 세션 초기화 ────────────────────────────────────────
if "page"                   not in st.session_state: st.session_state.page                   = "home"
if "survey_page"            not in st.session_state: st.session_state.survey_page            = 1
if "survey_user_id"         not in st.session_state: st.session_state.survey_user_id         = None
if "survey_respondent_type" not in st.session_state: st.session_state.survey_respondent_type = "학생"
if "user"                   not in st.session_state: st.session_state.user                   = None

# ── 전체 스타일 CSS ────────────────────────────────────
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

/* ── 기본 폰트 ── */
html, body, [class*="css"], * {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Noto Sans KR', sans-serif !important;
    font-size: 16px;
}

/* ── 전체 배경 ── */
.stApp {
    background: #0D1525 !important;
}
.main .block-container {
    padding: 2.5rem 3rem;
    max-width: 1150px;
    background: transparent;
}

/* ── 상단 헤더바 ── */
[data-testid="stHeader"] {
    background: #0A1220 !important;
    border-bottom: 1px solid rgba(74,144,255,0.15) !important;
}
[data-testid="stHeader"] * {
    color: rgba(200,220,255,0.6) !important;
}
[data-testid="stDecoration"] {
    display: none !important;
}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1220 0%, #0E1830 55%, #111A38 100%) !important;
    border-right: 1px solid rgba(74,144,255,0.15) !important;
}
[data-testid="stSidebarNav"] { display: none; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: rgba(200,220,255,0.82) !important;
    font-size: 1.3rem !important;
}

/* ── 사이드바 섹션 헤더 ── */
.nav-section {
    color: rgba(74,144,255,0.75);
    font-size: 0.94rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    padding: 1.3rem 0 0.4rem 0;
    display: block;
}

/* ── EVENT 뱃지 ── */
.event-badge-chip {
    background: #FF2D2D;
    color: #fff;
    font-size: 0.62rem;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 20px;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    display: inline-block;
    pointer-events: none;
    box-shadow: 0 0 8px rgba(255,45,45,0.6);
    animation: chipPulse 1.4s ease-in-out infinite;
}
@keyframes chipPulse {
    0%, 100% { box-shadow: 0 0 6px rgba(255,45,45,0.5); }
    50%       { box-shadow: 0 0 14px rgba(255,45,45,0.9), 0 0 4px rgba(255,45,45,0.4); }
}
.nav-divider {
    border: none;
    border-top: 1px solid rgba(74,144,255,0.08);
    margin: 0.5rem 0;
}

/* ── nav 버튼 비활성 ── */
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    background: transparent !important;
    border: none !important;
    color: rgba(200,220,255,0.82) !important;
    text-align: left !important;
    padding: 0.48rem 0.9rem !important;
    border-radius: 4px !important;
    font-size: 1.3rem !important;
    font-weight: 400 !important;
    justify-content: flex-start !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
    background: rgba(74,144,255,0.1) !important;
    color: #fff !important;
}

/* ── nav 버튼 활성 ── */
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background: rgba(74,144,255,0.1) !important;
    border: none !important;
    border-left: 2px solid #4A90FF !important;
    color: #E4EDFF !important;
    font-weight: 700 !important;
    text-align: left !important;
    padding: 0.48rem 0.9rem !important;
    border-radius: 0 4px 4px 0 !important;
    font-size: 1.3rem !important;
    justify-content: flex-start !important;
    letter-spacing: 0.01em !important;
}

/* ── 제목 ── */
h1 {
    font-size: 2.1rem !important;
    font-weight: 700 !important;
    color: #E4EDFF !important;
    letter-spacing: -0.5px !important;
    line-height: 1.2 !important;
}
h2 {
    font-size: 1.45rem !important;
    font-weight: 600 !important;
    color: #D0DFFF !important;
}
h3 {
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    color: #BDD0FF !important;
}

/* ── 본문 텍스트 전역 ── */
p, li, span, label, div {
    color: #C0D2F5;
}

/* ── 섹션 타이틀 ── */
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #D0DFFF;
    border-left: 3px solid #4A90FF;
    padding-left: 0.75rem;
    margin: 2.5rem 0 1.2rem 0;
    letter-spacing: -0.1px;
}

/* ── 히어로 배너 ── */
.hero {
    background: linear-gradient(135deg, #101D3C 0%, #172B55 50%, #111E3E 100%);
    border: 1px solid rgba(74,144,255,0.28);
    padding: 3.25rem 3rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60%;
    right: -5%;
    width: 340px;
    height: 340px;
    background: radial-gradient(circle, rgba(74,144,255,0.18) 0%, transparent 65%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -40%;
    left: 15%;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(120,80,255,0.13) 0%, transparent 65%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 700;
    color: #E4EDFF;
    letter-spacing: -0.5px;
    margin-bottom: 0.6rem;
    line-height: 1.15;
    position: relative;
}
.hero-accent { color: #4A90FF; }
.hero-sub {
    font-size: 1.1rem;
    color: rgba(190,215,255,0.82);
    margin: 0;
    line-height: 1.75;
    position: relative;
}

/* ── 전문가 ── */
.expert-name { font-size: 1.15rem; font-weight: 700; color: #D0DFFF; margin: 0.5rem 0 0.25rem 0; }
.expert-tags { font-size: 0.88rem; color: rgba(190,215,255,0.7); line-height: 1.85; }

/* ── CTA 배너 ── */
.cta-banner {
    background: linear-gradient(135deg, #152248 0%, #122040 100%);
    border: 1px solid rgba(74,144,255,0.32);
    padding: 2.25rem 2.5rem;
    border-radius: 8px;
    text-align: center;
    margin: 1.5rem 0 1rem 0;
    position: relative;
    overflow: hidden;
}
.cta-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    left: 50%;
    transform: translateX(-50%);
    width: 300px;
    height: 200px;
    background: radial-gradient(ellipse, rgba(74,144,255,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.cta-title { font-size: 1.35rem; font-weight: 700; color: #E4EDFF; margin-bottom: 0.4rem; position: relative; }
.cta-desc  { font-size: 0.95rem; color: rgba(190,215,255,0.8); margin: 0; position: relative; }

/* ── Q&A ── */
.qa-q {
    background: rgba(74,144,255,0.07);
    border: 1px solid rgba(74,144,255,0.18);
    border-radius: 4px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.45rem;
    font-weight: 600;
    color: #8BB8FF;
    font-size: 0.95rem;
}
.qa-a {
    background: rgba(0,210,150,0.05);
    border: 1px solid rgba(0,210,150,0.12);
    border-radius: 4px;
    padding: 0.7rem 1rem;
    color: rgba(180,240,210,0.75);
    font-size: 0.95rem;
}

/* ── 일반 버튼 ── */
[data-testid="stBaseButton-primary"]:not([data-testid="stSidebar"] *) {
    background: linear-gradient(135deg, #1A4FCC, #2563EB) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
    border-radius: 4px !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *) {
    background: rgba(74,144,255,0.1) !important;
    border: 1px solid rgba(74,144,255,0.28) !important;
    color: #C0D2F5 !important;
    border-radius: 4px !important;
    font-size: 0.95rem !important;
}

/* ── 입력 위젯 ── */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: #162038 !important;
    border: 1px solid rgba(74,144,255,0.28) !important;
    border-radius: 4px !important;
    color: #D0DFFF !important;
    font-size: 0.95rem !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: #4A90FF !important;
    box-shadow: 0 0 0 2px rgba(74,144,255,0.12) !important;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #162038 !important;
    border: 1px solid rgba(74,144,255,0.28) !important;
    color: #D0DFFF !important;
    border-radius: 4px !important;
}

/* ── 컨테이너 카드 ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #162038 !important;
    border: 1px solid rgba(74,144,255,0.18) !important;
    border-radius: 6px !important;
}

/* ── 메트릭 ── */
[data-testid="stMetric"] label { color: rgba(190,215,255,0.7) !important; font-size: 0.9rem !important; }
[data-testid="stMetricValue"] { color: #E4EDFF !important; font-size: 1.9rem !important; font-weight: 700 !important; }

/* ── 구분선 ── */
hr { border-color: rgba(74,144,255,0.18) !important; }

/* ── expander ── */
.streamlit-expanderHeader {
    color: #BDD0FF !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
}

/* ── alert 박스 ── */
[data-testid="stAlert"] {
    background: rgba(74,144,255,0.1) !important;
    border: 1px solid rgba(74,144,255,0.28) !important;
    color: #C0D2F5 !important;
    border-radius: 4px !important;
    font-size: 0.95rem !important;
}

/* ── caption ── */
[data-testid="stCaptionContainer"] { color: rgba(190,215,255,0.6) !important; font-size: 0.875rem !important; }

/* ── progress ── */
.stProgress > div > div { background: linear-gradient(90deg, #2563EB, #4A90FF) !important; }

/* ── radio / checkbox ── */
.stRadio label, .stCheckbox label { color: #C0D2F5 !important; font-size: 0.95rem !important; }

/* ── dataframe ── */
.stDataFrame { border: 1px solid rgba(74,144,255,0.1) !important; border-radius: 6px !important; }
.stDataFrame tbody tr:hover td { background: rgba(74,144,255,0.06) !important; }

/* ── 입력창 너비 제한 ── */
[data-testid="stTextInput"],
[data-testid="stNumberInput"],
[data-testid="stSelectbox"],
[data-testid="stMultiSelect"] {
    max-width: 520px;
}
[data-testid="stTextArea"] {
    max-width: 680px;
}

/* ── 사이드바 푸터 ── */
.sidebar-footer {
    background: transparent;
    padding: 0.5rem 0.75rem;
    font-size: 0.75rem;
    color: rgba(180,200,255,0.18);
    letter-spacing: 0.3px;
}

/* ══════════════════════════════════════
   반응형 — 태블릿 (≤ 768px)
══════════════════════════════════════ */
@media (max-width: 768px) {
    /* 본문 여백 축소 */
    .main .block-container {
        padding: 1.25rem 1.25rem !important;
    }

    /* 히어로 배너 */
    .hero { padding: 2rem 1.5rem !important; }
    .hero-title { font-size: 2rem !important; }
    .hero-sub   { font-size: 1rem !important; }

    /* 제목 */
    h1 { font-size: 1.65rem !important; }
    h2 { font-size: 1.25rem !important; }
    h3 { font-size: 1.05rem !important; }

    /* 컬럼 세로 스태킹 */
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 0.75rem !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    /* 입력창 전체 너비 */
    [data-testid="stTextInput"],
    [data-testid="stNumberInput"],
    [data-testid="stSelectbox"],
    [data-testid="stMultiSelect"],
    [data-testid="stTextArea"] {
        max-width: 100% !important;
    }

    /* 메트릭 숫자 축소 */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }

    /* CTA 배너 */
    .cta-banner { padding: 1.75rem 1.25rem !important; }
    .cta-title  { font-size: 1.15rem !important; }
}

/* ══════════════════════════════════════
   반응형 — 모바일 (≤ 480px)
══════════════════════════════════════ */
@media (max-width: 480px) {
    /* 본문 여백 더 축소 */
    .main .block-container {
        padding: 0.9rem 0.9rem !important;
    }

    /* 히어로 배너 */
    .hero { padding: 1.5rem 1.1rem !important; }
    .hero-title { font-size: 1.6rem !important; line-height: 1.2 !important; }
    .hero-sub   { font-size: 0.92rem !important; }

    /* 제목 */
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.1rem !important; }

    /* 사이드바 nav 버튼 — 터치 영역 확보 */
    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
    [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
        padding: 0.75rem 0.9rem !important;
        font-size: 1.15rem !important;
    }

    /* 일반 버튼 터치 영역 */
    [data-testid="stBaseButton-primary"]:not([data-testid="stSidebar"] *),
    [data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *) {
        min-height: 2.75rem !important;
        font-size: 1rem !important;
    }

    /* 메트릭 */
    [data-testid="stMetricValue"] { font-size: 1.3rem !important; }
    [data-testid="stMetric"] label { font-size: 0.8rem !important; }

    /* 섹션 타이틀 */
    .section-title { font-size: 0.95rem !important; }

    /* 차트가 화면 밖으로 나가지 않도록 */
    .stPlotlyChart, .stDataFrame {
        overflow-x: auto !important;
    }

    /* 가로 스크롤 방지 */
    .stApp { overflow-x: hidden !important; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# DB 연결 및 인증 함수
# ══════════════════════════════════════════
DB_PATH = "../futureverse_survey.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def _hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def init_accounts():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student')""")
    conn.commit()
    c.execute("SELECT COUNT(*) FROM accounts WHERE role='admin'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO accounts (username, password_hash, role) VALUES (?,?,?)",
                  ("admin", _hash_pw("admin1234"), "admin"))
        conn.commit()
    conn.close()

def do_login(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM accounts WHERE username=? AND password_hash=?",
              (username, _hash_pw(password)))
    row = c.fetchone()
    conn.close()
    return {"id": row[0], "username": row[1], "role": row[2]} if row else None

def do_register(username, password):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO accounts (username, password_hash, role) VALUES (?,?,?)",
                  (username, _hash_pw(password), "student"))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

@st.dialog("로그인 / 회원가입")
def login_dialog():
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    with tab1:
        with st.form("dlg_login"):
            u = st.text_input("아이디")
            p = st.text_input("비밀번호", type="password")
            if st.form_submit_button("로그인", use_container_width=True, type="primary"):
                user = do_login(u.strip(), p)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
    with tab2:
        with st.form("dlg_register"):
            nu = st.text_input("아이디 (2자 이상)")
            np_ = st.text_input("비밀번호 (4자 이상)", type="password")
            cp  = st.text_input("비밀번호 확인", type="password")
            if st.form_submit_button("회원가입", use_container_width=True):
                if len(nu.strip()) < 2:
                    st.error("아이디는 2자 이상이어야 합니다.")
                elif len(np_) < 4:
                    st.error("비밀번호는 4자 이상이어야 합니다.")
                elif np_ != cp:
                    st.error("비밀번호가 일치하지 않습니다.")
                elif do_register(nu.strip(), np_):
                    st.success("회원가입 완료! 로그인 탭에서 로그인하세요.")
                else:
                    st.error("이미 사용 중인 아이디입니다.")


# ══════════════════════════════════════════
# 커리어 탐색 공통 필터 UI
# ══════════════════════════════════════════
def show_career_filters(df):
    """전공/활동분야 필터 + 관심전공/희망직업 추천을 페이지 상단에 표시하고 샘플 데이터를 반환합니다"""
    with st.expander("필터 & 맞춤 추천", expanded=True):
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            sel_major   = st.multiselect("전공 필터",      ["전체"] + sorted(df['전공'].unique().tolist()),        default=["전체"])
        with r1c2:
            sel_project = st.multiselect("활동 분야 필터", ["전체"] + sorted(df['활동 분야'].unique().tolist()), default=["전체"])

        stu_interest = st.selectbox("희망 직업 분야", ["선택 안 함"] + sorted(df['현재 직업'].unique().tolist()))

        filtered = df.copy()
        if "전체" not in sel_major:
            filtered = filtered[filtered['전공'].isin(sel_major)]
        if "전체" not in sel_project:
            filtered = filtered[filtered['활동 분야'].isin(sel_project)]

        if stu_interest != "선택 안 함":
            st.divider()
            st.markdown("**맞춤 추천 인사이트**")
            majors = filtered[filtered['현재 직업'] == stu_interest]['전공'].value_counts().head(3)
            if not majors.empty:
                st.write(f"**{stu_interest}** 추천 전공:")
                for m, cnt in majors.items(): st.write(f"- {m} ({cnt}명)")

    df_sample = filtered.sample(min(200, len(filtered))).reset_index(drop=True)
    st.caption(f"표시 중인 전문가: **{len(df_sample)}명** / 전체 {len(df)}명")
    return df_sample


# ══════════════════════════════════════════
# 사이드바 네비게이션 (계층형)
# ══════════════════════════════════════════
SECTIONS = {
    "퓨처유니버스": [
        ("홈",     "home"),
        ("설문조사", "survey"),
    ],
    "커리어 탐색": [
        ("3D 탐색기",       "3d"),
        ("전문가 데이터베이스", "db"),
        ("전문가 분포 현황",   "distribution"),
    ],
    "분석 도구": [
        ("인사이트 시각화", "insights"),
        ("AI 컨설턴트",    "ai"),
        ("로드맵 설계",    "roadmap"),
    ],
}

def nav_btn(label, key, badge=None):
    t = "primary" if st.session_state.page == key else "secondary"
    if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True, type=t):
        st.session_state.page = key
        st.rerun()
    if badge:
        st.sidebar.markdown(
            f'<div style="margin-top:-3.3rem;text-align:left;padding-left:0.75rem;'
            f'pointer-events:none;position:relative;z-index:9;">'
            f'<span class="event-badge-chip">{badge}</span></div>',
            unsafe_allow_html=True
        )

init_accounts()

with st.sidebar:
    # ── 로고 ──────────────────────────────
    st.markdown("""
    <div style='padding:1.75rem 0.5rem 0.9rem 0.5rem;'>
        <div style='font-size:1.05rem; font-weight:700; color:#C8DCFF; letter-spacing:0.5px;'>Future Universe</div>
        <div style='font-size:0.67rem; color:rgba(74,144,255,0.45); margin-top:5px; text-transform:uppercase; letter-spacing:1.8px;'>Career Exploration</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<hr class="nav-divider">', unsafe_allow_html=True)

    # ── 로그인 / 사용자 영역 (최상단) ──────
    if st.session_state.user:
        u          = st.session_state.user
        uname      = u["username"]
        role_label = "관리자" if u["role"] == "admin" else "학생"
        st.markdown(f"""
        <div style='background:rgba(74,144,255,0.08);border-radius:4px;border-left:2px solid #4A90FF;
                    padding:0.65rem 0.9rem;margin:0.3rem 0 0.5rem 0;'>
            <div style='color:#C8DCFF;font-weight:600;font-size:0.925rem;'>{uname}</div>
            <div style='color:rgba(74,144,255,0.55);font-size:0.75rem;margin-top:3px;letter-spacing:0.3px;'>{role_label}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("로그아웃", use_container_width=True, key="sb_logout"):
            st.session_state.user = None
            st.rerun()
    else:
        lc, rc = st.columns(2)
        with lc:
            if st.button("로그인",   use_container_width=True, type="primary", key="sb_login"):
                login_dialog()
        with rc:
            if st.button("회원가입", use_container_width=True, key="sb_register"):
                login_dialog()

    st.markdown('<hr class="nav-divider">', unsafe_allow_html=True)

    # ── 네비게이션 메뉴 ────────────────────
    for section_title, items in SECTIONS.items():
        st.markdown(f'<span class="nav-section">{section_title}</span>', unsafe_allow_html=True)
        for label, key in items:
            nav_btn(label, key, badge="EVENT!" if key == "survey" else None)

    if st.session_state.user and st.session_state.user.get("role") == "admin":
        st.markdown('<hr class="nav-divider">', unsafe_allow_html=True)
        st.markdown('<span class="nav-section">관리자</span>', unsafe_allow_html=True)
        nav_btn("대시보드", "admin_dashboard")

    st.markdown('<hr class="nav-divider" style="margin-top:1rem;">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-footer">© 2025 Future Career Universe</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
# 한글 폰트 설정
# ══════════════════════════════════════════
def set_korean_font():
    system_name = platform.system()
    if system_name == "Windows":
        path = "C:/Windows/Fonts/malgun.ttf"
    elif system_name == "Darwin":
        path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
    else:
        path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    try:
        font_name = font_manager.FontProperties(fname=path).get_name()
        rc('font', family=font_name)
    except:
        pass
    return path

FONT_PATH = set_korean_font()


# ══════════════════════════════════════════
# 3D HTML 임베딩 + 클릭 시 로그인 팝업 함수
# ══════════════════════════════════════════
def embed_3d_with_overlay(html_path, height=620, overlay=True):
    """3D HTML을 임베딩합니다. overlay=True이면 클릭 시 로그인 안내 팝업을 표시합니다."""

    overlay_code = """
<style>
/* 투명 클릭 감지 레이어 */
#fu-overlay {
    position: fixed; top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 9998; cursor: pointer;
    background: transparent;
}
/* 팝업 배경 */
#fu-modal {
    display: none;
    position: fixed; top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 9999;
    background: rgba(0, 0, 0, 0.78);
    align-items: center;
    justify-content: center;
}
/* 팝업 카드 */
.fu-card {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 100%);
    border-radius: 22px;
    padding: 3rem 2.5rem;
    text-align: center;
    max-width: 420px;
    width: 90%;
    box-shadow: 0 30px 80px rgba(0,0,0,0.9);
    border: 1px solid rgba(247, 151, 30, 0.45);
    animation: fuFadeIn 0.25s ease;
}
@keyframes fuFadeIn {
    from { opacity: 0; transform: scale(0.9) translateY(20px); }
    to   { opacity: 1; transform: scale(1) translateY(0); }
}
.fu-icon   { font-size: 3.8rem; margin-bottom: 0.5rem; }
.fu-title  { color: #fff; font-size: 1.5rem; font-weight: 800; margin: 0.6rem 0; }
.fu-desc   { color: #c9d1f5; line-height: 1.75; margin-bottom: 1.8rem; font-size: 0.96rem; }
.fu-btn {
    display: inline-block;
    background: rgba(255,255,255,0.08);
    color: #c9d1f5;
    border: 1px solid rgba(255,255,255,0.22);
    padding: 0.75rem 2.2rem;
    border-radius: 30px;
    font-size: 0.95rem;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
}
.fu-btn:hover { background: rgba(255,255,255,0.15); color: #fff; }
.fu-hint {
    font-size: 0.78rem; color: #8892b0;
    margin-top: 1.6rem; line-height: 1.6;
}
.fu-hint strong { color: #f7971e; }
</style>

<!-- 투명 오버레이: 클릭을 감지합니다 -->
<div id="fu-overlay" onclick="showLoginModal()"></div>

<!-- 로그인 안내 팝업 -->
<div id="fu-modal">
    <div class="fu-card">
        <div class="fu-icon">🔐</div>
        <div class="fu-title">로그인이 필요합니다</div>
        <div class="fu-desc">
            3D 커리어 유니버스를 직접 탐험하려면<br>로그인이 필요합니다.
        </div>
        <button class="fu-btn" onclick="dismissModal()">닫기</button>
        <div class="fu-hint">
            왼쪽 메뉴 → <strong>🌌 3D 탐색기</strong> 에서<br>전체 기능을 이용할 수 있습니다.
        </div>
    </div>
</div>

<script>
function showLoginModal() {
    document.getElementById('fu-modal').style.display = 'flex';
}
function dismissModal() {
    // 팝업을 닫고 오버레이도 제거해 자유롭게 탐색 가능하게 합니다
    document.getElementById('fu-modal').style.display   = 'none';
    document.getElementById('fu-overlay').style.display = 'none';
}
</script>
"""

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        if overlay:
            html_content = html_content.replace("</body>", overlay_code + "\n</body>")
        components.html(html_content, height=height, scrolling=False)
    except FileNotFoundError:
        st.warning(f"3D HTML 파일(`{html_path}`)을 찾을 수 없습니다. 파일을 확인해 주세요.")


# ══════════════════════════════════════════
# 전문가 데이터 생성 (1,000명)
# ══════════════════════════════════════════
@st.cache_data
def generate_expanded_data():
    jobs    = ["프롬프트 엔지니어","로봇 윤리학자","ESG 컨설턴트","메타버스 건축가",
               "디지털 자산 분석가","스마트팜 운영자","동화 작가","비건 셰프",
               "자율주행 UI 디자이너","데이터 사이언티스트","로컬 크리에이터",
               "퍼스널 브랜딩 매니저","신재생 에너지 전문가","시니어 코디네이터"]
    majors  = ["철학","컴퓨터공학","심리학","경영학","서양화",
               "기계공학","사회학","생명공학","의류학과","정치외교학"]
    projects= ["뉴스레터 운영","오픈소스 기여","독립 출판","앱 개발",
               "유튜브 채널","이모티콘 작가","제로웨이스트 샵 운영","팟캐스트 진행"]
    last_names  = ["김","이","박","최","정","강","조","윤"]
    first_names = ["민준","서연","도윤","하은","주원","지우","예준","수아"]
    data = []
    for i in range(1000):
        name = random.choice(last_names) + random.choice(first_names) + f"_{i}"
        data.append({"이름": name, "현재 직업": random.choice(jobs),
                     "전공": random.choice(majors), "활동 분야": random.choice(projects)})
    return pd.DataFrame(data)

df_all = generate_expanded_data()


# ══════════════════════════════════════════
# 설문 DB 함수
# ══════════════════════════════════════════
def _seed_survey_questions(c):
    L = "1=전혀 아니다 / 2=아니다 / 3=보통 / 4=그렇다 / 5=매우 그렇다"
    J = lambda lst: json.dumps(lst, ensure_ascii=False)
    rows = [
        # ── 학생 (10문항) ────────────────────────────────────────────────
        ( 1, f"진로에 대해 평소에 얼마나 고민하나요?\n({L})",                                      "likert5",         None,                                                                                   "학생"),
        ( 2, f"나는 다양한 직업의 종류에 대해 잘 알고 있다.\n({L})",                              "likert5",         None,                                                                                   "학생"),
        ( 3, f"3D 가상공간에서 직업을 탐험하는 것이 흥미로울 것 같다.\n({L})",                    "likert5",         None,                                                                                   "학생"),
        ( 4, f"컴퓨터나 태블릿 사용이 익숙하고 편하다.\n({L})",                                   "likert5",         None,                                                                                   "학생"),
        ( 5, f"퓨처유니버스 체험 이후, 진로에 대한 생각이 넓어졌다.\n({L})",                      "likert5",         None,                                                                                   "학생"),
        ( 6, f"퓨처유니버스의 콘텐츠는 이해하기 쉬웠다.\n({L})",                                  "likert5",         None,                                                                                   "학생"),
        ( 7, "퓨처유니버스에서 가장 흥미로웠던 콘텐츠는?",                                         "multiple_choice", J(["3D 직업 현장 탐험","전문가 데이터베이스","인사이트 시각화","AI 컨설턴트"]),          "학생"),
        ( 8, "퓨처유니버스를 친구에게 추천하고 싶은 정도는?",                                      "multiple_choice", J(["꼭 추천하고 싶다","추천할 것 같다","잘 모르겠다","추천하지 않을 것 같다"]),            "학생"),
        ( 9, "퓨처유니버스를 통해 관심 갖게 된 직업 분야는?",                                     "multiple_choice", J(["IT·AI·데이터","환경·에너지","교육·상담","창작·문화·예술"]),                          "학생"),
        (10, "퓨처유니버스에 추가되면 좋겠다고 생각하는 기능이나 콘텐츠를 자유롭게 써주세요.",    "text",            None,                                                                                   "학생"),
        # ── 교사 (10문항) ────────────────────────────────────────────────
        ( 1, f"수업에서 디지털 도구나 메타버스 환경을 활용한 경험이 있으신가요?\n({L})",           "likert5",         None,                                                                                   "교사"),
        ( 2, f"퓨처유니버스가 학생들의 진로 탐색에 효과적일 것이라고 생각하시나요?\n({L})",       "likert5",         None,                                                                                   "교사"),
        ( 3, f"현재 담당 학생들의 진로 관심도가 높다고 생각하시나요?\n({L})",                     "likert5",         None,                                                                                   "교사"),
        ( 4, f"진로 교육을 위한 디지털 자료가 충분하다고 느끼시나요?\n({L})",                     "likert5",         None,                                                                                   "교사"),
        ( 5, f"퓨처유니버스가 수업 시간에 활용하기 적합하다고 생각하시나요?\n({L})",              "likert5",         None,                                                                                   "교사"),
        ( 6, f"퓨처유니버스 체험 후 학생들의 반응이 긍정적이었나요?\n({L})",                      "likert5",         None,                                                                                   "교사"),
        ( 7, "현재 진로 교육에서 가장 어려운 점은?",                                               "multiple_choice", J(["학생들의 낮은 관심","다양한 직업 정보 부족","체험 기회 부족","학생별 맞춤 지도 어려움"]), "교사"),
        ( 8, "퓨처유니버스를 수업에서 어떤 방식으로 활용하고 싶으신가요?",                        "multiple_choice", J(["정규 진로 수업 자료","방과후 활동","학급 진로 탐색 프로젝트","자유 탐색 시간"]),        "교사"),
        ( 9, "교사용 관리 기능 중 가장 필요한 것은?",                                              "multiple_choice", J(["학급 진도 관리","학생별 탐색 이력","설문 결과 분석","커리큘럼 연계 자료"]),            "교사"),
        (10, "교사용으로 추가되면 좋겠다고 생각하는 기능이나 콘텐츠를 자유롭게 써주세요.",        "text",            None,                                                                                   "교사"),
        # ── 학부모 (10문항) ──────────────────────────────────────────────
        ( 1, f"자녀의 진로에 대해 얼마나 자주 대화를 나누시나요?\n({L})",                         "likert5",         None,                                                                                   "학부모"),
        ( 2, f"자녀의 진로 탐색에 도움이 되는 정보를 구하기 어려우셨나요?\n({L})",               "likert5",         None,                                                                                   "학부모"),
        ( 3, f"퓨처유니버스가 자녀의 진로 고민에 도움이 될 것이라고 생각하시나요?\n({L})",       "likert5",         None,                                                                                   "학부모"),
        ( 4, f"자녀가 미래 직업에 대해 충분히 알고 있다고 생각하시나요?\n({L})",                  "likert5",         None,                                                                                   "학부모"),
        ( 5, f"자녀와 함께 퓨처유니버스를 활용해보고 싶으신가요?\n({L})",                         "likert5",         None,                                                                                   "학부모"),
        ( 6, f"자녀의 진로 탐색을 위해 디지털 도구 활용이 효과적이라고 생각하시나요?\n({L})",    "likert5",         None,                                                                                   "학부모"),
        ( 7, "자녀에게 가장 추천하고 싶은 콘텐츠는?",                                              "multiple_choice", J(["3D 직업 현장 탐험","전문가 데이터베이스","인사이트 시각화","AI 컨설턴트"]),          "학부모"),
        ( 8, "자녀의 진로 탐색에서 가장 어려운 점은?",                                            "multiple_choice", J(["관심 분야 파악","다양한 직업 정보 부족","체험 기회 부족","자녀와의 소통 어려움"]),     "학부모"),
        ( 9, "학부모가 퓨처유니버스에서 확인하고 싶은 기능은?",                                   "multiple_choice", J(["자녀 탐색 이력","직업별 상세 정보","진로 상담 연결","학부모 커뮤니티"]),               "학부모"),
        (10, "학부모를 위해 추가되면 좋겠다고 생각하는 기능이나 콘텐츠를 자유롭게 써주세요.",    "text",            None,                                                                                   "학부모"),
        # ── 일반인 (10문항) ──────────────────────────────────────────────
        ( 1, f"평소 미래 직업 트렌드에 얼마나 관심이 있으신가요?\n({L})",                         "likert5",         None,                                                                                   "일반인"),
        ( 2, f"3D 가상공간에서 직업을 탐험하는 것이 흥미로울 것 같다.\n({L})",                   "likert5",         None,                                                                                   "일반인"),
        ( 3, f"퓨처유니버스의 콘텐츠 수준이 적절하다고 생각하시나요?\n({L})",                    "likert5",         None,                                                                                   "일반인"),
        ( 4, f"진로 탐색에 디지털 도구를 활용하는 것이 효과적이라고 생각하시나요?\n({L})",       "likert5",         None,                                                                                   "일반인"),
        ( 5, f"퓨처유니버스를 주변에 추천하고 싶으신가요?\n({L})",                                "likert5",         None,                                                                                   "일반인"),
        ( 6, f"퓨처유니버스가 청소년 진로 교육에 도움이 된다고 생각하시나요?\n({L})",            "likert5",         None,                                                                                   "일반인"),
        ( 7, "퓨처유니버스를 알게 된 경로는?",                                                    "multiple_choice", J(["지인 추천","SNS·유튜브","뉴스·기사","검색"]),                                        "일반인"),
        ( 8, "퓨처유니버스를 어떤 목적으로 활용하고 싶으신가요?",                                 "multiple_choice", J(["직업 정보 탐색","자녀 진로 지도","교육 자료 제작","단순 흥미·체험"]),                 "일반인"),
        ( 9, "가장 관심 있는 미래 직업 분야는?",                                                  "multiple_choice", J(["IT·AI·데이터","환경·에너지","교육·복지·상담","창작·문화·예술"]),                     "일반인"),
        (10, "퓨처유니버스에 추가되면 좋겠다고 생각하는 기능이나 콘텐츠를 자유롭게 써주세요.",   "text",            None,                                                                                   "일반인"),
    ]
    c.executemany(
        "INSERT INTO survey_questions (order_num,question_text,question_type,options,respondent_type) VALUES (?,?,?,?,?)",
        rows
    )


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # users 테이블 (respondent_type, school_level 추가)
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, gender TEXT NOT NULL,
        school TEXT, grade TEXT,
        age INTEGER NOT NULL,
        respondent_type TEXT,
        school_level TEXT,
        created_at TEXT NOT NULL)""")
    for col, typ in [("respondent_type","TEXT"), ("school_level","TEXT")]:
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {typ}")
        except: pass

    # survey_questions 테이블 (respondent_type 컬럼 포함)
    c.execute("""CREATE TABLE IF NOT EXISTS survey_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, order_num INTEGER NOT NULL,
        question_text TEXT NOT NULL, question_type TEXT NOT NULL,
        options TEXT, respondent_type TEXT)""")

    # 기존 테이블에 respondent_type 컬럼이 없으면 추가 후 재시드
    existing_cols = [r[1] for r in c.execute("PRAGMA table_info(survey_questions)").fetchall()]
    if "respondent_type" not in existing_cols:
        try: c.execute("ALTER TABLE survey_questions ADD COLUMN respondent_type TEXT")
        except: pass
        c.execute("DELETE FROM survey_questions")

    c.execute("""CREATE TABLE IF NOT EXISTS survey_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL, question_id INTEGER NOT NULL,
        response_value TEXT, created_at TEXT NOT NULL)""")
    conn.commit()

    c.execute("SELECT COUNT(*) FROM survey_questions")
    if c.fetchone()[0] == 0:
        _seed_survey_questions(c)
        conn.commit()

    # Q7 보기 마이그레이션: 구현된 기능명으로 업데이트
    _J = lambda lst: json.dumps(lst, ensure_ascii=False)
    new_opts = _J(["3D 직업 현장 탐험", "전문가 데이터베이스", "인사이트 시각화", "AI 컨설턴트"])
    c.execute(
        "UPDATE survey_questions SET options=? WHERE order_num=7 AND respondent_type IN ('학생','학부모')",
        (new_opts,)
    )
    conn.commit()
    conn.close()


# ══════════════════════════════════════════
# PAGE: 홈
# ══════════════════════════════════════════
if st.session_state.page == "home":
    st.markdown("""
    <div class="hero">
        <div class="hero-title"><span class="hero-accent">Future</span> Universe</div>
        <p class="hero-sub">미래의 직업을 탐험하고, 나만의 진로를 찾아보세요</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">오늘의 3D 탐색기 미리보기</div>', unsafe_allow_html=True)
    st.caption('2026-03-30  ·  로그인 후 직접 탐험할 수 있습니다')
    embed_3d_with_overlay("future_universe_3d (1).html", height=620,
                          overlay=st.session_state.user is None)

    st.markdown('<div class="section-title">이번 주 전문가</div>', unsafe_allow_html=True)
    col_expert, col_advice = st.columns(2, gap="large")

    with col_expert:
        with st.container(border=True):
            st.markdown("**새로운 전문가**")
            st.divider()
            img_col, info_col = st.columns([1, 2])
            with img_col:
                expert_img = 'data:image/jpeg;base64,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'
                st.image(expert_img, use_container_width=True)
            with info_col:
                st.markdown('<div class="expert-name">미미미누</div>', unsafe_allow_html=True)
                st.markdown('<div class="expert-tags">입시 전문가 · 교육 콘텐츠 크리에이터 · 학습 코치 · 진로 컨설턴트 · 공부 전략가 · 유튜버 · 교육 인플루언서 · 온라인 강사</div>', unsafe_allow_html=True)

    with col_advice:
        with st.container(border=True):
            st.markdown("**전문가가 남긴 조언**")
            st.divider()
            with st.expander("from. 물리학자 김상욱 교수  →  동화중학교 김0환 학생"):
                st.markdown('<div class="qa-q">Q. 중학교 때 좋아했던 과목은?</div>', unsafe_allow_html=True)
                st.markdown('<div class="qa-a">A. 국어를 좋아했어요. 글을 읽는 것도 좋아했고, 글을 쓰는 것도 좋아했어요. 그래서 국어 선생님이 되고 싶었어요.</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="cta-banner">
        <div class="cta-title">퓨처유니버스 설문조사</div>
        <p class="cta-desc">여러분의 소중한 의견이 퓨처유니버스를 더 좋게 만드는 데 쓰입니다.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("설문조사 참여하기", use_container_width=True, type="primary"):
        st.session_state.page = "survey"
        st.session_state.survey_page = 1
        st.rerun()

    st.markdown('<div class="section-title">진로 탐색 영상</div>', unsafe_allow_html=True)
    col_v1, col_v2 = st.columns(2, gap="large")
    with col_v1:
        with st.container(border=True):
            st.markdown("**미래 직업 탐색에 도움이 되는 영상**")
            st.video('https://www.youtube.com/watch?v=-xkBMxdPaME')
            st.caption('이 정도는 봐야 미래지구인 🌍')
    with col_v2:
        with st.container(border=True):
            st.markdown("**직업의 세계**")
            st.video('https://www.youtube.com/watch?v=SyElvkVe_-g')
            st.caption('다양한 직업의 세계를 영상으로 만나보세요.')


# ══════════════════════════════════════════
# PAGE: 설문조사
# ══════════════════════════════════════════
elif st.session_state.page == "survey":
    init_db()
    progress = st.session_state.survey_page / 3

    # ── 페이지 1: 인구통계 ──────────────────────────────────────────────
    if st.session_state.survey_page == 1:
        st.title("퓨처유니버스 사용자 설문")
        st.caption("여러분의 소중한 의견이 퓨처유니버스를 더 좋게 만드는 데 쓰입니다!")
        st.progress(progress, text=f"Step {st.session_state.survey_page} / 3")
        st.divider()
        st.subheader("기본 정보")

        name   = st.text_input("이름 (또는 별명)", placeholder="홍길동", key="sv_name")
        age    = st.number_input("나이", min_value=5, max_value=80, value=14, step=1, key="sv_age")
        gender = st.radio("성별", ["남", "여", "응답하지 않음"], horizontal=True, key="sv_gender")
        rtype  = st.radio("응답자 유형", ["학생", "교사", "학부모", "일반인"], horizontal=True, key="sv_rtype")

        school_level, school, grade = None, "", ""

        if rtype == "학생":
            school_level = st.selectbox("학교급", ["초등학생", "중학생", "고등학생", "대학생·대학원생"], key="sv_level")
            school = st.text_input("학교명", placeholder="○○중학교", key="sv_school")
            grade  = st.selectbox("학년", ["1학년", "2학년", "3학년", "4학년"], key="sv_grade")
        elif rtype == "교사":
            school = st.text_input("근무 학교명", placeholder="○○중학교", key="sv_school_t")

        if st.button("다음 →", use_container_width=True, type="primary", key="sv_next"):
            if not name.strip():
                st.error("이름을 입력해 주세요.")
            elif rtype in ["학생", "교사"] and not school.strip():
                st.error("학교명을 입력해 주세요.")
            else:
                conn = get_conn()
                c = conn.cursor()
                c.execute(
                    "INSERT INTO users (name,gender,school,grade,age,respondent_type,school_level,created_at) VALUES (?,?,?,?,?,?,?,?)",
                    (name.strip(), gender, school.strip(), grade, int(age), rtype, school_level, datetime.now().isoformat())
                )
                conn.commit()
                st.session_state.survey_user_id         = c.lastrowid
                st.session_state.survey_respondent_type = rtype
                conn.close()
                st.session_state.survey_page = 2
                st.rerun()

    # ── 페이지 2: 유형별 설문 문항 ──────────────────────────────────────
    elif st.session_state.survey_page == 2:
        rtype = st.session_state.survey_respondent_type
        rtype_labels = {"학생": "학생용", "교사": "교사용", "학부모": "학부모용", "일반인": "일반인용"}
        st.title("퓨처유니버스 설문")
        st.caption(f"솔직하게 답해 줄수록 더 좋은 서비스가 만들어져요 😊  ·  **{rtype_labels.get(rtype, '')} 문항**")
        st.progress(progress, text=f"Step {st.session_state.survey_page} / 3")
        st.divider()

        conn = get_conn()
        questions = conn.execute(
            "SELECT id,order_num,question_text,question_type,options FROM survey_questions WHERE respondent_type=? ORDER BY order_num",
            (rtype,)
        ).fetchall()
        conn.close()

        responses = {}
        with st.form("survey_form"):
            for qid, order_num, text, qtype, options_json in questions:
                st.markdown(f"**Q{order_num}. {text}**")
                if qtype == "likert5":
                    val = st.radio(f"q{qid}", [1,2,3,4,5], format_func=str, horizontal=True, index=None, label_visibility="collapsed")
                elif qtype == "multiple_choice":
                    val = st.radio(f"q{qid}", json.loads(options_json), index=None, label_visibility="collapsed")
                else:
                    val = st.text_area(f"q{qid}", placeholder="자유롭게 작성해 주세요.", label_visibility="collapsed")
                responses[qid] = val
                st.write("")
            if st.form_submit_button("제출하기", use_container_width=True, type="primary"):
                missing = [f"Q{on}" for qid2, on, _, qt, _ in questions if qt != "text" and responses.get(qid2) is None]
                if missing:
                    st.error(f"아직 답하지 않은 문항: {', '.join(missing)}")
                else:
                    conn = get_conn()
                    c = conn.cursor()
                    now = datetime.now().isoformat()
                    c.executemany("INSERT INTO survey_responses (user_id,question_id,response_value,created_at) VALUES (?,?,?,?)",
                                  [(st.session_state.survey_user_id, qid, str(v), now) for qid, v in responses.items()])
                    conn.commit()
                    conn.close()
                    st.session_state.survey_page = 3
                    st.rerun()

    # ── 페이지 3: 완료 ──────────────────────────────────────────────────
    elif st.session_state.survey_page == 3:
        st.balloons()
        st.title("설문 완료")
        st.progress(progress, text=f"Step {st.session_state.survey_page} / 3")
        st.success("설문에 참여해 주셔서 감사합니다!\n여러분의 의견이 퓨처유니버스를 더 멋진 공간으로 만드는 데 큰 도움이 됩니다.")
        st.divider()
        if st.button("홈으로 돌아가기", use_container_width=True):
            st.session_state.survey_page            = 1
            st.session_state.survey_user_id         = None
            st.session_state.survey_respondent_type = "학생"
            st.session_state.page = "home"
            st.rerun()


# ══════════════════════════════════════════
# PAGE: 3D 탐색기
# ══════════════════════════════════════════
elif st.session_state.page == "3d":
    st.title("3D 커리어 유니버스 탐색기")
    st.write("전문가는 행성(Planet), 직업·전공·활동은 별(Star)이 되어 연결됩니다.")
    st.info("노드가 많아 복잡하다면 필터를 사용해 관심 있는 분야만 탐색하세요.")

    df_sample = show_career_filters(df_all)

    @st.cache_data
    def get_3d_layout(df):
        all_nodes = (list(df['이름'].unique()) + list(df['현재 직업'].unique()) +
                     list(df['전공'].unique()) + list(df['활동 분야'].unique()))
        node_map  = {node: i for i, node in enumerate(all_nodes)}
        coords    = np.zeros((len(all_nodes), 3))
        centers   = {'expert': np.array([0,0,0]), 'job': np.array([5,5,5]),
                     'major':  np.array([-5,5,5]), 'project': np.array([5,-5,5])}
        for i, node in enumerate(all_nodes):
            if   node in df['이름'].values:        coords[i] = centers['expert']  + np.random.uniform(-2,2,3)
            elif node in df['현재 직업'].values:    coords[i] = centers['job']     + np.random.uniform(-2,2,3)
            elif node in df['전공'].values:         coords[i] = centers['major']   + np.random.uniform(-2,2,3)
            else:                                   coords[i] = centers['project'] + np.random.uniform(-2,2,3)
        return all_nodes, node_map, coords

    labels, node_map, coords = get_3d_layout(df_sample)

    html_path = "future_universe_3d (1).html"
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=760, scrolling=True)
    except FileNotFoundError:
        st.error(f"3D HTML 파일을 찾을 수 없습니다: {html_path}")


# ══════════════════════════════════════════
# PAGE: 전문가 데이터베이스
# ══════════════════════════════════════════
elif st.session_state.page == "db":
    st.title("전문가 커리어 데이터")
    st.write("1,000명의 전문가 데이터를 필터링하여 상세히 확인하세요.")
    df_filtered = show_career_filters(df_all)
    st.dataframe(df_filtered, use_container_width=True)
    csv = df_filtered.to_csv(index=False).encode('utf-8-sig')
    st.download_button("Career_Data.csv 다운로드", data=csv, file_name='career_data.csv', mime='text/csv')


# ══════════════════════════════════════════
# PAGE: 전문가 분포 현황
# ══════════════════════════════════════════
elif st.session_state.page == "distribution":
    st.title("전문가 분포 현황")
    st.write("유니버스에 등록된 1,000명 전문가들의 분포 데이터입니다.")
    df_dist = show_career_filters(df_all)
    m1, m2, m3 = st.columns(3)
    m1.metric("표시 중인 전문가", f"{len(df_dist)}명")
    m2.metric("활성화 직업군",    f"{df_dist['현재 직업'].nunique()}종")
    m3.metric("다양한 전공 수",   f"{df_dist['전공'].nunique()}종")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("직업군별 인원 분포")
        job_counts = df_dist["현재 직업"].value_counts().reset_index()
        job_counts.columns = ["직업", "인원"]
        fig = px.bar(job_counts, x="인원", y="직업", orientation='h',
                     color="인원", color_continuous_scale="Viridis", text_auto=True)
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("전공 계열 분포")
        major_counts = df_dist["전공"].value_counts().reset_index()
        major_counts.columns = ["전공", "인원"]
        fig = px.pie(major_counts, values="인원", names="전공", hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("활동 분야 인기 순위")
    project_counts = df_dist["활동 분야"].value_counts().reset_index()
    project_counts.columns = ["활동 분야", "인원"]
    fig = px.treemap(project_counts, path=["활동 분야"], values="인원",
                     color="인원", color_continuous_scale="RdBu")
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════
# PAGE: 인사이트 시각화
# ══════════════════════════════════════════
elif st.session_state.page == "insights":
    st.title("진로 확장 인사이트")
    target_job  = st.selectbox("분석할 직업 선택", sorted(df_all["현재 직업"].unique().tolist()))
    analysis_df = df_all[df_all["현재 직업"] == target_job]
    col1, col2  = st.columns(2)
    with col1:
        st.subheader(f"{target_job} — 전공 분포")
        major_counts = analysis_df["전공"].value_counts()
        plt.rcParams['font.family'] = font_manager.FontProperties(fname=FONT_PATH).get_name()
        fig_pie, ax_pie = plt.subplots(figsize=(8,8))
        fig_pie.patch.set_facecolor('white')
        ax_pie.pie(major_counts, labels=major_counts.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
        st.pyplot(fig_pie)
    with col2:
        st.subheader(f"{target_job} — 활동 분야")
        text = " ".join(analysis_df["활동 분야"].tolist())
        try:
            wc = WordCloud(font_path=FONT_PATH, background_color="white", width=800, height=800).generate(text)
            fig_wc, ax_wc = plt.subplots(figsize=(8,8))
            ax_wc.imshow(wc, interpolation='bilinear')
            ax_wc.axis("off")
            st.pyplot(fig_wc)
        except:
            st.table(analysis_df["활동 분야"].value_counts().head(5))
    st.info(f"{target_job} 직업군에는 {major_counts.index[0]} 외에도 다양한 전공자들이 활동 중입니다.")


# ══════════════════════════════════════════
# PAGE: AI 컨설턴트
# ══════════════════════════════════════════
elif st.session_state.page == "ai":
    st.title("Career AI 컨설턴트")
    st.write("유니버스의 데이터를 기반으로 커리어 패스를 분석합니다.")
    with st.chat_message("assistant"):
        st.write("안녕하세요! 현재 고민 중인 직무나 전공을 말씀해주시면 유니버스의 1,000명 전문가 데이터를 기반으로 조언해 드릴게요.")
    user_input = st.text_input("질문을 입력하세요 (예: 심리학 전공인데 데이터 사이언티스트가 될 수 있을까요?)")
    if user_input:
        with st.spinner("유니버스 데이터 분석 중..."):
            time.sleep(1.5)
            st.info(f"'{user_input}'에 대한 유니버스 분석 결과")
            relevant_experts = df_all[df_all['현재 직업'].str.contains("데이터") | df_all['전공'].str.contains("심리")].head(3)
            st.markdown(f"""
            ### AI 분석 리포트
            1. **데이터 기반 가능성** — 유니버스 내에서 유사한 경로를 가진 전문가가 **{len(relevant_experts)}명** 발견되었습니다.
            2. **추천 전략** — 전공의 인간 이해 능력과 활동 분야를 통한 데이터 분석 실무를 결합하세요.
            3. **롤모델 추천**
            """)
            for _, row in relevant_experts.iterrows():
                st.write(f"— **{row['이름']}**: {row['전공']} 전공 · {row['현재 직업']} ({row['활동 분야']})")


# ══════════════════════════════════════════
# PAGE: 로드맵 설계
# ══════════════════════════════════════════
elif st.session_state.page == "roadmap":
    st.title("커리어 로드맵 설계")
    st.write("목표 직업까지의 단계별 계획을 생성합니다.")
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        start_point = st.text_input("현재 상태 (전공/직무)", "예: 경영학부 대학생")
    with col_input2:
        end_goal = st.selectbox("목표 직업", sorted(df_all["현재 직업"].unique().tolist()))
    if st.button("로드맵 생성하기"):
        st.divider()
        st.subheader(f"{start_point}  →  {end_goal}")
        steps = [
            {"step": "Step 1 — 기초 역량",    "desc": f"{end_goal}와 관련된 기술 블로그·뉴스레터 구독 시작"},
            {"step": "Step 2 — 실무 활동",    "desc": "전문가들이 선호하는 오픈소스 기여 또는 앱 개발 시도"},
            {"step": "Step 3 — 네트워크 확장", "desc": "관련 커뮤니티 활동 및 퍼스널 브랜딩 구축"},
            {"step": "Step 4 — 실전 도전",    "desc": "포트폴리오 완성 및 인턴십·이직 도전"},
        ]
        for s in steps:
            with st.expander(s["step"]):
                st.write(s["desc"])
        fig_line = go.Figure(data=[go.Scatter(
            x=[1,2,3,4], y=[1,1,1,1],
            mode='lines+markers+text',
            text=[s["step"] for s in steps],
            textposition="top center",
            marker=dict(size=20, color="#0053A5")
        )])
        fig_line.update_layout(height=200, showlegend=False,
                               xaxis=dict(visible=False), yaxis=dict(visible=False))
        st.plotly_chart(fig_line, use_container_width=True)


# ══════════════════════════════════════════
# PAGE: 관리자 대시보드
# ══════════════════════════════════════════
elif st.session_state.page == "admin_dashboard":
    if not st.session_state.user or st.session_state.user.get("role") != "admin":
        st.error("관리자만 접근할 수 있는 페이지입니다.")
        st.stop()

    st.title("관리자 대시보드")
    st.caption("설문 응답 분석 및 원데이터 다운로드")
    st.divider()

    conn = get_conn()
    users_df     = pd.read_sql("SELECT * FROM users", conn)
    questions_df = pd.read_sql("SELECT * FROM survey_questions ORDER BY respondent_type, order_num", conn)
    responses_df = pd.read_sql("SELECT * FROM survey_responses", conn)
    conn.close()

    total = len(users_df)
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("총 응답자 수", f"{total}명")
    col_m2.metric("응답자 유형", f"{users_df['respondent_type'].nunique()}종")
    st.divider()

    all_types   = sorted(users_df["respondent_type"].dropna().unique().tolist())
    tab_labels  = ["전체"] + all_types
    tabs        = st.tabs(tab_labels)

    for i, tab_label in enumerate(tab_labels):
        with tabs[i]:
            if tab_label == "전체":
                u_df = users_df
                q_df = questions_df
                r_df = responses_df
            else:
                u_df = users_df[users_df["respondent_type"] == tab_label]
                q_df = questions_df[questions_df["respondent_type"] == tab_label]
                valid_uids = u_df["id"].tolist()
                valid_qids = q_df["id"].tolist()
                r_df = responses_df[
                    responses_df["user_id"].isin(valid_uids) &
                    responses_df["question_id"].isin(valid_qids)
                ]

            st.metric(f"응답자 ({tab_label})", f"{len(u_df)}명")

            if r_df.empty:
                st.info("아직 응답 데이터가 없습니다.")
                continue

            st.subheader("문항별 결과")
            for _, q in q_df.iterrows():
                qid   = q["id"]
                qtype = q["question_type"]
                qtext = q["question_text"].split("\n")[0]
                order = int(q["order_num"])
                st.markdown(f"**Q{order}. {qtext}**")
                q_vals = r_df[r_df["question_id"] == qid]["response_value"]

                if q_vals.empty:
                    st.caption("아직 응답 없음")
                elif qtype == "likert5":
                    nums = pd.to_numeric(q_vals, errors="coerce").dropna()
                    if not nums.empty:
                        c1, c2 = st.columns([1, 3])
                        with c1:
                            st.metric("평균", f"{nums.mean():.2f}")
                            st.metric("응답 수", f"{len(nums)}명")
                        with c2:
                            st.bar_chart(nums.value_counts().sort_index().rename("응답 수"))
                elif qtype == "multiple_choice":
                    st.bar_chart(q_vals.value_counts().rename("응답 수"))
                elif qtype == "text":
                    texts = q_vals[q_vals.str.strip() != ""].tolist()
                    if texts:
                        for t in texts:
                            st.write(f"- {t}")
                    else:
                        st.caption("자유 응답 없음")
                st.write("")

            st.divider()
            st.subheader("원데이터")
            if len(u_df) > 0:
                merged = r_df.merge(q_df[["id", "order_num"]], left_on="question_id", right_on="id", how="left")
                merged = merged.dropna(subset=["order_num"])
                merged["문항"] = merged["order_num"].apply(lambda x: f"Q{int(x)}")
                pivot = merged.pivot_table(
                    index="user_id", columns="문항",
                    values="response_value", aggfunc="first"
                )
                user_info = u_df[["id", "name", "gender", "school", "grade", "age", "respondent_type"]].set_index("id")
                result = user_info.join(pivot)
                st.dataframe(result, use_container_width=True)

                fname = f"survey_{tab_label}.csv" if tab_label != "전체" else "survey_all.csv"
                csv = result.to_csv(encoding="utf-8-sig").encode("utf-8-sig")
                st.download_button(
                    f"CSV 다운로드 ({tab_label})",
                    data=csv,
                    file_name=fname,
                    mime="text/csv",
                    use_container_width=True,
                    key=f"dl_{tab_label}"
                )
            else:
                st.info("해당 유형의 응답 데이터가 없습니다.")
