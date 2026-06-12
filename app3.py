import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from matplotlib import font_manager, rc
import platform
import sqlite3
import json
import base64
import hashlib
import os
import shutil
import math
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
_openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
APP_DIR = os.path.dirname(os.path.abspath(__file__))


def _image_data_uri(filename):
    image_path = os.path.join(APP_DIR, filename)
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


HERO_BG_URI = _image_data_uri("bg_image.png")

def _has_usable_openai_key():
    key = (os.getenv("OPENAI_API_KEY") or "").strip()
    return key.startswith("sk-") and len(key) > 40


def _is_valid_nickname(name):
    return bool(re.fullmatch(r"[가-힣0-9]{1,10}", name))


def _local_career_answer(question, my_nodes=None, connected_names=None):
    nodes = my_nodes or []
    experts = connected_names or []
    node_text = ", ".join(nodes[:4]) if nodes else "아직 저장한 관심 노드가 없습니다"
    expert_text = "; ".join(experts[:2]) if experts else "아직 연결된 전문가 데이터가 없습니다"
    return (
        "현재 AI API 설정을 확인해야 해서, 우선 로컬 가이드로 답변드릴게요.\n\n"
        f"- 질문 핵심: {question}\n"
        f"- 내 관심 분야: {node_text}\n"
        f"- 참고할 전문가 연결: {expert_text}\n\n"
        "추천 순서는 1) 관심 분야에서 실제 직업 2~3개를 고르고, "
        "2) 필요한 전공/기술을 비교하고, 3) 전문가 Q&A에 구체적인 질문을 남기는 것입니다. "
        "질문을 한 문장 더 구체화하면 더 좋은 진로 후보를 좁힐 수 있어요."
    )

def _local_roadmap(start_point, end_goal, my_nodes=None):
    interest = f" 관심 분야({', '.join(my_nodes[:3])})와 연결해" if my_nodes else ""
    return f"""Step 1 — 현재 위치 정리: {start_point}에서 이미 가진 과목, 활동, 강점을 적고 {end_goal}에 필요한 역량과 비교하세요.
Step 2 — 핵심 역량 선택: {end_goal}에 필요한 기본 지식 2개와 실습 도구 1개를 정해 4주 동안 학습하세요.
Step 3 — 작은 프로젝트 만들기:{interest} 결과물 하나를 만들어 포트폴리오로 남기세요.
Step 4 — 전문가 피드백 받기: 관련 전문가에게 진로 경로, 준비 순서, 실제 업무에 대해 질문하고 다음 행동을 수정하세요."""

def _local_career_answer(question, my_nodes=None, connected_names=None):
    nodes = my_nodes or []
    experts = connected_names or []
    node_text = ", ".join(nodes[:4]) if nodes else "아직 저장한 관심 노드가 없습니다"
    expert_text = "; ".join(experts[:2]) if experts else "아직 연결된 전문가 데이터가 없습니다"
    return (
        "현재 AI API 설정을 확인해야 해서, 우선 로컬 가이드로 답변드릴게요.\n\n"
        f"- 질문 핵심: {question}\n"
        f"- 내 관심 분야: {node_text}\n"
        f"- 참고할 전문가 연결: {expert_text}\n\n"
        "추천 순서는 1) 관심 분야에서 실제 직업 2~3개를 고르고, "
        "2) 필요한 전공/기술을 비교하고, 3) 전문가 Q&A에 구체적인 질문을 남기는 것입니다. "
        "질문을 한 문장 더 구체화하면 더 좋은 진로 후보를 좁힐 수 있어요."
    )

def _local_roadmap(start_point, end_goal, my_nodes=None):
    interest = f" 관심 분야({', '.join(my_nodes[:3])})와 연결해" if my_nodes else ""
    return f"""Step 1 - 현재 위치 정리: {start_point}에서 이미 가진 과목, 활동, 강점을 적고 {end_goal} 활동 분야에 필요한 역량과 비교하세요.
Step 2 - 핵심 역량 선택: {end_goal}에 필요한 기본 지식 2개와 실습 도구 1개를 정해 4주 동안 학습하세요.
Step 3 - 작은 프로젝트 만들기:{interest} 결과물 하나를 만들어 포트폴리오로 남기세요.
Step 4 - 전문가 피드백 받기: 관련 전문가에게 진로 경로, 준비 순서, 실제 업무에 대해 질문하고 다음 행동을 수정하세요."""

def _local_career_answer(question, my_nodes=None, connected_names=None):
    nodes = my_nodes or []
    experts = connected_names or []
    node_text = ", ".join(nodes[:4]) if nodes else "\uc544\uc9c1 \uc800\uc7a5\ud55c \uad00\uc2ec \ub178\ub4dc\uac00 \uc5c6\uc2b5\ub2c8\ub2e4"
    expert_text = "; ".join(experts[:2]) if experts else "\uc544\uc9c1 \uc5f0\uacb0\ub41c \uc804\ubb38\uac00 \ub370\uc774\ud130\uac00 \uc5c6\uc2b5\ub2c8\ub2e4"
    return (
        "\ud604\uc7ac AI API \uc124\uc815\uc744 \ud655\uc778\ud574\uc57c \ud574\uc11c, \uc6b0\uc120 \ub85c\uceec \uac00\uc774\ub4dc\ub85c \ub2f5\ubcc0\ub4dc\ub9b4\uac8c\uc694.\n\n"
        f"- \uc9c8\ubb38 \ud575\uc2ec: {question}\n"
        f"- \ub0b4 \uad00\uc2ec \ubd84\uc57c: {node_text}\n"
        f"- \ucc38\uace0\ud560 \uc804\ubb38\uac00 \uc5f0\uacb0: {expert_text}\n\n"
        "\ucd94\ucc9c \uc21c\uc11c\ub294 1) \uad00\uc2ec \ubd84\uc57c\uc5d0\uc11c \uc2e4\uc81c \uc9c1\uc5c5 2~3\uac1c\ub97c \uace0\ub974\uace0, "
        "2) \ud544\uc694\ud55c \uc804\uacf5/\uae30\uc220\uc744 \ube44\uad50\ud558\uace0, 3) \uc804\ubb38\uac00 Q&A\uc5d0 \uad6c\uccb4\uc801\uc778 \uc9c8\ubb38\uc744 \ub0a8\uae30\ub294 \uac83\uc785\ub2c8\ub2e4. "
        "\uc9c8\ubb38\uc744 \ud55c \ubb38\uc7a5 \ub354 \uad6c\uccb4\ud654\ud558\uba74 \ub354 \uc88b\uc740 \uc9c4\ub85c \ud6c4\ubcf4\ub97c \uc881\ud790 \uc218 \uc788\uc5b4\uc694."
    )

def _local_roadmap(start_point, end_goal, my_nodes=None):
    interest = f" \uad00\uc2ec \ubd84\uc57c({', '.join(my_nodes[:3])})\uc640 \uc5f0\uacb0\ud574" if my_nodes else ""
    return f"""Step 1 - \ud604\uc7ac \uc704\uce58 \uc815\ub9ac: {start_point}\uc5d0\uc11c \uc774\ubbf8 \uac00\uc9c4 \uacfc\ubaa9, \ud65c\ub3d9, \uac15\uc810\uc744 \uc801\uace0 {end_goal} \ud65c\ub3d9 \ubd84\uc57c\uc5d0 \ud544\uc694\ud55c \uc5ed\ub7c9\uacfc \ube44\uad50\ud558\uc138\uc694.
Step 2 - \ud575\uc2ec \uc5ed\ub7c9 \uc120\ud0dd: {end_goal}\uc5d0 \ud544\uc694\ud55c \uae30\ubcf8 \uc9c0\uc2dd 2\uac1c\uc640 \uc2e4\uc2b5 \ub3c4\uad6c 1\uac1c\ub97c \uc815\ud574 4\uc8fc \ub3d9\uc548 \ud559\uc2b5\ud558\uc138\uc694.
Step 3 - \uc791\uc740 \ud504\ub85c\uc81d\ud2b8 \ub9cc\ub4e4\uae30:{interest} \uacb0\uacfc\ubb3c \ud558\ub098\ub97c \ub9cc\ub4e4\uc5b4 \ud3ec\ud2b8\ud3f4\ub9ac\uc624\ub85c \ub0a8\uae30\uc138\uc694.
Step 4 - \uc804\ubb38\uac00 \ud53c\ub4dc\ubc31 \ubc1b\uae30: \uad00\ub828 \uc804\ubb38\uac00\uc5d0\uac8c \uc9c4\ub85c \uacbd\ub85c, \uc900\ube44 \uc21c\uc11c, \uc2e4\uc81c \uc5c5\ubb34\uc5d0 \ub300\ud574 \uc9c8\ubb38\ud558\uace0 \ub2e4\uc74c \ud589\ub3d9\uc744 \uc218\uc815\ud558\uc138\uc694."""

st.set_page_config(page_title="Future Universe", page_icon="🚀", layout="wide")

# ── 세션 초기화 ────────────────────────────────────────
if "page"                   not in st.session_state: st.session_state.page                   = "home"
if "survey_page"            not in st.session_state: st.session_state.survey_page            = 1
if "survey_participant_id"  not in st.session_state: st.session_state.survey_participant_id  = None
if "survey_respondent_type" not in st.session_state: st.session_state.survey_respondent_type = "학생"
if "account"                not in st.session_state: st.session_state.account                = None

_requested_page = st.query_params.get("fu_page")
if isinstance(_requested_page, list):
    _requested_page = _requested_page[0] if _requested_page else None
if _requested_page == "home":
    st.session_state.page = "home"
    try:
        del st.query_params["fu_page"]
    except Exception:
        pass

# ── 전체 스타일 CSS ────────────────────────────────────
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

/* ── 기본 폰트 — font-size는 html에만 ── */
html {
    font-size: 16px;
}
html, body, .stApp, button, input, textarea, select {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Noto Sans KR', sans-serif !important;
}

[data-testid="stMarkdownContainer"],
[data-testid="stText"],
[data-testid="stWidgetLabel"],
[data-testid="stCaptionContainer"],
[data-testid="stMetric"],
[data-testid="stDataFrame"],
[role="dialog"] {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Noto Sans KR', sans-serif !important;
}

/* Streamlit 내부 아이콘 폰트는 전역 폰트로 덮어쓰면 arrow_drop_down 같은 텍스트로 보입니다. */
[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"] *,
.material-icons,
.material-symbols,
.material-symbols-rounded,
.material-symbols-outlined {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    font-weight: normal !important;
    font-style: normal !important;
    font-size: inherit !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    display: inline-block !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    direction: ltr !important;
    -webkit-font-feature-settings: 'liga' !important;
    font-feature-settings: 'liga' !important;
    -webkit-font-smoothing: antialiased !important;
}

/* ── 컬러 팔레트 변수 ── */
:root {
    --bg-main:    #13151C;
    --bg-card:    #191C27;
    --bg-panel:   #151A25;
    --bg-sidebar: #1C1E28;
    --text-1:     #E2EAFF;   /* 제목·강조 */
    --text-2:     #C4D4F6;   /* 본문 */
    --text-3:     #AFC2EF;   /* 보조·캡션 */
    --accent:     #4A90FF;
    --accent-2:   #27D6A2;
    --accent-3:   #FFB84A;
    --accent-soft: rgba(74,144,255,0.12);
    --border:     rgba(165,195,255,0.46);
    --border-soft: rgba(150,178,230,0.34);
    --border-strong: rgba(170,205,255,0.68);
}

/* ── 전체 배경 ── */
.stApp {
    background: var(--bg-main) !important;
}
.main .block-container {
    padding: 0.55rem 2.5rem 2.5rem;
    max-width: 1280px;
    background: transparent;
}
[data-testid="stAppViewContainer"] > .main {
    padding-top: 0 !important;
}

/* ── 상단 헤더바 완전 숨김 ── */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    display: none !important;
}
#MainMenu { visibility: hidden !important; }

/* ── 사이드바 — 메인보다 밝은 톤으로 구분 ── */
[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebarNav"] { display: none; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: rgba(200,220,255,0.75) !important;
    font-size: 0.88rem !important;
}
/* 사이드바 내부 기본 여백 최소화 */
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}
[data-testid="stSidebarContent"] {
    padding-top: 0.6rem !important;
}
[data-testid="stSidebarContent"] > div:first-child {
    padding-top: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

/* ── 사이드바 섹션 헤더 ── */
.nav-section {
    color: #91A5D6;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    padding: 0.55rem 0 0.15rem 0.9rem;
    display: block;
}

/* ── EVENT 뱃지 ── */
.event-badge-chip {
    background: rgba(255,184,74,0.14);
    color: #FFD89A;
    font-size: 0.58rem;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 4px;
    letter-spacing: 0.9px;
    text-transform: uppercase;
    display: inline-block;
    pointer-events: none;
    border: 1px solid rgba(255,184,74,0.56);
    box-shadow: none;
}
.nav-divider {
    border: none;
    border-top: 1px solid rgba(165,195,255,0.38);
    margin: 0.2rem 0;
}

/* ── nav 버튼 비활성 ── */
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    background: transparent !important;
    border: none !important;
    color: rgba(190,210,255,0.7) !important;
    text-align: left !important;
    padding: 0.28rem 0.9rem !important;
    border-radius: 4px !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    justify-content: flex-start !important;
    letter-spacing: 0.01em !important;
    transition: all 0.12s ease !important;
    min-height: unset !important;
    height: auto !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
    background: rgba(255,255,255,0.07) !important;
    color: #fff !important;
}

/* ── nav 버튼 활성 ── */
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background: rgba(74,144,255,0.12) !important;
    border: none !important;
    border-left: 2px solid #4A90FF !important;
    color: #C8DCFF !important;
    font-weight: 600 !important;
    text-align: left !important;
    padding: 0.28rem 0.9rem !important;
    border-radius: 0 4px 4px 0 !important;
    font-size: 0.88rem !important;
    justify-content: flex-start !important;
    letter-spacing: 0.01em !important;
    min-height: unset !important;
    height: auto !important;
}

/* ── 제목 — 3단계 텍스트 계층 ── */
h1 {
    font-size: 2.1rem !important;
    font-weight: 700 !important;
    color: var(--text-1) !important;
    letter-spacing: -0.5px !important;
    line-height: 1.2 !important;
}
h2 {
    font-size: 1.45rem !important;
    font-weight: 600 !important;
    color: var(--text-1) !important;
}
h3 {
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    color: var(--text-2) !important;
}

/* ── 본문 — div 제외, 텍스트 요소만 ── */
p, li {
    color: var(--text-2);
}
/* Streamlit 텍스트 컴포넌트 */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stText"] {
    color: var(--text-2) !important;
}
/* 캡션 */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * {
    color: var(--text-3) !important;
}

/* ── 섹션 타이틀 ── */
.section-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-1);
    border-left: 3px solid var(--accent);
    padding-left: 0.75rem;
    margin: 1.8rem 0 0.8rem 0;
    letter-spacing: -0.1px;
}

/* ── 히어로 배너 ── */
.hero {
    background:
        linear-gradient(135deg, rgba(15,27,54,0.96) 0%, rgba(20,32,50,0.98) 58%, rgba(11,18,31,0.98) 100%);
    border: 1px solid var(--border-strong);
    padding: 3rem 2.75rem;
    border-radius: 8px;
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
    min-height: 360px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at 78% 34%, rgba(39,214,162,0.16) 0%, transparent 28%),
        radial-gradient(circle at 86% 76%, rgba(74,144,255,0.20) 0%, transparent 34%),
        linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px);
    background-size: auto, auto, 54px 54px, 54px 54px;
    pointer-events: none;
    opacity: 0.9;
}
.hero::after {
    display: none;
}

.hero-title {
    font-size: 2.85rem;
    font-weight: 800;
    color: var(--text-1);
    letter-spacing: 0;
    margin-bottom: 0.7rem;
    line-height: 1.12;
    position: relative;
    max-width: 1120px;
    word-break: keep-all;
    overflow-wrap: normal;
}
.hero-kicker {
    color: var(--accent-2);
    font-size: 0.76rem;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.7rem;
    position: relative;
}
.hero-accent { color: var(--accent-2); }
.hero-sub {
    font-size: 1.05rem;
    color: var(--text-2);
    margin: 0;
    line-height: 1.72;
    position: relative;
    max-width: 680px;
}
.home-flow {
    display: flex;
    gap: 0.45rem;
    flex-wrap: wrap;
    margin-top: 0.95rem;
    position: relative;
}

.shortcut-title {
    color: var(--text-1);
    font-size: 0.96rem;
    font-weight: 700;
    margin: 0.15rem 0 0.65rem;
}
.home-flow span {
    color: rgba(210,226,255,0.72);
    font-size: 0.78rem;
    border: 1px solid var(--border-soft);
    border-radius: 999px;
    padding: 0.34rem 0.62rem;
    background: rgba(10,16,28,0.35);
}

/* ── 히어로 지표 카드 ── */
.hero-stat-wrap {
    display: flex;
    gap: 0.85rem;
    margin-top: 1.6rem;
    flex-wrap: wrap;
    position: relative;
}
.hero-stat {
    text-align: left;
    min-width: 126px;
    padding: 0.85rem 1rem;
    background: rgba(10,16,28,0.46);
    border: 1px solid var(--border-soft);
    border-radius: 6px;
}
.hero-stat-num {
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--accent-2);
    line-height: 1;
}
.hero-stat-label {
    font-size: 0.75rem;
    color: var(--text-3);
    margin-top: 3px;
}

/* ── 기능 소개 카드 ── */
.feature-cards {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.75rem;
    margin: 1rem 0 1.4rem;
}
.feature-card {
    min-width: 145px;
    background: linear-gradient(180deg, rgba(25,28,39,0.95), rgba(21,26,37,0.95));
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.1rem;
    transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
}
.feature-card:hover {
    transform: translateY(-2px);
    border-color: rgba(110,170,255,0.68);
    background: linear-gradient(180deg, rgba(27,34,49,0.98), rgba(20,27,41,0.98));
}
.feature-card:nth-child(2) { border-color: rgba(39,214,162,0.44); }
.feature-card:nth-child(3) { border-color: rgba(255,184,74,0.46); }
.feature-card:nth-child(4) { border-color: rgba(139,184,255,0.50); }
.feature-card-icon { font-size: 1.35rem; }
.feature-card-title {
    font-weight: 600;
    color: var(--text-1);
    font-size: 0.9rem;
    margin: 0.35rem 0 0.2rem;
}
.feature-card-desc {
    font-size: 0.78rem;
    color: #B8C8EF;
    line-height: 1.5;
}

/* ── 전문가 ── */
.expert-name { font-size: 1.1rem; font-weight: 700; color: var(--text-1); margin: 0.4rem 0 0.2rem; }
.expert-tags { font-size: 0.84rem; color: #B8C8EF; line-height: 1.8; }

/* ── CTA 배너 (버튼 포함 일체형) ── */
.cta-banner {
    background: linear-gradient(135deg, rgba(39,214,162,0.14) 0%, rgba(15,26,54,0.96) 58%, rgba(255,184,74,0.08) 100%);
    border: 1px solid rgba(39,214,162,0.58);
    padding: 1.5rem 1.75rem;
    border-radius: 8px;
    text-align: left;
    margin: 1.8rem 0 0 0;
    position: relative;
    overflow: hidden;
}
.cta-banner::after {
    content: '';
    position: absolute;
    right: 1.5rem;
    top: 50%;
    width: 120px;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(39,214,162,0.55));
}
.cta-title { font-size: 1.15rem; font-weight: 700; color: var(--text-1); margin-bottom: 0.35rem; }
.cta-desc  { font-size: 0.9rem; color: var(--text-2); margin: 0 0 1rem; max-width: 720px; }

/* ── Q&A ── */
.qa-q {
    background: rgba(74,144,255,0.07);
    border: 1px solid rgba(122,174,255,0.72);
    border-radius: 4px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.45rem;
    font-weight: 600;
    color: #8BB8FF;
    font-size: 0.95rem;
}
.qa-a {
    background: rgba(0,210,150,0.05);
    border: 1px solid rgba(39,214,162,0.62);
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
    border: 1px solid var(--border-strong) !important;
    color: #C0D2F5 !important;
    border-radius: 4px !important;
    font-size: 0.95rem !important;
}
[data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *) * {
    color: inherit !important;
}
[data-testid="stFormSubmitButton"] [data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #1A4FCC, #2563EB) !important;
    border: none !important;
    color: #fff !important;
}
[data-testid="stFormSubmitButton"] button[kind="primary"],
[data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #1A4FCC, #2563EB) !important;
    border: none !important;
    color: #fff !important;
}
[data-testid="stFormSubmitButton"] button[kind="primary"] *,
[data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primary"] * {
    color: #fff !important;
}
[data-testid="stFormSubmitButton"] [data-testid="stBaseButton-secondary"] {
    background: rgba(74,144,255,0.08) !important;
    border: 1px solid var(--border) !important;
    color: #C0D2F5 !important;
}
[data-testid="stFormSubmitButton"] button[kind="secondary"],
[data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-secondary"] {
    background: rgba(74,144,255,0.08) !important;
    border: 1px solid var(--border) !important;
    color: #C0D2F5 !important;
}

/* ── 입력 위젯 ── */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: #162038 !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 4px !important;
    color: #D0DFFF !important;
    font-size: 0.95rem !important;
}
.stTextInput input::placeholder,
.stNumberInput input::placeholder,
.stTextArea textarea::placeholder,
input::placeholder,
textarea::placeholder {
    color: #7F91BF !important;
    opacity: 1 !important;
}
.stTextInput input::-webkit-input-placeholder,
.stNumberInput input::-webkit-input-placeholder,
.stTextArea textarea::-webkit-input-placeholder,
input::-webkit-input-placeholder,
textarea::-webkit-input-placeholder {
    color: #7F91BF !important;
    opacity: 1 !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: #4A90FF !important;
    box-shadow: 0 0 0 2px rgba(74,144,255,0.12) !important;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #162038 !important;
    border: 1px solid var(--border-strong) !important;
    color: #D0DFFF !important;
    border-radius: 4px !important;
}

/* ── 컨테이너 카드 ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 8px !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.08), 0 12px 28px rgba(0,0,0,0.18) !important;
}

/* ── 메트릭 ── */
[data-testid="stMetric"] label { color: rgba(190,215,255,0.7) !important; font-size: 0.9rem !important; }
[data-testid="stMetricValue"] { color: #E4EDFF !important; font-size: 1.9rem !important; font-weight: 700 !important; }

/* ── 구분선 ── */
hr { border-color: rgba(110,170,255,0.38) !important; }

/* ── "Press Enter to submit form" 숨김 ── */
[data-testid="InputInstructions"] { display: none !important; }

/* ── 다이얼로그 — [role="dialog"] 로 확실히 타겟 ── */

/* 모든 텍스트 진하게 */
[role="dialog"] p,
[role="dialog"] span,
[role="dialog"] div,
[role="dialog"] label,
[role="dialog"] h2,
[role="dialog"] h3 {
    color: #1a1a2e !important;
}

/* 탭 버튼 */
[role="dialog"] button[role="tab"] {
    color: #555 !important;
    font-weight: 600 !important;
    background: transparent !important;
    border: none !important;
}
[role="dialog"] button[role="tab"][aria-selected="true"] {
    color: #2563EB !important;
}

/* 레이블 */
[role="dialog"] label {
    color: #1a1a2e !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
}

/* 입력창 — 흰 배경, 진한 글씨 */
[role="dialog"] input,
[role="dialog"] textarea,
[role="dialog"] .stTextInput input,
[role="dialog"] .stNumberInput input,
[role="dialog"] .stTextArea textarea {
    background: #ffffff !important;
    border: 1px solid #c0c8d8 !important;
    border-radius: 6px !important;
    color: #111111 !important;
    font-size: 0.95rem !important;
}
[role="dialog"] input::placeholder,
[role="dialog"] textarea::placeholder {
    color: #aaa !important;
}
[role="dialog"] input:focus,
[role="dialog"] textarea:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 2px rgba(37,99,235,0.15) !important;
}

/* selectbox / multiselect */
[role="dialog"] .stSelectbox > div > div,
[role="dialog"] .stMultiSelect > div > div {
    background: #ffffff !important;
    border: 1px solid #c0c8d8 !important;
    color: #111111 !important;
    border-radius: 6px !important;
}

/* radio · checkbox 텍스트 */
[role="dialog"] [data-testid="stRadio"] label,
[role="dialog"] [data-testid="stCheckbox"] label {
    color: #1a1a2e !important;
    font-weight: 500 !important;
}

/* primary 버튼 */
[role="dialog"] [data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #1A4FCC, #2563EB) !important;
    border: none !important;
    border-radius: 6px !important;
    color: #fff !important;
    font-weight: 700 !important;
}

/* secondary 버튼 */
[role="dialog"] [data-testid="stBaseButton-secondary"] {
    background: #f0f4ff !important;
    border: 1px solid #c0cce8 !important;
    border-radius: 6px !important;
    color: #1e3a8a !important;
    font-weight: 600 !important;
}

/* 에러 알림 */
[role="dialog"] [data-testid="stAlert"] * { color: #7f1d1d !important; }

/* 성공 알림 */
[role="dialog"] [data-testid="stNotification"] * { color: #14532d !important; }

/* ── 멀티셀렉트 드롭다운 팝업 (portal 렌더링 — 전역 적용) ── */
[data-baseweb="popover"],
[data-baseweb="popover"] * {
    background: #ffffff !important;
    color: #111111 !important;
}
[data-baseweb="menu"] li,
[data-baseweb="menu"] [role="option"],
[data-baseweb="option"] {
    color: #111111 !important;
    background: #ffffff !important;
    font-size: 0.93rem !important;
}
[data-baseweb="menu"] li:hover,
[data-baseweb="menu"] [role="option"]:hover,
[data-baseweb="option"]:hover {
    background: #eef2ff !important;
    color: #1e3a8a !important;
}
/* 선택된(체크) 항목 */
[data-baseweb="menu"] li[aria-selected="true"],
[data-baseweb="option"][aria-selected="true"] {
    background: #dbeafe !important;
    color: #1e40af !important;
}
/* "Select all" 텍스트 */
[data-baseweb="menu"] [data-testid="stMultiSelectDropdown"] span {
    color: #111111 !important;
}

/* ── expander ── */
.streamlit-expanderHeader {
    color: #BDD0FF !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
}

/* ── alert 박스 ── */
[data-testid="stAlert"] {
    background: rgba(74,144,255,0.1) !important;
    border: 1px solid var(--border-strong) !important;
    color: #C0D2F5 !important;
    border-radius: 4px !important;
    font-size: 0.95rem !important;
}

/* ── caption ── */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * {
    color: #B8C8EF !important;
    font-size: 0.875rem !important;
}

/* ── progress ── */
.stProgress > div > div { background: linear-gradient(90deg, #2563EB, #4A90FF) !important; }

/* ── radio / checkbox ── */
.stRadio label, .stCheckbox label { color: #C0D2F5 !important; font-size: 0.95rem !important; }

/* ── dataframe ── */
.stDataFrame { border: 1px solid var(--border-strong) !important; border-radius: 6px !important; }
.stDataFrame tbody tr:hover td { background: rgba(74,144,255,0.06) !important; }

/* ── Career page refinement ── */
.career-shell {
    max-width: 980px;
}
.career-muted {
    color: var(--text-3);
    font-size: 0.9rem;
    margin: 0.15rem 0 1rem;
}
.career-section-label {
    color: var(--text-1);
    font-size: 0.95rem;
    font-weight: 700;
    margin: 0.75rem 0 0.35rem;
}
.career-hint {
    color: var(--text-3);
    font-size: 0.86rem;
    margin: 0.1rem 0 0.65rem;
}
[data-testid="stForm"] {
    border-color: var(--border-strong) !important;
    background: rgba(18,22,32,0.42) !important;
}
[data-testid="stTabs"] {
    margin-top: 0.5rem;
}
[data-testid="stTabs"] button {
    color: var(--text-2) !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--text-1) !important;
}

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
    color: #7F91BF;
    letter-spacing: 0.3px;
}
.sidebar-brand {
    display: block;
    padding: 0.25rem 0.5rem 0.5rem 0.9rem;
    text-decoration: none !important;
    border-radius: 8px;
    transition: background 0.16s ease, transform 0.16s ease;
}
.sidebar-brand:hover {
    background: rgba(74,144,255,0.08);
    transform: translateY(-1px);
}
.sidebar-brand-title {
    font-size: 1rem;
    font-weight: 700;
    color: #C8DCFF;
    letter-spacing: 0.5px;
}
.sidebar-brand-subtitle {
    font-size: 0.62rem;
    color: #8FA8E8;
    margin-top: 3px;
    text-transform: uppercase;
    letter-spacing: 1.8px;
}

/* ══════════════════════════════════════
   반응형 — 태블릿 (≤ 768px)
══════════════════════════════════════ */
@media (max-width: 768px) {
    /* 본문 여백 축소 */
    .main .block-container {
        padding: 0.55rem 1.25rem 1.25rem !important;
    }

    /* 히어로 배너 */
    .hero {
        padding: 2rem 1.5rem !important;
        min-height: 320px !important;
    }
    .hero-title { font-size: 2rem !important; }
    .hero-sub   { font-size: 1rem !important; }
    .hero-stat-wrap { gap: 0.65rem !important; }
    .hero-stat {
        min-width: calc(50% - 0.65rem) !important;
        flex: 1 1 calc(50% - 0.65rem) !important;
    }
    .feature-cards {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }

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
    .cta-banner::after { display: none !important; }
}

/* ══════════════════════════════════════
   반응형 — 모바일 (≤ 480px)
══════════════════════════════════════ */
@media (max-width: 480px) {
    /* 본문 여백 더 축소 */
    .main .block-container {
        padding: 0.45rem 0.9rem 0.9rem !important;
    }

    /* 히어로 배너 */
    .hero {
        padding: 1.5rem 1.1rem !important;
        min-height: 300px !important;
    }
    .hero-title { font-size: 1.6rem !important; line-height: 1.2 !important; }
    .hero-sub   { font-size: 0.92rem !important; }
    .hero::after { display: none !important; }
    .hero-stat {
        min-width: 100% !important;
        flex-basis: 100% !important;
    }
    .feature-cards {
        grid-template-columns: 1fr !important;
    }

    /* 제목 */
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.1rem !important; }

    /* 사이드바 nav 버튼 — 터치 영역 확보 */
    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
    [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
        padding: 0.68rem 0.9rem !important;
        font-size: 1rem !important;
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
# 상수 — 3D 유니버스 구(sphere) 노드 목록
# ══════════════════════════════════════════
UNIVERSE_NODES = [
    '양자역학', 'AI', '데이터 분석', '글쓰기', '영상제작', '사진', '디자인',
    '과학커뮤니케이션', '대중강연', '저널리즘', '환경보호', '기후위기', '사회혁신',
    '교육', 'SF 독서', '등산', '요리', '음악', '로보틱스', '자율주행',
    '앱 개발', '웹 개발', '게임 개발', '사이버보안', '클라우드', '반도체',
    '우주항공', '바이오', '의료기술', '심리상담', '진로교육', '번역',
    '마케팅', '브랜딩', '창업', '서비스기획', 'UX 리서치', '제품디자인',
    '일러스트', '애니메이션', '공연기획', '음향', '스포츠', '공공정책',
    '국제협력', '도시계획', '건축', '농업기술', '식품개발', '동물복지',
    '재생에너지', 'ESG', '금융', '회계', '법률', '기타',
]

EXPERT_FIELDS = [
    '과학/기술', 'IT/AI/데이터', '공학/제조', '연구/개발', '예술/디자인',
    '미디어/콘텐츠', '교육/진로', '의료/바이오', '심리/상담', '환경/에너지',
    '사회/경영', '창업/스타트업', '금융/회계', '법률/공공정책', '국제/언어',
    '문화/공연', '스포츠/건강', '농업/식품', '건축/도시', '기타'
]
SCHOOL_LEVELS = ['초등학생', '중학생', '고등학생', '대학생', '성인']

MAJOR_LIST = [
    # 인문계열
    "국어국문학", "영어영문학", "불어불문학", "독어독문학", "중어중문학", "일어일문학",
    "철학", "사학", "고고학", "종교학",
    # 사회과학계열
    "심리학", "사회학", "정치외교학", "경제학", "경영학", "회계학", "무역학",
    "행정학", "법학", "언론정보학", "광고홍보학", "사회복지학", "교육학",
    # 자연과학계열
    "수학", "물리학", "화학", "생명과학", "생물학", "지구과학", "천문학", "통계학",
    # 공학계열
    "컴퓨터공학", "소프트웨어학", "전기전자공학", "기계공학", "화학공학",
    "건축학", "토목공학", "산업공학", "항공우주공학", "재료공학",
    # 의학/보건계열
    "의학", "치의학", "한의학", "간호학", "약학", "보건학", "의공학",
    # 예술계열
    "음악학", "미술학", "디자인학", "영상학", "연극영화학", "무용학",
    # 체육/농업/환경계열
    "체육학", "스포츠과학", "농학", "식품공학", "환경학", "산림학",
    # 기타
    "기타",
]


# ══════════════════════════════════════════
# DB 연결 및 스키마
# ══════════════════════════════════════════
if HERO_BG_URI:
    st.markdown(f"""
<style>
.hero {{
    background:
        linear-gradient(90deg, rgba(10, 14, 24, 0.96) 0%, rgba(10, 14, 24, 0.82) 48%, rgba(10, 14, 24, 0.46) 100%),
        url("{HERO_BG_URI}") center / cover no-repeat !important;
}}
.hero::before {{
    background:
        radial-gradient(circle at 76% 32%, rgba(39, 214, 162, 0.18) 0%, transparent 28%),
        radial-gradient(circle at 82% 78%, rgba(74, 144, 255, 0.20) 0%, transparent 34%),
        linear-gradient(90deg, rgba(10, 14, 24, 0.16), rgba(10, 14, 24, 0.02)) !important;
    background-size: auto !important;
}}
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "future_universe.db")
UNIVERSE_3D_COMPONENT_DIR = os.path.join(BASE_DIR, "components", "future_universe_3d")
os.makedirs(UNIVERSE_3D_COMPONENT_DIR, exist_ok=True)
future_universe_3d_component = components.declare_component(
    "future_universe_3d_component",
    path=UNIVERSE_3D_COMPONENT_DIR,
)
LEGACY_DB_PATHS = [
    os.path.join(BASE_DIR, "futureverse_survey.db"),
    os.path.abspath(os.path.join(BASE_DIR, "..", "futureverse_survey.db")),
]
SEED_DATA_DIR = os.path.join(BASE_DIR, "data", "seed")
LEGACY_SEED_DATA_DIR = os.path.join(BASE_DIR, "data", "mock")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def render_3d_universe_component(html_content, key):
    index_path = os.path.join(UNIVERSE_3D_COMPONENT_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return future_universe_3d_component(default=None, key=key)

def _hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def _login_id_for_ref(account_ref):
    if isinstance(account_ref, dict):
        return account_ref.get("login_id")
    conn = get_conn()
    if isinstance(account_ref, int):
        row = conn.execute("SELECT login_id FROM accounts WHERE id=?", (account_ref,)).fetchone()
    else:
        row = conn.execute("SELECT login_id FROM accounts WHERE login_id=?", (str(account_ref),)).fetchone()
    conn.close()
    return row[0] if row else None

def _account_id_for_login(login_id):
    conn = get_conn()
    row = conn.execute("SELECT id FROM accounts WHERE login_id=?", (login_id,)).fetchone()
    conn.close()
    return row[0] if row else None

def _add_col(c, table, col, typ):
    try:
        c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")
    except Exception:
        pass

def init_accounts():
    conn = get_conn()
    c = conn.cursor()

    # ── accounts: 공통 로그인 테이블 ──────────────────
    # role: 'admin' | 'expert' | 'student'
    c.execute("""CREATE TABLE IF NOT EXISTS accounts (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        login_id      TEXT    NOT NULL UNIQUE,
        password_hash TEXT    NOT NULL,
        role          TEXT    NOT NULL DEFAULT 'student',
        created_at    TEXT    NOT NULL DEFAULT (datetime('now')))""")
    _add_col(c, 'accounts', 'created_at', "TEXT DEFAULT (datetime('now'))")
    conn.commit()

    # ── student_profiles: 학생 프로필 ──────────────
    c.execute("""CREATE TABLE IF NOT EXISTS student_profiles (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        login_id     TEXT    NOT NULL UNIQUE REFERENCES accounts(login_id) ON DELETE CASCADE,
        display_name TEXT,
        school_level TEXT,
        school_name  TEXT,
        grade        TEXT,
        created_at   TEXT    NOT NULL DEFAULT (datetime('now')))""")
    conn.commit()

    # ── expert_profiles: 전문가 프로필 ────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS expert_profiles (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        login_id      TEXT    NOT NULL UNIQUE REFERENCES accounts(login_id) ON DELETE CASCADE,
        display_name  TEXT    NOT NULL,
        title         TEXT,   -- 직함 (예: 교수, 회사원, 프리랜서)
        organization  TEXT,   -- 소속 (예: KAIST)
        major         TEXT,   -- 전공/학과 (예: 물리학과)
        current_job   TEXT,   -- 현재 직업/역할
        field         TEXT,   -- 대분류 분야
        description   TEXT,   -- 소개
        contact_email TEXT,
        is_approved   INTEGER NOT NULL DEFAULT 0,  -- 0=대기 / 1=승인
        created_at    TEXT    NOT NULL DEFAULT (datetime('now')))""")
    _add_col(c, 'expert_profiles', 'major', 'TEXT')
    _add_col(c, 'expert_profiles', 'current_job', 'TEXT')
    conn.commit()

    # ── expert_nodes: 전문가 ↔ 구(node) 매핑 ──────────
    c.execute("""CREATE TABLE IF NOT EXISTS expert_nodes (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        expert_id  INTEGER NOT NULL REFERENCES expert_profiles(id) ON DELETE CASCADE,
        node_name  TEXT    NOT NULL,
        created_at TEXT    NOT NULL DEFAULT (datetime('now')),
        UNIQUE(expert_id, node_name))""")
    conn.commit()

    # ── my_universe: 학생 마이유니버스 저장 ──────
    c.execute("""CREATE TABLE IF NOT EXISTS my_universe (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        login_id    TEXT    NOT NULL REFERENCES accounts(login_id) ON DELETE CASCADE,
        node_name   TEXT    NOT NULL,
        selected_at TEXT    NOT NULL DEFAULT (datetime('now')),
        UNIQUE(login_id, node_name))""")
    conn.commit()

    # ── accounts: tokens 컬럼 ────────────────────────────
    _add_col(c, 'accounts', 'tokens', 'INTEGER NOT NULL DEFAULT 0')
    conn.commit()

    # ── token_transactions: 토큰 내역 ────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS token_transactions (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        login_id   TEXT    NOT NULL REFERENCES accounts(login_id) ON DELETE CASCADE,
        amount     INTEGER NOT NULL,   -- 양수=적립 / 음수=사용
        reason     TEXT    NOT NULL,   -- '가입 보너스', '질문 작성', '답변 등록' 등
        related_id INTEGER,            -- question_id 등 참조
        created_at TEXT    NOT NULL DEFAULT (datetime('now')))""")
    conn.commit()

    # ── questions: 전문가 질문 ────────────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS questions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        from_login_id   TEXT    NOT NULL REFERENCES accounts(login_id) ON DELETE CASCADE,
        to_expert_id  INTEGER NOT NULL REFERENCES expert_profiles(id) ON DELETE CASCADE,
        question_title TEXT,
        question_text TEXT    NOT NULL,
        is_public     INTEGER NOT NULL DEFAULT 1,  -- 1=공개 / 0=비공개
        created_at    TEXT    NOT NULL DEFAULT (datetime('now')))""")
    _add_col(c, 'questions', 'question_title', 'TEXT')
    c.execute("""
        UPDATE questions
        SET question_title = substr(question_text, 1, 40)
        WHERE question_title IS NULL OR question_title = ''
    """)

    # ── question_answers: 전문가 답변 ────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS question_answers (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id      INTEGER NOT NULL UNIQUE REFERENCES questions(id) ON DELETE CASCADE,
        answer_text      TEXT    NOT NULL,
        answered_by      TEXT    NOT NULL REFERENCES accounts(login_id),
        is_new_for_asker INTEGER NOT NULL DEFAULT 1,  -- 1=질문자 미확인
        created_at       TEXT    NOT NULL DEFAULT (datetime('now')))""")
    _add_col(c, 'question_answers', 'is_new_for_asker', 'INTEGER DEFAULT 1')
    conn.commit()

    # ── universe_nodes: 관리자 추가 노드 ────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS universe_nodes (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        node_name  TEXT    NOT NULL UNIQUE,
        created_at TEXT    NOT NULL DEFAULT (datetime('now')))""")
    conn.commit()

    # ── node_requests: 활동분야 추가 요청 ───────────────
    c.execute("""CREATE TABLE IF NOT EXISTS node_requests (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expert_id    INTEGER NOT NULL REFERENCES expert_profiles(id) ON DELETE CASCADE,
        node_name    TEXT    NOT NULL,
        status       TEXT    NOT NULL DEFAULT 'pending',
        requested_at TEXT    NOT NULL DEFAULT (datetime('now')),
        handled_at   TEXT)""")
    conn.commit()

    # admin 계정 초기 생성
    c.execute("SELECT COUNT(*) FROM accounts WHERE role='admin'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO accounts (login_id, password_hash, role) VALUES (?,?,?)",
                  ("admin", _hash_pw("admin1234"), "admin"))
        conn.commit()

    # ── career_videos: 진로 탐색 영상 관리 ───────────────
    c.execute("""CREATE TABLE IF NOT EXISTS career_videos (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        title      TEXT    NOT NULL,
        url        TEXT    NOT NULL UNIQUE,
        caption    TEXT,
        created_at TEXT    NOT NULL DEFAULT (datetime('now')))""")
    c.execute("SELECT COUNT(*) FROM career_videos")
    if c.fetchone()[0] == 0:
        for video in CAREER_VIDEOS:
            c.execute(
                "INSERT OR IGNORE INTO career_videos (title, url, caption) VALUES (?,?,?)",
                (video["title"], video["url"], video["caption"])
            )
        conn.commit()

    conn.close()


# ══════════════════════════════════════════
# 인증 함수
# ══════════════════════════════════════════
def do_login(login_id, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, login_id, role FROM accounts WHERE login_id=? AND password_hash=?",
              (login_id, _hash_pw(password)))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    role = row[2]
    if role == "expert":
        profile_row = conn.execute("SELECT display_name FROM expert_profiles WHERE login_id=?", (row[1],)).fetchone()
    elif role == "admin":
        profile_row = ("관리자",)
    else:
        profile_row = conn.execute("SELECT display_name FROM student_profiles WHERE login_id=?", (row[1],)).fetchone()
    conn.close()
    display_name = profile_row[0] if profile_row and profile_row[0] else row[1]
    return {"account_id": row[0], "login_id": row[1], "role": role, "display_name": display_name}

def do_register(login_id, password, role='student', profile=None):
    """
    profile dict 예시
      학생:       {display_name, school_level, school_name, grade}
      전문가:     {display_name, title, organization, field, description, contact_email, nodes:[...]}
    """
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO accounts (login_id, password_hash, role) VALUES (?,?,?)",
                  (login_id, _hash_pw(password), role))
        conn.commit()
        uid = c.lastrowid

        p = profile or {}
        # 역할별 초기 토큰 지급
        init_tokens = 5000 if role == 'expert' else 10000
        c.execute("UPDATE accounts SET tokens=? WHERE id=?", (init_tokens, uid))
        c.execute(
            "INSERT INTO token_transactions (login_id, amount, reason) VALUES (?,?,?)",
            (login_id, init_tokens, "가입 보너스")
        )

        if role == 'student':
            c.execute("""INSERT INTO student_profiles (login_id, display_name, school_level, school_name, grade)
                         VALUES (?,?,?,?,?)""",
                      (login_id, p.get('display_name',''), p.get('school_level',''),
                       p.get('school_name',''), p.get('grade','')))
        elif role == 'expert':
            c.execute("""INSERT INTO expert_profiles
                         (login_id, display_name, title, organization, major, current_job,
                          field, description, contact_email)
                         VALUES (?,?,?,?,?,?,?,?,?)""",
                      (login_id, p.get('display_name',''), p.get('title',''),
                       p.get('organization',''), p.get('major',''),
                       p.get('current_job',''), p.get('field',''),
                       p.get('description',''), p.get('contact_email','')))
            conn.commit()
            eid = c.lastrowid
            for node in p.get('nodes', []):
                c.execute("INSERT OR IGNORE INTO expert_nodes (expert_id, node_name) VALUES (?,?)", (eid, node))

        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


# ══════════════════════════════════════════
# 프로필 조회 함수
# ══════════════════════════════════════════
def get_student_profile(account_ref):
    login_id = _login_id_for_ref(account_ref)
    if not login_id:
        return {}
    conn = get_conn()
    row = conn.execute("SELECT * FROM student_profiles WHERE login_id=?", (login_id,)).fetchone()
    conn.close()
    if not row:
        return {}
    cols = ['id','login_id','display_name','school_level','school_name','grade','created_at']
    return dict(zip(cols, row))

def get_expert_profile(account_ref):
    login_id = _login_id_for_ref(account_ref)
    if not login_id:
        return {}
    conn = get_conn()
    cols = ['id','login_id','display_name','title','organization','major','current_job',
            'field','description','contact_email','is_approved','created_at']
    row = conn.execute(f"""
        SELECT {', '.join(cols)}
        FROM expert_profiles
        WHERE login_id=?
    """, (login_id,)).fetchone()
    conn.close()
    if not row:
        return {}
    return dict(zip(cols, row))

def get_account_display_name(account_ref, fallback=""):
    login_id = _login_id_for_ref(account_ref)
    if not login_id:
        return fallback
    conn = get_conn()
    row = conn.execute("""
        SELECT COALESCE(NULLIF(sp.display_name, ''), NULLIF(ep.display_name, ''), a.login_id) AS display_name
        FROM accounts a
        LEFT JOIN student_profiles sp ON sp.login_id = a.login_id
        LEFT JOIN expert_profiles ep ON ep.login_id = a.login_id
        WHERE a.login_id = ?
    """, (login_id,)).fetchone()
    conn.close()
    return row[0] if row and row[0] else fallback

def get_expert_nodes(expert_id):
    conn = get_conn()
    rows = conn.execute("SELECT node_name FROM expert_nodes WHERE expert_id=?", (expert_id,)).fetchall()
    conn.close()
    return [r[0] for r in rows]

def search_experts(keyword=""):
    """승인된 전문가 목록 반환 (검색어 있으면 이름 필터)"""
    conn = get_conn()
    if keyword:
        rows = conn.execute("""
            SELECT ep.id, ep.display_name, ep.title, ep.organization, ep.field, ep.login_id
            FROM expert_profiles ep
            WHERE ep.is_approved=1 AND ep.display_name LIKE ?
        """, (f"%{keyword}%",)).fetchall()
    else:
        rows = conn.execute("""
            SELECT ep.id, ep.display_name, ep.title, ep.organization, ep.field, ep.login_id
            FROM expert_profiles ep
            WHERE ep.is_approved=1
        """).fetchall()
    conn.close()
    cols = ['id','display_name','title','organization','field','login_id']
    return [dict(zip(cols, r)) for r in rows]

def recommend_experts_for_question(question="", my_nodes=None, limit=3):
    """질문 문장과 관심 노드에 맞는 승인 전문가 추천."""
    q = (question or "").lower()
    selected_nodes = set(my_nodes or [])
    conn = get_conn()
    rows = conn.execute("""
        SELECT ep.id, ep.login_id, ep.display_name, ep.title, ep.organization,
               ep.current_job, ep.major, ep.field, ep.description,
               GROUP_CONCAT(en.node_name, ',') AS nodes
        FROM expert_profiles ep
        LEFT JOIN expert_nodes en ON en.expert_id = ep.id
        WHERE ep.is_approved = 1
        GROUP BY ep.id
    """).fetchall()
    conn.close()

    experts = []
    for r in rows:
        d = {
            "id": r[0],
            "login_id": r[1],
            "display_name": r[2],
            "title": r[3],
            "organization": r[4],
            "current_job": r[5],
            "major": r[6],
            "field": r[7],
            "description": r[8],
            "nodes": [n for n in (r[9] or "").split(",") if n],
        }
        score = 0
        reason_parts = []

        for node in d["nodes"]:
            if node in selected_nodes:
                score += 5
                reason_parts.append(f"관심 노드 {node}")
            if node and node.lower() in q:
                score += 6
                reason_parts.append(f"질문 키워드 {node}")

        for key, weight in [("current_job", 4), ("major", 3), ("field", 3), ("description", 1)]:
            value = (d.get(key) or "").strip()
            if value and value.lower() in q:
                score += weight
                if key != "description":
                    reason_parts.append(value)

        if not score and selected_nodes:
            overlap = selected_nodes.intersection(d["nodes"])
            if overlap:
                score += 2

        d["score"] = score
        d["reason"] = " · ".join(dict.fromkeys(reason_parts[:3])) or "전문가 DB 기반 추천"
        experts.append(d)

    experts.sort(key=lambda x: (x["score"], len(set(x["nodes"]).intersection(selected_nodes))), reverse=True)
    return experts[:limit]

def post_question(from_login_id, to_expert_id, title, text, is_public):
    """질문 등록 + 1,000 토큰 차감. 잔액 부족 시 False 반환."""
    if get_token_balance(from_login_id) < 1000:
        return False
    conn = get_conn()
    c = conn.cursor()
    if not _account_id_for_login(from_login_id):
        conn.close()
        return False
    c.execute("""INSERT INTO questions
                 (from_login_id, to_expert_id, question_title, question_text, is_public)
                 VALUES (?,?,?,?,?)""",
              (from_login_id, to_expert_id, title, text, 1 if is_public else 0))
    qid = c.lastrowid
    c.execute("UPDATE accounts SET tokens = tokens - 1000 WHERE login_id=?", (from_login_id,))
    c.execute("""INSERT INTO token_transactions (login_id, amount, reason, related_id)
                 VALUES (?,?,?,?)""",
              (from_login_id, -1000, "질문 작성", qid))
    conn.commit()
    conn.close()
    return True

def get_questions_for_expert(expert_id, viewer_login_id=None, viewer_role=None):
    """전문가가 받은 질문 목록. 비공개는 admin·질문자·해당전문가만 조회 가능."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT q.id, q.from_login_id,
               COALESCE(NULLIF(sp.display_name, ''), NULLIF(ep_asker.display_name, ''), q.from_login_id) AS asker_nickname,
               q.question_text,
               q.is_public, q.created_at,
               qa.answer_text, qa.created_at as answered_at
        FROM questions q
        LEFT JOIN student_profiles sp ON sp.login_id = q.from_login_id
        LEFT JOIN expert_profiles ep_asker ON ep_asker.login_id = q.from_login_id
        LEFT JOIN question_answers qa ON qa.question_id = q.id
        WHERE q.to_expert_id = ?
        ORDER BY q.created_at DESC
    """, (expert_id,)).fetchall()
    conn.close()
    cols = ['id','from_login_id','asker_nickname','question_text',
            'is_public','created_at','answer_text','answered_at']
    result = []
    for r in rows:
        d = dict(zip(cols, r))
        if not d['is_public']:
            if viewer_role == 'admin':
                pass
            elif viewer_login_id and (viewer_login_id == d['from_login_id']):
                pass
            else:
                continue
        result.append(d)
    return result

def get_public_questions(to_expert_id=None):
    """공개 질문 전체 목록"""
    conn = get_conn()
    if to_expert_id:
        rows = conn.execute("""
            SELECT q.id, ep.display_name as expert_name,
                   COALESCE(NULLIF(sp.display_name, ''), NULLIF(ep_asker.display_name, ''), q.from_login_id) AS asker_nickname,
                   q.question_text, q.created_at,
                   qa.answer_text, qa.created_at as answered_at
            FROM questions q
            JOIN expert_profiles ep ON ep.id = q.to_expert_id
            LEFT JOIN student_profiles sp ON sp.login_id = q.from_login_id
            LEFT JOIN expert_profiles ep_asker ON ep_asker.login_id = q.from_login_id
            LEFT JOIN question_answers qa ON qa.question_id = q.id
            WHERE q.is_public=1 AND q.to_expert_id=?
            ORDER BY q.created_at DESC
        """, (to_expert_id,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT q.id, ep.display_name as expert_name,
                   COALESCE(NULLIF(sp.display_name, ''), NULLIF(ep_asker.display_name, ''), q.from_login_id) AS asker_nickname,
                   q.question_text, q.created_at,
                   qa.answer_text, qa.created_at as answered_at
            FROM questions q
            JOIN expert_profiles ep ON ep.id = q.to_expert_id
            LEFT JOIN student_profiles sp ON sp.login_id = q.from_login_id
            LEFT JOIN expert_profiles ep_asker ON ep_asker.login_id = q.from_login_id
            LEFT JOIN question_answers qa ON qa.question_id = q.id
            WHERE q.is_public=1
            ORDER BY q.created_at DESC
        """).fetchall()
    conn.close()
    cols = ['id','expert_name','asker_nickname','question_text',
            'created_at','answer_text','answered_at']
    return [dict(zip(cols, r)) for r in rows]

def get_token_balance(account_ref):
    login_id = _login_id_for_ref(account_ref)
    if not login_id:
        return 0
    conn = get_conn()
    row = conn.execute("SELECT tokens FROM accounts WHERE login_id=?", (login_id,)).fetchone()
    conn.close()
    return row[0] if row else 0

def add_tokens(account_ref, amount, reason, related_id=None):
    """토큰 증감 + 내역 기록. amount 음수면 차감."""
    login_id = _login_id_for_ref(account_ref)
    if not login_id:
        return
    conn = get_conn()
    conn.execute("UPDATE accounts SET tokens = tokens + ? WHERE login_id=?", (amount, login_id))
    conn.execute(
        "INSERT INTO token_transactions (login_id, amount, reason, related_id) VALUES (?,?,?,?)",
        (login_id, amount, reason, related_id)
    )
    conn.commit()
    conn.close()

def get_token_history(account_ref, limit=30):
    login_id = _login_id_for_ref(account_ref)
    if not login_id:
        return []
    conn = get_conn()
    rows = conn.execute("""
        SELECT amount, reason, created_at
        FROM token_transactions
        WHERE login_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (login_id, limit)).fetchall()
    conn.close()
    return rows

def get_new_answer_count(account_ref):
    """학생의 미확인 새 답변 수"""
    login_id = _login_id_for_ref(account_ref)
    if not login_id:
        return 0
    conn = get_conn()
    row = conn.execute("""
        SELECT COUNT(*) FROM question_answers qa
        JOIN questions q ON q.id = qa.question_id
        WHERE q.from_login_id = ? AND qa.is_new_for_asker = 1
    """, (login_id,)).fetchone()
    conn.close()
    return row[0] if row else 0

def mark_answers_read(login_id):
    """프로필 조회 시 해당 계정의 새 답변을 읽음 처리"""
    conn = get_conn()
    conn.execute("""
        UPDATE question_answers SET is_new_for_asker = 0
        WHERE question_id IN (
            SELECT id FROM questions WHERE from_login_id = ?
        )
    """, (login_id,))
    conn.commit()
    conn.close()

def get_unanswered_count(expert_profile_id):
    """전문가의 미답변 질문 수"""
    conn = get_conn()
    row = conn.execute("""
        SELECT COUNT(*) FROM questions q
        LEFT JOIN question_answers qa ON qa.question_id = q.id
        WHERE q.to_expert_id = ? AND qa.id IS NULL
    """, (expert_profile_id,)).fetchone()
    conn.close()
    return row[0] if row else 0

def post_answer(question_id, answer_text, answered_by):
    """답변 등록 + 전문가에게 1,000 토큰 적립."""
    answered_by_login_id = _login_id_for_ref(answered_by)
    if not answered_by_login_id:
        return
    conn = get_conn()
    c = conn.cursor()
    existing_answer = c.execute(
        "SELECT id FROM question_answers WHERE question_id=?",
        (question_id,),
    ).fetchone()
    c.execute("""INSERT OR REPLACE INTO question_answers
                 (question_id, answer_text, answered_by, is_new_for_asker)
                 VALUES (?,?,?,1)""",
              (question_id, answer_text, answered_by_login_id))
    if existing_answer is None:
        c.execute("UPDATE accounts SET tokens = tokens + 1000 WHERE login_id=?", (answered_by_login_id,))
        c.execute(
            "INSERT INTO token_transactions (login_id, amount, reason, related_id) VALUES (?,?,?,?)",
            (answered_by_login_id, 1000, "답변 등록", question_id)
        )
    conn.commit()
    conn.close()

def update_display_name(account_ref, role, new_name):
    login_id = _login_id_for_ref(account_ref)
    if not login_id:
        return
    conn = get_conn()
    if role == "expert":
        conn.execute("UPDATE expert_profiles SET display_name=? WHERE login_id=?", (new_name, login_id))
    else:
        conn.execute("UPDATE student_profiles SET display_name=? WHERE login_id=?", (new_name, login_id))
    conn.commit()
    conn.close()


def get_all_universe_nodes():
    conn = get_conn()
    rows = conn.execute("SELECT node_name FROM universe_nodes").fetchall()
    conn.close()
    custom = [r[0] for r in rows]
    return list(dict.fromkeys(UNIVERSE_NODES + custom))

def add_universe_node(node_name):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO universe_nodes (node_name) VALUES (?)", (node_name,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False

def delete_universe_node(node_name):
    conn = get_conn()
    conn.execute("DELETE FROM universe_nodes WHERE node_name=?", (node_name,))
    conn.commit()
    conn.close()


def request_node(expert_id, node_name):
    conn = get_conn()
    existing = conn.execute(
        "SELECT id FROM node_requests WHERE expert_id=? AND node_name=? AND status='pending'",
        (expert_id, node_name)
    ).fetchone()
    if existing:
        conn.close()
        return False
    conn.execute("INSERT INTO node_requests (expert_id, node_name) VALUES (?,?)", (expert_id, node_name))
    conn.commit()
    conn.close()
    return True

def get_node_requests(status=None):
    conn = get_conn()
    q = """
        SELECT nr.id, nr.node_name, nr.status, nr.requested_at,
               ep.display_name AS expert_name, ep.id AS expert_profile_id
        FROM node_requests nr
        JOIN expert_profiles ep ON ep.id = nr.expert_id
        {}
        ORDER BY nr.requested_at DESC
    """
    if status:
        rows = conn.execute(q.format("WHERE nr.status=?"), (status,)).fetchall()
    else:
        rows = conn.execute(q.format("")).fetchall()
    conn.close()
    cols = ['id', 'node_name', 'status', 'requested_at', 'expert_name', 'expert_profile_id']
    return [dict(zip(cols, r)) for r in rows]

def handle_node_request(request_id, approve):
    conn = get_conn()
    c = conn.cursor()
    row = c.execute("SELECT expert_id, node_name FROM node_requests WHERE id=?", (request_id,)).fetchone()
    if not row:
        conn.close()
        return
    expert_id, node_name = row
    status = 'approved' if approve else 'rejected'
    c.execute("UPDATE node_requests SET status=?, handled_at=datetime('now') WHERE id=?", (status, request_id))
    if approve:
        c.execute("INSERT OR IGNORE INTO expert_nodes (expert_id, node_name) VALUES (?,?)", (expert_id, node_name))
    conn.commit()
    conn.close()


def update_expert_nodes(expert_id, node_names):
    """활동 분야 수정 후 is_approved=0 으로 재승인 대기 처리"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM expert_nodes WHERE expert_id=?", (expert_id,))
    for name in node_names:
        c.execute("INSERT OR IGNORE INTO expert_nodes (expert_id, node_name) VALUES (?,?)",
                  (expert_id, name))
    c.execute("UPDATE expert_profiles SET is_approved=0 WHERE id=?", (expert_id,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════
# 마이유니버스 저장/불러오기
# ══════════════════════════════════════════
def _account_refs(account_ref):
    if isinstance(account_ref, dict):
        return account_ref.get("account_id"), account_ref.get("login_id")
    conn = get_conn()
    if isinstance(account_ref, int):
        row = conn.execute("SELECT id, login_id FROM accounts WHERE id=?", (account_ref,)).fetchone()
    else:
        row = conn.execute("SELECT id, login_id FROM accounts WHERE login_id=?", (str(account_ref),)).fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return account_ref if isinstance(account_ref, int) else None, account_ref if isinstance(account_ref, str) else None


def sync_student_univers_seed(login_id, node_names):
    if not login_id:
        return
    os.makedirs(SEED_DATA_DIR, exist_ok=True)
    path = os.path.join(SEED_DATA_DIR, "student_univers.csv")
    columns = ["login_id", "node_name"]
    if os.path.exists(path):
        df = pd.read_csv(path, dtype=str).fillna("")
        df.columns = [str(col).strip() for col in df.columns]
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        df = df[columns]
    else:
        df = pd.DataFrame(columns=columns)

    df = df[df["login_id"] != login_id]
    unique_nodes = list(dict.fromkeys(str(name).strip() for name in node_names if str(name).strip()))
    if unique_nodes:
        df = pd.concat(
            [df, pd.DataFrame({"login_id": login_id, "node_name": unique_nodes})],
            ignore_index=True,
        )
    df.to_csv(path, index=False, encoding="utf-8-sig")


def save_my_universe(account_ref, node_names):
    account_id, login_id = _account_refs(account_ref)
    conn = get_conn()
    c = conn.cursor()
    cols = {row[1] for row in c.execute("PRAGMA table_info(my_universe)").fetchall()}
    where_parts = []
    where_values = []
    if "login_id" in cols and login_id:
        where_parts.append("login_id=?")
        where_values.append(login_id)
    if where_parts:
        c.execute(f"DELETE FROM my_universe WHERE {' OR '.join(where_parts)}", where_values)
    for name in node_names:
        data = {"node_name": name}
        if "login_id" in cols and login_id:
            data["login_id"] = login_id
        insert_cols = list(data.keys())
        placeholders = ",".join("?" for _ in insert_cols)
        c.execute(
            f"INSERT OR IGNORE INTO my_universe ({','.join(insert_cols)}) VALUES ({placeholders})",
            [data[col] for col in insert_cols],
        )
    conn.commit()
    conn.close()
    sync_student_univers_seed(login_id, node_names)

def load_my_universe(account_ref):
    account_id, login_id = _account_refs(account_ref)
    conn = get_conn()
    cols = {row[1] for row in conn.execute("PRAGMA table_info(my_universe)").fetchall()}
    where_parts = []
    where_values = []
    if "login_id" in cols and login_id:
        where_parts.append("login_id=?")
        where_values.append(login_id)
    if where_parts:
        rows = conn.execute(
            f"SELECT DISTINCT node_name FROM my_universe WHERE {' OR '.join(where_parts)} ORDER BY selected_at, id",
            where_values,
        ).fetchall()
    else:
        rows = []
    conn.close()
    return [r[0] for r in rows]


# ══════════════════════════════════════════
# 로그인 / 회원가입 다이얼로그
# ══════════════════════════════════════════
@st.dialog("로그인 / 회원가입")
def login_dialog():
    tab_login, tab_reg = st.tabs(["로그인", "회원가입"])

    def render_register_guide(role):
        if role == "전문가":
            st.markdown(
                """
                <div style="border:1px solid rgba(170,205,255,0.68);background:rgba(74,144,255,0.10);border-radius:8px;padding:14px 16px;margin:2px 0 14px 0;">
                    <div style="color:#E2EAFF;font-weight:800;font-size:0.98rem;margin-bottom:8px;">전문가 가입 안내</div>
                    <div style="color:#C4D4F6;font-size:0.86rem;line-height:1.7;">
                        가입 직후에는 관리자 승인 대기 상태입니다.<br>
                        활동 분야는 가입 후 이메일로 인증서류를 요청합니다.<br>
                        승인 후 기본 5,000 토큰이 지급되고, 답변을 등록할 때마다 1,000 토큰이 적립됩니다.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="border:1px solid rgba(170,205,255,0.68);background:rgba(74,144,255,0.10);border-radius:8px;padding:14px 16px;margin:2px 0 14px 0;">
                    <div style="color:#E2EAFF;font-weight:800;font-size:0.98rem;margin-bottom:8px;">학생 가입 안내</div>
                    <div style="color:#C4D4F6;font-size:0.86rem;line-height:1.7;">
                        가입 즉시 10,000 토큰이 지급됩니다.<br>
                        토큰은 전문가에게 질문을 등록하거나 진로 탐색 활동에 사용할 수 있습니다.<br>
                        3D 유니버스에서 관심 노드를 저장하면 내 프로필의 나만의 우주에도 반영됩니다.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── 로그인 탭 ────────────────────────────────────
    with tab_login:
        with st.form("dlg_login"):
            u = st.text_input("아이디")
            p = st.text_input("비밀번호", type="password")
            if st.form_submit_button("로그인", use_container_width=True, type="primary"):
                account = do_login(u.strip(), p)
                if account:
                    st.session_state.account = account
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

    # ── 회원가입 탭 ──────────────────────────────────
    with tab_reg:
        role = st.radio("회원 유형 선택", ["학생", "전문가"],
                        horizontal=True, key="reg_role_radio")
        st.divider()

        # 폼 키를 role에 따라 분리해 role 변경 시 폼 초기화
        render_register_guide(role)
        with st.form(f"dlg_register_{role}"):
            nu          = st.text_input(
                "아이디 (2자 이상)",
                help="영어, 숫자, 특수문자 모두 사용 가능합니다. 2자 이상 입력해주세요."
            )
            np_         = st.text_input("비밀번호 (4자 이상)", type="password")
            cp          = st.text_input("비밀번호 확인",       type="password")
            display_name = st.text_input(
                "닉네임 *",
                placeholder="책쓰는태권도사범" if role == "전문가" else "",
                help="필수 입력입니다. 한글과 숫자만, 띄어쓰기 없이 최대 10자까지 입력하세요."
            )
            if role == "전문가":
                st.caption("닉네임은 웹 안에서 표시되는 이름입니다. 학생들이 어떤 전문가인지 쉽게 떠올릴 수 있게 작성해 주세요.")
            else:
                st.caption("한글과 숫자만, 띄어쓰기 없이 최대 10자까지 입력 가능합니다.")

            profile = {'display_name': display_name.strip()}

            if role == "학생":
                school_level = st.selectbox("학교급", SCHOOL_LEVELS)
                school_name  = st.text_input("학교명", placeholder="○○중학교 (선택)")
                grade        = st.selectbox("학년", ["1학년","2학년","3학년","4학년","해당없음"])
                profile.update({'school_level': school_level,
                                'school_name':  school_name.strip(),
                                'grade':        grade})
            else:  # 전문가
                title = st.selectbox(
                    "직함 *",
                    ["교수", "강사", "연구원", "회사원", "프리랜서", "크리에이터",
                     "작가", "예술가", "의료인", "공무원", "창업가", "기타"],
                    help="현재 주된 직업 유형을 선택하세요."
                )
                current_job = st.text_input(
                    "현재 직업 *",
                    placeholder="예: 양자물리학 교수, AI 연구원, 환경 다큐 감독"
                )
                organization = st.text_input("소속", placeholder="예: KAIST, EBS, (주)○○")

                # 주전공 드롭다운 + 기타 직접입력
                major_select = st.selectbox("주전공(학과) *", MAJOR_LIST)
                major_other  = st.text_input(
                    "전공 직접 입력",
                    placeholder="기타 선택 시 필수 입력입니다. 예: 융합콘텐츠학, 데이터저널리즘"
                )
                major = major_other.strip() if major_select == "기타" else major_select

                field_select = st.selectbox("대분류 분야 *", EXPERT_FIELDS)
                field_other = st.text_input(
                    "대분류 분야 직접 입력",
                    placeholder="기타 선택 시 필수 입력입니다. 예: 문화기술, 국제개발"
                )
                field = field_other.strip() if field_select == "기타" else field_select
                description = st.text_area(
                    "소개 *",
                    placeholder="활동 및 전문 영역을 간단히 소개해 주세요."
                )
                contact_email = st.text_input(
                    "연락처 또는 이메일 *",
                    placeholder="예: 010-0000-0000 또는 example@email.com"
                )
                st.markdown("**활동 분야 선택 ***")
                st.caption("직업명이 아닌 관심사·전문 주제를 선택하세요. 예: 교수라면 '양자역학', '대중강연' 등")
                selected_nodes = st.multiselect(
                    "활동 분야",
                    get_all_universe_nodes(),
                    help="직업명이 아닌 관심사·전문 주제를 선택하세요."
                )
                nodes = selected_nodes
                profile.update({'title':         title,
                                'current_job':   current_job.strip(),
                                'organization':  organization.strip(),
                                'major':         major,
                                'field':         field,
                                'description':   description.strip(),
                                'contact_email': contact_email.strip(),
                                'nodes':         nodes})

            submitted = st.form_submit_button("회원가입", use_container_width=True, type="primary")

        if submitted:
            err = None
            if len(nu.strip()) < 2:
                err = "아이디는 2자 이상이어야 합니다."
            elif len(np_) < 4:
                err = "비밀번호는 4자 이상이어야 합니다."
            elif np_ != cp:
                err = "비밀번호가 일치하지 않습니다."
            elif not display_name.strip():
                err = "닉네임을 입력해 주세요."
            elif not _is_valid_nickname(display_name.strip()):
                err = "닉네임은 한글과 숫자만, 띄어쓰기 없이 최대 10자입니다."
            elif role == "전문가" and not profile.get('current_job'):
                err = "현재 직업을 입력해 주세요."
            elif role == "전문가" and major_select == "기타" and not major_other.strip():
                err = "기타를 선택한 경우 전공을 직접 입력해 주세요."
            elif role == "전문가" and field_select == "기타" and not field_other.strip():
                err = "기타를 선택한 경우 대분류 분야를 직접 입력해 주세요."
            elif role == "전문가" and not profile.get('description'):
                err = "소개를 입력해 주세요."
            elif role == "전문가" and not profile.get('contact_email'):
                err = "연락처 또는 이메일을 입력해 주세요."
            elif role == "전문가" and not profile.get('nodes'):
                err = "활동 분야를 최소 1개 이상 선택해 주세요."

            if err:
                st.error(err)
            elif not re.fullmatch(r"[가-힣0-9]{1,10}", display_name.strip()):
                st.error("닉네임은 한글과 숫자만 가능하며 최대 10자입니다.")
            elif do_register(nu.strip(), np_,
                             role='student' if role == "학생" else 'expert',
                             profile=profile):
                if role == "전문가":
                    st.toast("전문가 승인 요청이 완료되었습니다.")
                    st.success("회원가입이 완료되었습니다. 관리자 승인 후 전문가 기능이 활성화됩니다.")
                    st.info(
                        "전문가로 승인되기 위해 필요한 추가 서류를 제공해주신 이메일로 발송드리겠습니다. "
                        "(서류 발송 기능은 추후 구현 예정입니다.)"
                    )
                    st.info(
                        "전문가 승인 후에는 기본 5,000 토큰이 지급되고, 질문에 답변을 남길수록 토큰이 쌓이는 보상 구조입니다. "
                        "답변 활동이 많아질수록 더 많은 토큰을 받을 수 있습니다."
                    )
                else:
                    st.toast("가입을 환영합니다! 토큰이 지급되었습니다.")
                    st.success("회원가입 완료! 로그인 탭에서 로그인하세요.")
                    st.info(
                        "가입 보너스 10,000 토큰이 지급되었습니다. 이 토큰으로 전문가에게 질문을 등록하거나, "
                        "커리어 Q&A와 추천 콘텐츠를 이용할 수 있습니다."
                    )
            else:
                st.error("이미 사용 중인 아이디입니다.")


# ══════════════════════════════════════════
# 커리어 탐색 공통 필터 UI
# ══════════════════════════════════════════
def show_career_filters(df):
    """전공/활동분야 필터 + 맞춤 추천. 빈 DataFrame이면 안내 메시지 반환."""
    if df.empty:
        st.info("아직 등록된 전문가 데이터가 없습니다. 전문가가 가입하고 승인되면 여기에 표시됩니다.")
        return df

    with st.expander("필터 & 맞춤 추천", expanded=True):
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            major_options = ["전체"] + sorted(df['전공'].dropna().unique().tolist())
            sel_major = st.multiselect("전공 필터", major_options, default=["전체"])
        with r1c2:
            field_options = ["전체"] + sorted(df['활동 분야'].dropna().unique().tolist())
            sel_project = st.multiselect("활동 분야 필터", field_options, default=["전체"])

        job_options = ["선택 안 함"] + sorted(df['현재 직업'].dropna().unique().tolist())
        stu_interest = st.selectbox("희망 직업 분야", job_options)

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
                for m, cnt in majors.items():
                    st.write(f"- {m} ({cnt}명)")

    n = min(200, len(filtered))
    df_sample = filtered.sample(n).reset_index(drop=True) if n > 0 else filtered
    st.caption(f"표시 중인 전문가: **{len(df_sample)}명** / 전체 {len(df)}명")
    return df_sample


# ══════════════════════════════════════════
# 사이드바 네비게이션 (계층형)
# ══════════════════════════════════════════
SECTIONS = {
    "퓨처유니버스": [
        ("🏠 홈", "home"),
        ("🌌 3D 유니버스",   "3d"),
        ("💬 전문가 Q&A",    "questions"),
        ("🤖 AI 진로상담", "career"),
        ("🎬 진로 탐색 영상", "career_videos"),
        ("📋 설문조사 참여", "survey"),
        ("✉️ Contact Us", "contact"),
    ],
}

CAREER_VIDEOS = [
    {
        "title": "미래 직업 탐색",
        "url": "https://www.youtube.com/watch?v=-xkBMxdPaME",
        "caption": "미래 직업을 넓게 조망해보세요.",
    },
    {
        "title": "직업의 세계",
        "url": "https://www.youtube.com/watch?v=SyElvkVe_-g",
        "caption": "다양한 직업의 세계를 영상으로 만나보세요.",
    },
]

CONTACT_PROFILE = {
    "name": "dorotea",
    "role": "Future Universe 기획자 · 운영자",
    "message": "학생들이 관심사, 전문가, 질문을 연결해 자기만의 진로 지도를 만들 수 있도록 이 플랫폼을 만들고 있습니다.",
    "email": "futureuniverse@example.com",
}

def nav_btn(label, key, badge=None):
    t = "primary" if st.session_state.page == key else "secondary"
    button_label = f"{label}  · {badge}" if badge else label
    if st.sidebar.button(button_label, key=f"nav_{key}", use_container_width=True, type=t):
        st.session_state.page = key
        st.rerun()

def ensure_career_videos_table():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS career_videos (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        title      TEXT    NOT NULL,
        url        TEXT    NOT NULL UNIQUE,
        caption    TEXT,
        created_at TEXT    NOT NULL DEFAULT (datetime('now')))""")
    c.execute("SELECT COUNT(*) FROM career_videos")
    if c.fetchone()[0] == 0:
        for video in CAREER_VIDEOS:
            c.execute(
                "INSERT OR IGNORE INTO career_videos (title, url, caption) VALUES (?,?,?)",
                (video["title"], video["url"], video["caption"])
            )
    conn.commit()
    conn.close()

def load_career_videos():
    ensure_career_videos_table()
    conn = get_conn()
    rows = conn.execute("""
        SELECT id, title, url, caption, created_at
        FROM career_videos
        ORDER BY created_at DESC, id DESC
    """).fetchall()
    conn.close()
    return [
        {"id": r[0], "title": r[1], "url": r[2], "caption": r[3] or "", "created_at": r[4]}
        for r in rows
    ]

def add_career_video(title, url, caption):
    ensure_career_videos_table()
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO career_videos (title, url, caption) VALUES (?,?,?)",
            (title, url, caption)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_career_video(video_id):
    ensure_career_videos_table()
    conn = get_conn()
    conn.execute("DELETE FROM career_videos WHERE id=?", (video_id,))
    conn.commit()
    conn.close()

@st.dialog("진로 탐색 영상 추가")
def career_video_dialog():
    with st.form("career_video_add_form"):
        title = st.text_input("영상 제목", placeholder="예: 미래 직업 탐색")
        url = st.text_input("YouTube 영상 URL", placeholder="https://www.youtube.com/watch?v=...")
        caption = st.text_area("설명", placeholder="영상 설명을 짧게 입력하세요.")
        submitted = st.form_submit_button("영상 추가", type="primary", use_container_width=True)

    if submitted:
        clean_title = title.strip()
        clean_url = url.strip()
        clean_caption = caption.strip()
        if not clean_title:
            st.error("영상 제목을 입력해 주세요.")
        elif not clean_url.startswith(("https://www.youtube.com/", "https://youtu.be/")):
            st.error("YouTube 영상 URL을 입력해 주세요.")
        elif add_career_video(clean_title, clean_url, clean_caption):
            st.success("영상이 추가되었습니다.")
            st.rerun()
        else:
            st.error("이미 등록된 영상 URL입니다.")

@st.dialog("질문 등록 결과")
def question_submit_dialog(message):
    st.success(message)
    st.caption("내 질문 탭으로 이동했습니다. 답변 상태를 이곳에서 확인할 수 있습니다.")
    if st.button("확인", type="primary", use_container_width=True):
        st.rerun()

@st.dialog("나만의 우주 저장 완료")
def universe_save_dialog(count):
    st.success(f"✅ {count}개 노드가 저장되었습니다!")
    st.caption("3D 탐색기에서 선택한 노드들이 저장되었습니다.\n프로필의 '나만의 우주' 섹션에서 확인할 수 있습니다.")
    if st.button("확인", type="primary", use_container_width=True, key="universe_save_confirm"):
        st.rerun()

def render_career_videos(show_admin_controls=False):
    videos = load_career_videos()
    if not videos:
        st.info("아직 등록된 진로 탐색 영상이 없습니다.")
        return

    cols = st.columns(2, gap="large")
    for idx, video in enumerate(videos):
        with cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"**{video['title']}**")
                st.video(video["url"])
                st.caption(video["caption"])
                if show_admin_controls:
                    if st.button("삭제", key=f"delete_career_video_{video['id']}", use_container_width=True):
                        delete_career_video(video["id"])
                        st.success("영상이 삭제되었습니다.")
                        st.rerun()

def render_qa_toggle_board(df, key_prefix, mine=False):
    header_cols = st.columns([1.1, 4, 1.4, 1.4, 1.2, 1.2])
    headers = ["상태", "제목", "질문자" if not mine else "공개", "전문가", "질문일자", "답변일자"]
    for col, header in zip(header_cols, headers):
        col.markdown(f"**{header}**")

    open_key = f"{key_prefix}_open_id"
    if open_key not in st.session_state:
        st.session_state[open_key] = None

    for _, row in df.iterrows():
        qid = int(row["id"])
        title = row["question_title"] if pd.notna(row["question_title"]) and row["question_title"] else str(row["question_text"])[:40]
        status = "답변 완료" if pd.notna(row["answer_text"]) else ("답변 대기" if mine else "미답변")
        asked_at = str(row["created_at"])[:10]
        answered_at = "" if pd.isna(row["answered_at"]) else str(row["answered_at"])[:10]
        third = ("공개" if row.get("is_public", 1) else "비공개") if mine else row.get("asker_nickname", "")
        is_open = st.session_state[open_key] == qid
        marker = "▾" if is_open else "▸"

        cols = st.columns([1.1, 4, 1.4, 1.4, 1.2, 1.2])
        cols[0].caption(status)
        if cols[1].button(f"{marker} {title}", key=f"{key_prefix}_toggle_{qid}", use_container_width=True):
            st.session_state[open_key] = None if is_open else qid
            st.rerun()
        cols[2].caption(str(third))
        cols[3].caption(str(row["expert_name"]))
        cols[4].caption(asked_at)
        cols[5].caption(answered_at or "-")

        if is_open:
            with st.container(border=True):
                meta_parts = [str(row["expert_name"])]
                if row.get("current_job"):
                    meta_parts.append(str(row["current_job"]))
                if row.get("field"):
                    meta_parts.append(str(row["field"]))
                meta_parts.append(asked_at)
                st.markdown(f"**{title}**")
                st.caption(" · ".join(meta_parts))
                st.markdown(f'<div class="qa-q">Q. {row["question_text"]}</div>', unsafe_allow_html=True)
                if pd.notna(row["answer_text"]):
                    st.markdown(f'<div class="qa-a">A. {row["answer_text"]}</div>', unsafe_allow_html=True)
                else:
                    st.caption("아직 답변이 없습니다.")

init_accounts()

with st.sidebar:
    # ── 로고 ──────────────────────────────
    st.markdown("""
    <a class="sidebar-brand" href="?fu_page=home" target="_self" aria-label="홈으로 이동">
        <div class="sidebar-brand-title">Future Universe</div>
        <div class="sidebar-brand-subtitle">Career Exploration</div>
    </a>
    """, unsafe_allow_html=True)
    st.markdown('<hr class="nav-divider">', unsafe_allow_html=True)

    # ── 로그인 / 계정 영역 (최상단) ──────
    if st.session_state.account:
        u          = st.session_state.account
        uname      = u.get("display_name") or get_account_display_name(u["account_id"], u["login_id"])
        role_label = {"admin": "관리자", "expert": "전문가", "student": "학생"}.get(u["role"], "계정")
        st.markdown(f"""
        <div style='background:rgba(74,144,255,0.08);border-radius:4px;border:1px solid rgba(170,205,255,0.62);border-left:2px solid #4A90FF;
                    padding:0.65rem 0.9rem;margin:0.2rem 0 0.85rem 0;'>
            <div style='color:#C8DCFF;font-weight:600;font-size:0.88rem;'>{uname}</div>
            <div style='color:#8FA8E8;font-size:0.72rem;letter-spacing:0.3px;'>{role_label}</div>
        </div>
        """, unsafe_allow_html=True)
        # 역할별 알림 카운트
        _badge_n = 0
        if u["role"] == "expert":
            _ep = get_expert_profile(u["account_id"])
            if _ep:
                _badge_n = get_unanswered_count(_ep["id"])
        elif u["role"] == "student":
            _badge_n = get_new_answer_count(u["account_id"])

        _profile_label = f"내 프로필  🔴 {_badge_n}" if _badge_n else "내 프로필"

        col_profile, col_logout = st.columns(2)
        with col_profile:
            if st.button(_profile_label, use_container_width=True, key="sb_profile"):
                st.session_state.page = "profile"
                st.rerun()
        with col_logout:
            if st.button("로그아웃", use_container_width=True, key="sb_logout"):
                st.session_state.account = None
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

    if st.session_state.account and st.session_state.account.get("role") == "admin":
        st.markdown('<hr class="nav-divider">', unsafe_allow_html=True)
        st.markdown('<span class="nav-section">관리자</span>', unsafe_allow_html=True)
        nav_btn("설문 대시보드", "admin_dashboard")
        nav_btn("섭외 인사이트", "admin_gap_insights")
        nav_btn("DB 관리", "admin_db_viewer")
        # 미승인 전문가 수 배지
        _conn = get_conn()
        _pending = _conn.execute(
            "SELECT COUNT(*) FROM expert_profiles WHERE is_approved=0"
        ).fetchone()[0]
        _conn.close()
        nav_btn("전문가 승인 관리", "admin_expert_approval",
                badge=f"{_pending}명 대기" if _pending else None)

    st.markdown('<hr class="nav-divider" style="margin-top:0.4rem;">', unsafe_allow_html=True)
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
# 3D HTML 임베딩 — 실제 DB 전문가 기반
# ══════════════════════════════════════════
FIELD_COLORS = {
    "과학/기술": 0x85B7EB,
    "예술/디자인": 0xED93B1,
    "사회/경영": 0x97C459,
    "미디어/콘텐츠": 0xEF9F27,
    "의료/바이오": 0x5DCAA5,
    "교육": 0xAFA9EC,
    "환경/에너지": 0x1D9E75,
    "기타": 0x8FA7D6,
}

NODE_COLORS = {
    "양자역학": 0x85B7EB,
    "AI": 0x97C459,
    "데이터 분석": 0x5DCAA5,
    "글쓰기": 0xE24B4A,
    "영상제작": 0xAFA9EC,
    "사진": 0xED93B1,
    "디자인": 0xF09595,
    "과학커뮤니케이션": 0xEF9F27,
    "대중강연": 0xF0997B,
    "저널리즘": 0x7F77DD,
    "환경보호": 0x1D9E75,
    "기후위기": 0x0F6E56,
    "사회혁신": 0x378ADD,
    "교육": 0xFA9F27,
    "SF 독서": 0xD4537E,
    "등산": 0x639922,
    "요리": 0xBA7517,
    "음악": 0x993556,
}

def _sphere_position(index, total, radius):
    """Deterministic spherical layout for stable 3D maps."""
    if total <= 1:
        return [0, 0, radius]
    phi = math.acos(1 - 2 * (index + 0.5) / total)
    theta = math.pi * (1 + math.sqrt(5)) * index
    return [
        round(math.cos(theta) * math.sin(phi) * radius, 2),
        round(math.sin(theta) * math.sin(phi) * radius, 2),
        round(math.cos(phi) * radius, 2),
    ]

def _color_for_name(name, fallback_palette):
    if name in NODE_COLORS:
        return NODE_COLORS[name]
    digest = int(hashlib.sha256(name.encode("utf-8")).hexdigest()[:8], 16)
    return fallback_palette[digest % len(fallback_palette)]

def _clean_desc(*parts):
    safe = []
    for part in parts:
        if part:
            safe.append(str(part).replace("<", "&lt;").replace(">", "&gt;"))
    return "<br>".join(safe)

def build_3d_universe_data():
    """Build Three.js nodes/connections from approved experts in SQLite."""
    conn = get_conn()
    expert_rows = conn.execute("""
        SELECT ep.id, ep.display_name, ep.current_job, ep.organization,
               ep.major, ep.field, ep.description, ep.title
        FROM expert_profiles ep
        WHERE ep.is_approved = 1
        ORDER BY ep.created_at DESC, ep.id ASC
    """).fetchall()
    node_rows = conn.execute("""
        SELECT ep.id AS expert_id, en.node_name
        FROM expert_profiles ep
        JOIN expert_nodes en ON en.expert_id = ep.id
        WHERE ep.is_approved = 1
        ORDER BY ep.id ASC, en.node_name ASC
    """).fetchall()
    conn.close()

    expert_nodes = {}
    actual_node_names = []
    for expert_id, node_name in node_rows:
        if not node_name:
            continue
        expert_nodes.setdefault(expert_id, []).append(node_name)
        actual_node_names.append(node_name)

    topic_names = list(dict.fromkeys(actual_node_names))
    palette = [0x85B7EB, 0x97C459, 0x5DCAA5, 0xED93B1, 0xEF9F27, 0xAFA9EC, 0x1D9E75]

    nodes = []
    expert_index_by_id = {}
    total_experts = max(len(expert_rows), 1)
    for idx, row in enumerate(expert_rows):
        expert_id, name, current_job, organization, major, field, description, title = row
        related = expert_nodes.get(expert_id, [])
        headline = " · ".join([p for p in [current_job or title, organization] if p])
        meta = " · ".join([p for p in [major, field] if p])
        related_text = "연결 노드: " + ", ".join(related[:5]) if related else "연결 노드 없음"
        desc = _clean_desc(headline, meta, description, related_text)
        expert_index_by_id[expert_id] = len(nodes)
        nodes.append({
            "name": name or f"전문가 {expert_id}",
            "type": "expert",
            "desc": desc,
            "pos": _sphere_position(idx, total_experts, 11),
            "color": FIELD_COLORS.get(field, FIELD_COLORS["기타"]),
            "size": 0.68,
        })

    node_index_by_name = {}
    total_topics = max(len(topic_names), 1)
    for idx, name in enumerate(topic_names):
        node_index_by_name[name] = len(nodes)
        degree = actual_node_names.count(name)
        nodes.append({
            "name": name,
            "type": "node",
            "desc": _clean_desc("관심사·활동 노드", f"연결 전문가 {degree}명" if degree else "아직 연결 전문가 없음"),
            "pos": _sphere_position(idx, total_topics, 5.6),
            "color": _color_for_name(name, palette),
            "size": round(min(0.65, 0.38 + degree * 0.05), 2),
        })

    connections = []
    seen = set()
    for expert_id, node_names in expert_nodes.items():
        from_idx = expert_index_by_id.get(expert_id)
        if from_idx is None:
            continue
        for node_name in node_names:
            to_idx = node_index_by_name.get(node_name)
            if to_idx is None:
                continue
            edge = (from_idx, to_idx)
            if edge not in seen:
                seen.add(edge)
                connections.append([from_idx, to_idx])

    return nodes, connections

def inject_3d_universe_data(html_content):
    nodes, connections = build_3d_universe_data()
    nodes_js = json.dumps(nodes, ensure_ascii=False)
    connections_js = json.dumps(connections, ensure_ascii=False)

    html_content = re.sub(
        r"// 노드 데이터\s*const nodes = \[.*?\];\s*// 연결선 데이터.*?const connections = \[.*?\];",
        (
            "// 노드 데이터 — SQLite 승인 전문가 기반\n"
            f"const nodes = {nodes_js};\n\n"
            "// 연결선 데이터 — 전문가 활동 노드 기반\n"
            f"const connections = {connections_js};"
        ),
        html_content,
        flags=re.S,
    )
    return html_content

def embed_3d_with_overlay(html_path, height=620, overlay=True):
    """3D HTML을 임베딩합니다. overlay=True이면 클릭 시 로그인 안내 팝업을 표시합니다."""

    overlay_code = """
<style>
/* 로그인 전 3D 접근 제한 레이어 */
#fu-overlay {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 9998;
    cursor: default;
    background: rgba(5, 10, 20, 0.68);
    color: #D8E7FF;
    border: none;
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
}
.fu-lock-card {
    width: min(440px, 92vw);
    background: linear-gradient(135deg, #10192E 0%, #172847 100%);
    border: 1px solid rgba(39,214,162,0.62);
    border-radius: 12px;
    padding: 2.4rem 2rem;
    text-align: center;
    box-shadow: 0 30px 80px rgba(0,0,0,0.55);
}
.fu-lock-icon { font-size: 2.8rem; margin-bottom: 0.55rem; }
.fu-lock-title { color: #fff; font-size: 1.35rem; font-weight: 800; margin-bottom: 0.55rem; }
.fu-lock-desc { color: #c9d1f5; line-height: 1.7; font-size: 0.95rem; margin: 0; }
.fu-lock-hint { color: #8FA7D6; font-size: 0.8rem; margin-top: 1rem; line-height: 1.6; }
</style>

<!-- 로그인 전 접근 제한 안내 -->
<div id="fu-overlay">
    <div class="fu-lock-card">
        <div class="fu-lock-icon">🔐</div>
        <div class="fu-lock-title">3D 탐색기는 로그인 후 이용할 수 있습니다</div>
        <p class="fu-lock-desc">관심 노드 저장, 나만의 우주 구성, 전문가 연결 기능을 안전하게 제공하기 위해 로그인이 필요합니다.</p>
        <div class="fu-lock-hint">왼쪽 사이드바에서 로그인 또는 회원가입을 진행해 주세요.</div>
    </div>
</div>

"""

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        html_content = inject_3d_universe_data(html_content)
        if overlay:
            html_content = html_content.replace("</body>", overlay_code + "\n</body>")
        components.html(html_content, height=height, scrolling=False)
    except FileNotFoundError:
        st.warning(f"3D HTML 파일(`{html_path}`)을 찾을 수 없습니다. 파일을 확인해 주세요.")


# ══════════════════════════════════════════
# 실제 DB 기반 전문가 데이터프레임
# ══════════════════════════════════════════
@st.cache_data(ttl=60)
def load_expert_dataframe():
    """승인된 전문가만 조회. 필수 항목(현재 직업·전공)이 모두 있는 행만 포함."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT ep.display_name  AS 이름,
               ep.current_job   AS 현재직업,
               ep.major         AS 전공,
               ep.field         AS 활동분야,
               ep.title         AS 직함,
               ep.organization  AS 소속,
               ep.description   AS 소개,
               ep.contact_email AS 연락처
        FROM expert_profiles ep
        WHERE ep.is_approved = 1
          AND ep.current_job  IS NOT NULL AND ep.current_job  != ''
          AND ep.major        IS NOT NULL AND ep.major        != ''
          AND ep.field        IS NOT NULL AND ep.field        != ''
        ORDER BY ep.created_at DESC
    """).fetchall()
    conn.close()

    cols = ['이름', '현재 직업', '전공', '활동 분야', '직함', '소속', '소개', '연락처']
    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows, columns=cols)

df_all = load_expert_dataframe()


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

    # survey_participants: 로그인 계정과 연결되는 설문 응답자 프로필
    c.execute("""CREATE TABLE IF NOT EXISTS survey_participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login_id TEXT UNIQUE REFERENCES accounts(login_id) ON DELETE CASCADE,
        name TEXT NOT NULL, gender TEXT NOT NULL,
        school TEXT, grade TEXT,
        age INTEGER NOT NULL,
        respondent_type TEXT,
        school_level TEXT,
        created_at TEXT NOT NULL)""")

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

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='survey_responses'")
    if not c.fetchone():
        c.execute("""CREATE TABLE survey_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_id INTEGER NOT NULL REFERENCES survey_participants(id) ON DELETE CASCADE,
            question_id INTEGER NOT NULL REFERENCES survey_questions(id) ON DELETE CASCADE,
            response_value TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(participant_id, question_id))""")
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
# 초기 데이터 생성 — 전문가 중심, 설문 응답 제외
# ══════════════════════════════════════════
def _read_seed_csv(file_name, required_columns):
    seed_dir = SEED_DATA_DIR if os.path.exists(SEED_DATA_DIR) else LEGACY_SEED_DATA_DIR
    path = os.path.join(seed_dir, file_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"초기 데이터 CSV 파일이 없습니다: {path}")
    df = pd.read_csv(path, dtype=str).fillna("")
    df.columns = [str(col).strip() for col in df.columns]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"{file_name}에 필요한 컬럼이 없습니다: {', '.join(missing)}")
    for col in df.columns:
        df[col] = df[col].map(lambda value: value.strip() if isinstance(value, str) else value)
    return df


def seed_initial_data():
    """CSV 파일에서 5개 핵심 테이블용 초기 데이터를 SQLite DB에 추가합니다."""
    init_accounts()
    init_db()

    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat(timespec="seconds")

    def _cols(table_name):
        return {r[1] for r in c.execute(f"PRAGMA table_info({table_name})").fetchall()}

    def _insert_or_ignore(table_name, data):
        available = _cols(table_name)
        filtered = {key: value for key, value in data.items() if key in available}
        if not filtered:
            return
        names = list(filtered.keys())
        placeholders = ",".join(["?"] * len(names))
        c.execute(
            f"INSERT OR IGNORE INTO {table_name} ({','.join(names)}) VALUES ({placeholders})",
            tuple(filtered[name] for name in names),
        )

    def _account_id(login_id):
        row = c.execute("SELECT id FROM accounts WHERE login_id=?", (login_id,)).fetchone()
        return row[0] if row else None

    expert_profile_cols = _cols("expert_profiles")
    student_profile_cols = _cols("student_profiles")
    my_universe_cols = _cols("my_universe")

    accounts_df = _read_seed_csv("accounts.csv", ["login_id", "password", "role", "tokens"])
    expert_profiles_df = _read_seed_csv(
        "expert_profiles.csv",
        ["login_id", "nickname", "title", "organization", "major", "current_job", "field", "description", "contact_email", "is_approved"],
    )
    expert_nodes_df = _read_seed_csv("expert_nodes.csv", ["login_id", "node_name"])
    student_profiles_df = _read_seed_csv("student_profiles.csv", ["login_id", "nickname", "school_level", "school_name", "grade"])
    my_universe_df = _read_seed_csv("student_univers.csv", ["login_id", "node_name"])

    seed_token_bases = {}
    for _, row in accounts_df.iterrows():
        seed_login_id = row["login_id"]
        if not seed_login_id:
            continue
        password = row["password"] or "mock1234"
        role = row["role"] or "student"
        try:
            tokens = int(row["tokens"] or 0)
        except ValueError:
            tokens = 0
        seed_token_bases[seed_login_id] = tokens
        c.execute(
            """INSERT OR IGNORE INTO accounts (login_id, password_hash, role, tokens)
               VALUES (?,?,?,?)""",
            (seed_login_id, _hash_pw(password), role, tokens),
        )
        c.execute(
            "UPDATE accounts SET role=? WHERE login_id=?",
            (role, seed_login_id),
        )

    for seed_login_id, base_tokens in seed_token_bases.items():
        runtime_delta = c.execute(
            """SELECT COALESCE(SUM(amount), 0)
               FROM token_transactions
               WHERE login_id=? AND reason <> ?""",
            (seed_login_id, "가입 보너스"),
        ).fetchone()[0] or 0
        c.execute(
            "UPDATE accounts SET tokens=? WHERE login_id=?",
            (base_tokens + int(runtime_delta), seed_login_id),
        )

    for _, row in expert_profiles_df.iterrows():
        seed_login_id = row["login_id"]
        account_id = _account_id(seed_login_id)
        if account_id is None:
            continue
        is_approved = 1 if str(row["is_approved"]).lower() in ("1", "true", "y", "yes", "승인") else 0
        profile_data = {
            "login_id": seed_login_id,
            "display_name": row["nickname"],
            "title": row["title"],
            "organization": row["organization"],
            "major": row["major"],
            "current_job": row["current_job"],
            "field": row["field"],
            "description": row["description"],
            "contact_email": row["contact_email"],
            "is_approved": is_approved,
            "created_at": now,
        }
        _insert_or_ignore("expert_profiles", profile_data)
        update_cols = [
            "login_id", "display_name", "title", "organization", "major",
            "current_job", "field", "description", "contact_email", "is_approved",
        ]
        update_cols = [col for col in update_cols if col in expert_profile_cols]
        where_col = "login_id"
        where_val = seed_login_id
        c.execute(
            f"""UPDATE expert_profiles
                SET {', '.join([f'{col}=?' for col in update_cols])}
                WHERE {where_col}=?""",
            tuple(profile_data[col] for col in update_cols) + (where_val,),
        )

    for _, row in expert_nodes_df.iterrows():
        account_id = _account_id(row["login_id"])
        if account_id is None:
            continue
        where_col = "login_id"
        where_val = row["login_id"]
        profile = c.execute(f"SELECT id FROM expert_profiles WHERE {where_col}=?", (where_val,)).fetchone()
        if profile and row["node_name"]:
            c.execute(
                "INSERT OR IGNORE INTO expert_nodes (expert_id, node_name) VALUES (?,?)",
                (profile[0], row["node_name"]),
            )

    for _, row in student_profiles_df.iterrows():
        seed_login_id = row["login_id"]
        account_id = _account_id(seed_login_id)
        if account_id is None:
            continue
        profile_data = {
            "login_id": seed_login_id,
            "display_name": row["nickname"],
            "school_level": row["school_level"],
            "school_name": row["school_name"],
            "grade": row["grade"],
            "created_at": now,
        }
        _insert_or_ignore("student_profiles", profile_data)
        update_cols = ["login_id", "display_name", "school_level", "school_name", "grade"]
        update_cols = [col for col in update_cols if col in student_profile_cols]
        where_col = "login_id"
        where_val = seed_login_id
        c.execute(
            f"""UPDATE student_profiles
                SET {', '.join([f'{col}=?' for col in update_cols])}
                WHERE {where_col}=?""",
            tuple(profile_data[col] for col in update_cols) + (where_val,),
        )

    for _, row in my_universe_df.iterrows():
        account_id = _account_id(row["login_id"])
        if account_id is not None and row["node_name"]:
            universe_data = {
                "login_id": row["login_id"],
                "node_name": row["node_name"],
                "selected_at": now,
            }
            _insert_or_ignore("my_universe", universe_data)

    conn.commit()
    conn.close()


init_accounts()
seed_initial_data()

_pending_universe_save = st.query_params.get("fu_save_universe")
if _pending_universe_save:
    current_account = st.session_state.get("account")
    if isinstance(_pending_universe_save, list):
        _pending_universe_save = _pending_universe_save[0]
    if current_account and current_account.get("role") == "student":
        try:
            requested_nodes = json.loads(_pending_universe_save)
        except Exception:
            requested_nodes = None
        if isinstance(requested_nodes, list):
            current_3d_nodes, _ = build_3d_universe_data()
            valid_nodes = {n["name"] for n in current_3d_nodes if n.get("type") == "node"}
            selected_nodes = [
                str(name) for name in requested_nodes
                if isinstance(name, str) and name in valid_nodes
            ]
            save_my_universe(current_account, selected_nodes)
            st.session_state.show_universe_save_dialog = len(selected_nodes)
    st.session_state.page = "3d"
    try:
        del st.query_params["fu_save_universe"]
    except Exception:
        st.query_params.clear()


# ══════════════════════════════════════════
# PAGE: 홈
# ══════════════════════════════════════════
if st.session_state.page == "home":
    _home_account = st.session_state.get("account")

    # DB 실시간 지표
    _conn = get_conn()
    _expert_cnt = _conn.execute("SELECT COUNT(*) FROM expert_profiles WHERE is_approved=1").fetchone()[0]
    _q_cnt      = _conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    _ans_cnt    = _conn.execute("SELECT COUNT(*) FROM question_answers").fetchone()[0]
    _conn.close()

    _expert_stat = f"{_expert_cnt}" if _expert_cnt else "모집 중"
    _q_stat = f"{_q_cnt}" if _q_cnt else "준비됨"
    _ans_stat = f"{_ans_cnt}" if _ans_cnt else "대기 중"

    # 히어로 배너 + CSS 클래스 기반 지표
    st.markdown(f"""
    <div class="hero">
        <div class="hero-kicker">Career Exploration Platform</div>
        <div class="hero-title"><span class="hero-accent">Future</span> Universe에서 진로의 연결을 탐색하세요</div>
        <p class="hero-sub">관심 분야를 3D 유니버스에서 둘러보고, 실제 전문가의 전공·직업·답변을 바탕으로 나만의 커리어 방향을 설계합니다.</p>
        <div class="home-flow">
            <span>관심 노드 발견</span>
            <span>전문가 연결</span>
            <span>질문과 답변</span>
            <span>로드맵 생성</span>
        </div>
        <div class="hero-stat-wrap">
            <div class="hero-stat">
                <div class="hero-stat-num">{_expert_stat}</div>
                <div class="hero-stat-label">등록 전문가</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-num">{_q_stat}</div>
                <div class="hero-stat-label">누적 질문</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-num">{_ans_stat}</div>
                <div class="hero-stat-label">전문가 답변</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="shortcut-title">바로가기</div>', unsafe_allow_html=True)
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    with nav_col1:
        if st.button("3D 유니버스", use_container_width=True, type="primary", key="home_go_3d"):
            st.session_state.page = "3d"
            st.rerun()
    with nav_col2:
        if st.button("전문가 Q&A", use_container_width=True, key="home_go_questions"):
            st.session_state.page = "questions"
            st.rerun()
    with nav_col3:
        if st.button("AI 진로상담", use_container_width=True, key="home_go_career"):
            st.session_state.page = "career"
            st.rerun()

    # 비로그인 기능 소개 카드 — CSS 클래스 사용
    if not _home_account:
        st.markdown("""
        <div class="feature-cards">
            <div class="feature-card">
                <div class="feature-card-icon">3D</div>
                <div class="feature-card-title">3D 유니버스 탐색</div>
                <div class="feature-card-desc">로그인 후 관심 주제와 전문가가 연결된 지도를 탐색합니다.</div>
            </div>
            <div class="feature-card">
                <div class="feature-card-icon">＋</div>
                <div class="feature-card-title">나만의 관심 노드</div>
                <div class="feature-card-desc">마음에 드는 분야를 저장하고 내 진로 후보군으로 모읍니다.</div>
            </div>
            <div class="feature-card">
                <div class="feature-card-icon">Q</div>
                <div class="feature-card-title">전문가 Q&amp;A</div>
                <div class="feature-card-desc">직업과 전공에 대한 궁금증을 승인된 전문가에게 질문합니다.</div>
            </div>
            <div class="feature-card">
                <div class="feature-card-icon">AI</div>
                <div class="feature-card-title">AI 커리어 설계</div>
                <div class="feature-card-desc">관심사와 질문 기록을 바탕으로 다음 행동을 구체화합니다.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    # 3D 탐색기 미리보기
    st.markdown('<div class="section-title">3D 탐색기 미리보기</div>', unsafe_allow_html=True)
    st.caption(f'{datetime.now().strftime("%Y-%m-%d")}  ·  3D 탐색기는 로그인 후 이용할 수 있습니다')
    embed_3d_with_overlay("future_universe_3d (1).html", height=580,
                          overlay=_home_account is None)

    # 이번 주 전문가 — 실제 DB
    st.markdown('<div class="section-title">이번 주 전문가</div>', unsafe_allow_html=True)
    col_expert, col_advice = st.columns(2, gap="large")

    with col_expert:
        with st.container(border=True):
            st.markdown("**최근 합류한 전문가**")
            st.divider()
            _conn2 = get_conn()
            _ep_row = _conn2.execute("""
                SELECT ep.display_name, ep.current_job, ep.organization,
                       ep.field, ep.description, ep.major
                FROM expert_profiles ep
                WHERE ep.is_approved=1
                ORDER BY ep.created_at DESC LIMIT 1
            """).fetchone()
            _conn2.close()
            if _ep_row:
                _name, _job, _org, _field, _desc, _major = _ep_row
                st.markdown(f'<div class="expert-name">{_name}</div>', unsafe_allow_html=True)
                _tags = " · ".join(filter(None, [_job, _org, _field, _major]))
                st.markdown(f'<div class="expert-tags">{_tags}</div>', unsafe_allow_html=True)
                if _desc:
                    st.caption(_desc[:100] + ("..." if len(_desc or "") > 100 else ""))
            else:
                st.caption("아직 등록된 전문가가 없습니다.")

    with col_advice:
        with st.container(border=True):
            st.markdown("**전문가 최신 답변**")
            st.divider()
            _conn3 = get_conn()
            _qa_rows = _conn3.execute("""
                SELECT ep.display_name, q.question_text, qa.answer_text
                FROM question_answers qa
                JOIN questions q ON q.id = qa.question_id
                JOIN expert_profiles ep ON ep.id = q.to_expert_id
                WHERE q.is_public = 1
                ORDER BY qa.created_at DESC LIMIT 2
            """).fetchall()
            _conn3.close()
            if _qa_rows:
                for _en, _qt, _at in _qa_rows:
                    with st.expander(f"from. {_en}"):
                        st.markdown(f'<div class="qa-q">Q. {_qt}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="qa-a">A. {_at}</div>', unsafe_allow_html=True)
            else:
                st.caption("아직 공개된 답변이 없습니다.")

    # 진로 탐색 영상 (CTA 앞으로 이동)
    st.markdown('<div class="section-title">진로 탐색 영상</div>', unsafe_allow_html=True)
    render_career_videos()

    # CTA — 하나의 컨테이너 안에서 설명과 버튼을 함께 제공
    with st.container(border=True):
        st.markdown("### 퓨처유니버스 설문조사")
        st.caption("여러분의 소중한 의견이 퓨처유니버스를 더 좋게 만드는 데 쓰입니다.")
        if st.button("설문조사 참여하기 →", use_container_width=True, type="primary"):
            st.session_state.page = "survey"
            st.session_state.survey_page = 1
            st.rerun()



# ══════════════════════════════════════════
# PAGE: 진로 탐색 영상
# ══════════════════════════════════════════
elif st.session_state.page == "career_videos":
    st.title("진로 탐색 영상")
    st.caption("미래 직업과 다양한 직업 세계를 영상으로 둘러봅니다.")

    current_account = st.session_state.get("account")
    is_admin = bool(current_account and current_account.get("role") == "admin")

    if is_admin:
        if st.button("영상 추가", type="primary", use_container_width=False):
            career_video_dialog()
        st.caption("관리자 모드: 영상을 추가하거나 삭제할 수 있습니다.")

    render_career_videos(show_admin_controls=is_admin)

    with st.expander("영상 사용과 저작권 안내"):
        st.write(
            "현재 영상은 YouTube 임베드 방식으로 표시됩니다. 공개 영상이라도 저작권은 원저작자에게 있으며, "
            "서비스 운영·수업·행사에서 안정적으로 사용하려면 공식 채널 영상인지, 임베드가 허용되어 있는지, "
            "교육/상업적 활용 조건에 문제가 없는지 확인하는 것이 좋습니다."
        )
        st.write(
            "가장 안전한 방식은 기관 공식 채널 영상, 저작권자가 명시적으로 허용한 영상, 또는 직접 제작한 영상을 사용하는 것입니다."
        )


# ══════════════════════════════════════════
# PAGE: 설문조사
# ══════════════════════════════════════════
elif st.session_state.page == "survey":
    init_db()
    current_account = st.session_state.get("account")
    if not current_account:
        st.warning("이벤트는 로그인 후 이용할 수 있습니다.")
        st.caption("왼쪽 사이드바에서 로그인 또는 회원가입을 진행해 주세요.")
        st.stop()

    progress = st.session_state.survey_page / 3

    # ── 페이지 1: 인구통계 ──────────────────────────────────────────────
    if st.session_state.survey_page == 1:
        st.title("퓨처유니버스 참여자 설문")
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
                existing = c.execute(
                    "SELECT id FROM survey_participants WHERE login_id=?",
                    (current_account["login_id"],)
                ).fetchone()
                if existing:
                    participant_id = existing[0]
                    c.execute(
                        """UPDATE survey_participants
                           SET name=?, gender=?, school=?, grade=?, age=?,
                               respondent_type=?, school_level=?, created_at=?
                           WHERE id=?""",
                        (name.strip(), gender, school.strip(), grade, int(age),
                         rtype, school_level, datetime.now().isoformat(), participant_id)
                    )
                else:
                    c.execute(
                        """INSERT INTO survey_participants
                           (login_id, name, gender, school, grade, age,
                            respondent_type, school_level, created_at)
                           VALUES (?,?,?,?,?,?,?,?,?)""",
                        (current_account["login_id"], name.strip(), gender, school.strip(), grade,
                         int(age), rtype, school_level, datetime.now().isoformat())
                    )
                    participant_id = c.lastrowid
                conn.commit()
                st.session_state.survey_participant_id  = participant_id
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
                    c.execute("DELETE FROM survey_responses WHERE participant_id=?", (st.session_state.survey_participant_id,))
                    c.executemany("INSERT INTO survey_responses (participant_id,question_id,response_value,created_at) VALUES (?,?,?,?)",
                                  [(st.session_state.survey_participant_id, qid, str(v), now) for qid, v in responses.items()])
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
            st.session_state.survey_participant_id  = None
            st.session_state.survey_respondent_type = "학생"
            st.session_state.page = "home"
            st.rerun()


# ══════════════════════════════════════════
# PAGE: 3D 탐색기
# ══════════════════════════════════════════
elif st.session_state.page == "3d":
    st.title("3D 커리어 유니버스 탐색기")
    st.write("전문가는 별(Star), 관심사·활동은 구(Sphere)로 연결됩니다.")

    # ── 저장된 관심 노드 로드 ────────────────────────────────────────
    account = st.session_state.get("account")
    if not account:
        st.warning("3D 탐색기는 로그인 후 이용할 수 있습니다.")
        st.caption("왼쪽 사이드바에서 로그인 또는 회원가입을 진행해 주세요.")
        st.stop()

    if account and account["role"] == "student":
        raw_save_nodes = st.query_params.get("fu_save_universe")
        if raw_save_nodes:
            try:
                if isinstance(raw_save_nodes, list):
                    raw_save_nodes = raw_save_nodes[0]
                requested_nodes = json.loads(raw_save_nodes)
            except Exception:
                requested_nodes = None
            if isinstance(requested_nodes, list):
                current_3d_nodes, _ = build_3d_universe_data()
                valid_nodes = {n["name"] for n in current_3d_nodes if n.get("type") == "node"}
                selected_nodes = [
                    str(name) for name in requested_nodes
                    if isinstance(name, str) and name in valid_nodes
                ]
                save_my_universe(account, selected_nodes)
                st.session_state.show_universe_save_dialog = len(selected_nodes)
            try:
                del st.query_params["fu_save_universe"]
            except Exception:
                st.query_params.clear()

    if "show_universe_save_dialog" in st.session_state:
        count = st.session_state.pop("show_universe_save_dialog")
        universe_save_dialog(count)

    saved_nodes = load_my_universe(account) if (account and account["role"] == "student") else []

    # ── 3D 뷰어 (저장 노드 주입) ─────────────────────────────────────
    html_path = "future_universe_3d (1).html"
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        html_content = inject_3d_universe_data(html_content)

        # 저장된 노드를 JS로 주입 — DB 상태를 기준으로 3D 선택 상태를 항상 초기화
        inject = f"""
<script>
(function() {{
  const _savedNames = {json.dumps(saved_nodes, ensure_ascii=False)};
  function _loadSaved() {{
    myUniverse.clear();
    _savedNames.forEach(function(name) {{
      const idx = nodes.findIndex(function(n) {{ return n.name === name && n.type === 'node'; }});
      if (idx !== -1) myUniverse.add(idx);
    }});
    updateMyUniversePanel();

    if (myUniverse.size > 0) {{
      isMyUniverseMode = true;
      const btn = document.getElementById('view-universe-btn');
      if (btn) btn.textContent = '전체 네트워크 보기 🌐';
      showMyUniverse();
    }} else if (typeof exitMyUniverseMode === 'function') {{
      exitMyUniverseMode();
    }}
  }}
  if (typeof nodes !== 'undefined' && typeof showMyUniverse === 'function') {{
    _loadSaved();
  }} else {{
    window.addEventListener('load', _loadSaved);
  }}
}})();
</script>
"""
        html_content = html_content.replace("</body>", inject + "\n</body>")

        component_key = "future_universe_3d_" + hashlib.md5(
            json.dumps(saved_nodes, ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:10]
        component_value = render_3d_universe_component(html_content, key=component_key)
        if isinstance(component_value, dict) and component_value.get("type") == "save_universe":
            nonce = component_value.get("nonce")
            if nonce and st.session_state.get("last_universe_save_nonce") != nonce:
                requested_nodes = component_value.get("nodes") or []
                current_3d_nodes, _ = build_3d_universe_data()
                valid_nodes = {n["name"] for n in current_3d_nodes if n.get("type") == "node"}
                selected_nodes = [
                    str(name) for name in requested_nodes
                    if isinstance(name, str) and name in valid_nodes
                ]
                save_my_universe(account, selected_nodes)
                st.session_state.last_universe_save_nonce = nonce
                st.session_state.show_universe_save_dialog = len(selected_nodes)
                st.rerun()
    except FileNotFoundError:
        st.error(f"3D HTML 파일을 찾을 수 없습니다: {html_path}")
    if account and account["role"] == "student":
        st.divider()
        st.subheader("✨ 나만의 우주 저장")
        st.caption("3D 탐색기에서 선택한 구(노드)를 여기서 저장하면 다음에도 불러올 수 있습니다.")

        saved = load_my_universe(account)
        current_3d_nodes, _ = build_3d_universe_data()
        node_options = [
            n["name"] for n in current_3d_nodes
            if n.get("type") == "node"
        ]
        node_options = list(dict.fromkeys(node_options + saved))

        col_sel, col_saved = st.columns([3, 2], gap="large")
        with col_sel:
            with st.form("save_universe_form"):
                selected = st.multiselect(
                    "저장할 관심 노드(구) 선택",
                    node_options,
                    default=saved,
                    help="3D 뷰어에서 클릭했던 구들을 여기서 저장하세요."
                )
                if st.form_submit_button("저장하기", use_container_width=True, type="primary"):
                    save_my_universe(account, selected)
                    st.session_state.show_universe_save_dialog = len(selected)
                    st.rerun()

        with col_saved:
            with st.container(border=True):
                st.markdown("**현재 저장된 나만의 우주**")
                if saved:
                    for n in saved:
                        st.markdown(f"🔵 {n}")
                else:
                    st.caption("아직 저장된 노드가 없습니다.")
    elif account and account["role"] == "expert":
        # 전문가는 자신의 노드 확인
        st.divider()
        ep = get_expert_profile(account["account_id"])
        if ep:
            my_nodes = get_expert_nodes(ep["id"])
            if my_nodes:
                st.info(f"전문가로 등록된 관련 노드: {', '.join(my_nodes)}")
    elif not account:
        st.info("로그인하면 나만의 우주를 저장할 수 있습니다.")


# ══════════════════════════════════════════
# PAGE: 전문가 현황 (데이터베이스 + 분포 통합)
# ══════════════════════════════════════════
elif st.session_state.page in ("experts", "db", "distribution"):
    df_all = load_expert_dataframe()
    st.title("전문가 현황")
    st.write(f"승인된 전문가 **{len(df_all)}명**의 데이터입니다.")

    tab_db, tab_dist = st.tabs(["📋 데이터베이스", "📊 분포 현황"])

    with tab_db:
        df_filtered = show_career_filters(df_all)
        if not df_filtered.empty:
            st.dataframe(df_filtered, use_container_width=True)
            csv = df_filtered.to_csv(index=False).encode('utf-8-sig')
            st.download_button("CSV 다운로드", data=csv, file_name='expert_data.csv', mime='text/csv')

    with tab_dist:
        df_dist = df_all.copy()
        if df_dist.empty:
            st.info("아직 등록된 전문가 데이터가 없습니다.")
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("전체 전문가",  f"{len(df_dist)}명")
            m2.metric("직업군",       f"{df_dist['현재 직업'].nunique()}종")
            m3.metric("전공 수",      f"{df_dist['전공'].nunique()}종")
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("직업군별 인원")
                job_counts = df_dist["현재 직업"].value_counts().reset_index()
                job_counts.columns = ["직업", "인원"]
                fig = px.bar(job_counts, x="인원", y="직업", orientation='h',
                             color="인원", color_continuous_scale="Viridis", text_auto=True)
                fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.subheader("전공 분포")
                major_counts = df_dist["전공"].value_counts().reset_index()
                major_counts.columns = ["전공", "인원"]
                fig = px.pie(major_counts, values="인원", names="전공", hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            st.subheader("활동 분야 순위")
            project_counts = df_dist["활동 분야"].value_counts().reset_index()
            project_counts.columns = ["활동 분야", "인원"]
            fig = px.treemap(project_counts, path=["활동 분야"], values="인원",
                             color="인원", color_continuous_scale="RdBu")
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════
# PAGE: 진로 인사이트
# ══════════════════════════════════════════
elif st.session_state.page == "insights":
    init_db()
    df_all = load_expert_dataframe()
    st.title("진로 인사이트")
    st.caption("전문가, 관심 노드, 질문 데이터를 연결해 진로 탐색의 흐름을 보여줍니다.")

    conn = get_conn()
    interest_df = pd.read_sql("""
        SELECT node_name AS 관심노드, COUNT(*) AS 저장수
        FROM my_universe
        GROUP BY node_name
        ORDER BY 저장수 DESC, 관심노드 ASC
    """, conn)
    expert_node_df = pd.read_sql("""
        SELECT en.node_name AS 관심노드, COUNT(*) AS 전문가수
        FROM expert_nodes en
        JOIN expert_profiles ep ON ep.id = en.expert_id
        WHERE ep.is_approved = 1
        GROUP BY en.node_name
        ORDER BY 전문가수 DESC, 관심노드 ASC
    """, conn)
    question_df = pd.read_sql("""
        SELECT q.id, q.question_text, q.created_at, q.to_expert_id,
               ep.display_name AS 전문가, ep.current_job AS 현재직업,
               ep.major AS 전공, ep.field AS 분야,
               CASE WHEN qa.id IS NULL THEN 0 ELSE 1 END AS 답변완료
        FROM questions q
        JOIN expert_profiles ep ON ep.id = q.to_expert_id
        LEFT JOIN question_answers qa ON qa.question_id = q.id
    """, conn)
    conn.close()

    total_experts = len(df_all)
    total_saved = int(interest_df["저장수"].sum()) if not interest_df.empty else 0
    total_questions = len(question_df)
    answer_rate = round(question_df["답변완료"].mean() * 100, 1) if not question_df.empty else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("승인 전문가", f"{total_experts:,}명")
    m2.metric("저장된 관심 노드", f"{total_saved:,}개")
    m3.metric("누적 질문", f"{total_questions:,}개")
    m4.metric("답변률", f"{answer_rate}%")

    tab_interest, tab_path, tab_questions = st.tabs([
        "관심 트렌드",
        "전공-직업 연결",
        "질문 흐름",
    ])

    with tab_interest:
        st.subheader("학생이 많이 저장한 관심 노드")
        if interest_df.empty:
            st.info("아직 저장된 관심 노드가 없습니다. 학생이 3D 유니버스에서 노드를 저장하면 이곳에 표시됩니다.")
        else:
            top_interest = interest_df.head(12)
            fig = px.bar(
                top_interest,
                x="저장수",
                y="관심노드",
                orientation="h",
                text="저장수",
                color="저장수",
                color_continuous_scale="Tealgrn",
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            if not expert_node_df.empty:
                merged = pd.merge(interest_df, expert_node_df, on="관심노드", how="left").fillna({"전문가수": 0})
                merged["전문가수"] = merged["전문가수"].astype(int)
                st.markdown("**관심은 높지만 전문가 연결이 부족한 노드**")
                st.dataframe(
                    merged.sort_values(["저장수", "전문가수"], ascending=[False, True]).head(8),
                    use_container_width=True,
                    hide_index=True,
                )

    with tab_path:
        st.subheader("전공이 어떤 직업으로 이어지는지 보기")
        if df_all.empty:
            st.info("아직 승인된 전문가 데이터가 없습니다.")
        else:
            col_a, col_b = st.columns([1, 2])
            with col_a:
                selected_major = st.selectbox(
                    "전공 선택",
                    ["전체"] + sorted(df_all["전공"].dropna().unique().tolist()),
                    key="insight_major",
                )
            path_df = df_all.copy()
            if selected_major != "전체":
                path_df = path_df[path_df["전공"] == selected_major]

            job_counts = path_df["현재 직업"].value_counts().reset_index()
            job_counts.columns = ["현재 직업", "전문가수"]
            field_counts = path_df["활동 분야"].value_counts().reset_index()
            field_counts.columns = ["활동 분야", "전문가수"]

            if job_counts.empty:
                st.info("선택한 전공에 연결된 전문가 데이터가 없습니다.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    fig = px.bar(
                        job_counts.head(10),
                        x="전문가수",
                        y="현재 직업",
                        orientation="h",
                        text="전문가수",
                        color="전문가수",
                        color_continuous_scale="Blues",
                    )
                    fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    fig = px.treemap(
                        field_counts,
                        path=["활동 분야"],
                        values="전문가수",
                        color="전문가수",
                        color_continuous_scale="Mint",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                top_job = job_counts.iloc[0]["현재 직업"]
                st.info(f"{selected_major if selected_major != '전체' else '전체 전공'} 데이터에서 가장 많이 연결된 직업은 **{top_job}**입니다.")

    with tab_questions:
        st.subheader("학생들이 실제로 묻는 질문 흐름")
        if question_df.empty:
            st.info("아직 등록된 질문이 없습니다.")
        else:
            question_df["날짜"] = pd.to_datetime(question_df["created_at"], errors="coerce").dt.date
            daily = question_df.dropna(subset=["날짜"]).groupby("날짜").size().reset_index(name="질문수")
            field_q = question_df["분야"].fillna("기타").value_counts().reset_index()
            field_q.columns = ["분야", "질문수"]
            unanswered = question_df[question_df["답변완료"] == 0]

            c1, c2 = st.columns(2)
            with c1:
                if daily.empty:
                    st.caption("날짜별 질문 데이터가 부족합니다.")
                else:
                    fig = px.line(daily, x="날짜", y="질문수", markers=True)
                    st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig = px.bar(
                    field_q.head(10),
                    x="질문수",
                    y="분야",
                    orientation="h",
                    text="질문수",
                    color="질문수",
                    color_continuous_scale="YlGnBu",
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("**최근 미답변 질문**")
            if unanswered.empty:
                st.success("현재 미답변 질문이 없습니다.")
            else:
                recent_unanswered = unanswered.sort_values("created_at", ascending=False).head(5)
                for _, row in recent_unanswered.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{row['전문가']}** · {row['현재직업'] or '직업 미입력'}")
                        st.write(row["question_text"])

# ══════════════════════════════════════════
# PAGE: AI 진로상담
# ══════════════════════════════════════════
elif st.session_state.page == "career":
    st.title("AI 진로상담")
    st.markdown(
        '<div class="career-muted">관심 분야와 전문가 데이터를 바탕으로 진로 고민을 짧고 구체적으로 정리합니다.</div>',
        unsafe_allow_html=True,
    )

    current_account  = st.session_state.get("account")
    if not current_account:
        st.warning("AI 진로상담은 로그인 후 이용할 수 있습니다.")
        st.caption("왼쪽 사이드바에서 로그인 또는 회원가입을 진행해 주세요.")
        st.stop()

    df_career = load_expert_dataframe()

    # ── 개인 맞춤 컨텍스트 수집 ──────────────────────────────────────
    my_nodes        = []
    connected_names = []
    if current_account and current_account["role"] == "student":
        my_nodes = load_my_universe(current_account)
        if my_nodes:
            # 관심 노드와 연결된 전문가 이름 수집
            conn_db = get_conn()
            rows = conn_db.execute("""
                SELECT DISTINCT ep.display_name, ep.current_job, ep.major, ep.field
                FROM expert_profiles ep
                JOIN expert_nodes en ON en.expert_id = ep.id
                WHERE en.node_name IN ({})
                  AND ep.is_approved = 1
            """.format(",".join("?" * len(my_nodes))), my_nodes).fetchall()
            conn_db.close()
            connected_names = [f"{r[0]} ({r[1]}, {r[2]}, {r[3]})" for r in rows]

    # 개인 맥락 표시
    if my_nodes:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**내 관심 분야**")
                st.write(", ".join(my_nodes))
            with c2:
                st.markdown("**연결된 전문가**")
                st.write(", ".join([r.split(" (")[0] for r in connected_names]) or "없음")

    tab_consult, tab_roadmap = st.tabs(["AI 진로상담", "AI 진로로드맵"])

    # ── AI 진로상담 ───────────────────────────────────────────────
    with tab_consult:
        # 개인 맞춤 시스템 프롬프트 구성
        personal_ctx = ""
        if my_nodes:
            personal_ctx = f"""
계정 정보:
- 관심 분야 노드: {', '.join(my_nodes)}
- 연결된 전문가: {'; '.join(connected_names) if connected_names else '없음'}
이 정보를 적극적으로 활용하여 개인 맞춤 조언을 해주세요.
"""
        else:
            personal_ctx = """
계정 정보:
- 아직 My Universe에 저장된 관심 분야 노드가 없습니다.
답변할 때 이 점을 자연스럽게 언급하고, 더 정확한 추천을 위해 3D 유니버스에서 관심 노드를 먼저 저장해보라고 안내하세요.
"""
        system_prompt = f"""당신은 Future Universe 플랫폼의 커리어 AI 컨설턴트입니다.
전문가 네트워크 데이터를 기반으로 진로 상담을 진행합니다.
한국어로 친절하고 구체적으로 답변하세요. 답변은 300자 이내로 핵심만 말해주세요.
{personal_ctx}"""

        if my_nodes:
            interest_question = (
                f"제가 저장한 관심 분야인 {', '.join(my_nodes[:5])}를 진로로 연결하려면 "
                "무엇부터 해보면 좋을까요?"
            )
        else:
            interest_question = (
                "아직 나만의 우주에 저장한 관심 분야가 없습니다. "
                "관심 분야를 찾고 진로 탐색을 시작하려면 무엇부터 해보면 좋을까요?"
            )

        example_questions = {
            "직접 입력": "",
            "관심 분야 시작": interest_question,
        }
        if "career_question_draft" not in st.session_state:
            st.session_state.career_question_draft = ""
        if "career_example_choice_applied" not in st.session_state:
            st.session_state.career_example_choice_applied = "직접 입력"

        left_pad, main_col, right_pad = st.columns([0.08, 0.66, 0.26])
        with main_col:
            st.markdown('<div class="career-section-label">질문 방법</div>', unsafe_allow_html=True)
            example_choice = st.radio(
                "질문 방법",
                list(example_questions.keys()),
                horizontal=True,
                label_visibility="collapsed",
                key="career_example_choice",
            )
            if (
                example_choice != "직접 입력"
                and st.session_state.career_example_choice_applied != example_choice
            ):
                st.session_state.career_question_draft = example_questions[example_choice]
                st.session_state.career_example_choice_applied = example_choice
                st.rerun()

            # 대화 히스토리 초기화
            if "career_messages" not in st.session_state:
                st.session_state.career_messages = []
            for msg in st.session_state.career_messages:
                if msg.get("role") == "assistant" and (
                    "API 오류" in msg.get("content", "")
                    or "Incorrect API key" in msg.get("content", "")
                    or "invalid_api_key" in msg.get("content", "")
                ):
                    msg["content"] = (
                        "이전 AI 응답은 API 설정 오류 때문에 숨겼습니다. "
                        "현재는 안전한 로컬 가이드로 답변하도록 수정되어 있습니다. "
                        "다시 질문을 입력해 주세요."
                    )

            # 대화 표시
            if not st.session_state.career_messages:
                st.markdown(
                    '<div class="career-hint">예시를 선택하거나 아래에 진로 고민을 적어보세요.</div>',
                    unsafe_allow_html=True,
                )
            for msg in st.session_state.career_messages:
                avatar = "🙋" if msg["role"] == "user" else "🤖"
                name = "나" if msg["role"] == "user" else "AI 진로상담"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.markdown(f"**{name}**")
                    st.markdown(msg["content"])

            latest_question_text = next(
                (m["content"] for m in reversed(st.session_state.career_messages) if m.get("role") == "user"),
                ""
            )
            recommended_experts = recommend_experts_for_question(latest_question_text, my_nodes, limit=3) if latest_question_text.strip() else []
            if recommended_experts:
                st.markdown("**이 질문과 연결할 수 있는 전문가**")
                expert_cols = st.columns(min(3, len(recommended_experts)))
                for idx, expert in enumerate(recommended_experts):
                    with expert_cols[idx % len(expert_cols)]:
                        with st.container(border=True):
                            st.markdown(f"**{expert['display_name']}**")
                            meta = " · ".join(filter(None, [
                                expert.get("current_job"),
                                expert.get("organization"),
                                expert.get("field"),
                            ]))
                            if meta:
                                st.markdown(f"<div style='color:#C7D7FF;line-height:1.55;margin-top:0.35rem;'>{meta}</div>", unsafe_allow_html=True)
                            if expert.get("nodes"):
                                st.markdown(
                                    f"<div style='color:#B8C8EF;line-height:1.55;margin-top:0.75rem;'>활동 노드: {', '.join(expert['nodes'][:4])}</div>",
                                    unsafe_allow_html=True
                                )
                            st.markdown(f"<div style='color:#AFC2F0;line-height:1.55;margin-top:0.35rem;'>{expert['reason']}</div>", unsafe_allow_html=True)
                            if st.button("전문가에게 질문하기", key=f"ask_recommended_expert_{expert['id']}", use_container_width=True):
                                st.session_state.qa_active_tab = "질문하기"
                                st.session_state.qa_prefill_expert_id = expert["id"]
                                st.session_state.page = "questions"
                                st.rerun()

            # 입력
            with st.form("career_consult_form"):
                question_text = st.text_area(
                    "메시지",
                    key="career_question_draft",
                    placeholder="진로 고민을 입력하세요. 예: 심리학 전공으로 AI 분야 갈 수 있을까요?",
                    height=96,
                )
                send_col, clear_col = st.columns([4, 1])
                with send_col:
                    submitted_question = st.form_submit_button("보내기", type="primary", use_container_width=True)
                with clear_col:
                    clear_chat = st.form_submit_button("초기화", use_container_width=True)

        if clear_chat:
            st.session_state.career_messages = []
            st.session_state.career_api_notice = ""
            st.rerun()

        if submitted_question and question_text.strip():
            question_text = question_text.strip()
            question_recommended = recommend_experts_for_question(question_text, my_nodes, limit=3)
            expert_ctx = ""
            if question_recommended:
                expert_ctx = "\n".join([
                    f"- {e['display_name']}: {e.get('current_job') or ''}, {e.get('major') or ''}, {e.get('field') or ''}, 활동 노드 {', '.join(e.get('nodes') or [])}"
                    for e in question_recommended
                ])
                system_prompt = system_prompt + f"""

이번 질문과 연결 가능한 실제 전문가 DB:
{expert_ctx}
답변 마지막에 필요하다면 어떤 전문가에게 추가 질문하면 좋을지도 짧게 제안하세요.
"""
            st.session_state.career_messages.append({"role": "user", "content": question_text})
            with st.spinner("분석 중..."):
                if _has_usable_openai_key():
                    try:
                        resp = _openai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                *st.session_state.career_messages
                            ],
                            max_tokens=600,
                            temperature=0.7
                        )
                        answer = resp.choices[0].message.content
                    except Exception:
                        answer = _local_career_answer(question_text, my_nodes, connected_names)
                else:
                    answer = _local_career_answer(question_text, my_nodes, connected_names)
            st.session_state.career_messages.append({"role": "assistant", "content": answer})
            st.rerun()
        elif submitted_question:
            st.error("질문을 입력해 주세요.")

    # ── AI 진로로드맵 ───────────────────────────────────────────────
    with tab_roadmap:
        st.subheader("AI 진로로드맵")
        st.caption("원하는 활동 분야를 입력하면, 그 분야에서 실제로 움직이기 위한 단계별 로드맵을 안내합니다.")

        col1, col2 = st.columns(2)
        with col1:
            start_point = st.text_input("현재 상태", placeholder="예: 중학교 2학년, 영상 제작과 AI에 관심 있음")
        with col2:
            field_options = sorted(df_career["활동 분야"].dropna().unique().tolist()) if not df_career.empty else ["IT·AI·데이터"]
            end_goal = st.selectbox("활동 분야", field_options) if field_options else st.text_input("활동 분야")

        if st.button("로드맵 생성하기", type="primary", use_container_width=True):
            if not start_point.strip():
                st.error("현재 상태를 입력해주세요.")
            else:
                # 관련 전문가 DB 조회
                expert_ctx = ""
                if not df_career.empty:
                    rel = df_career[df_career["활동 분야"] == end_goal][["이름","전공","현재 직업","활동 분야"]].head(3)
                    if not rel.empty:
                        expert_ctx = "\n".join([f"- {r['이름']}: {r['전공']} → {r['현재 직업']} (활동: {r['활동 분야']})" for _, r in rel.iterrows()])

                roadmap_prompt = f"""다음 사람이 '{end_goal}' 활동 분야를 하기 위해 필요한 진로 로드맵을 4단계로 작성해주세요.
현재: {start_point}
목표 활동 분야: {end_goal}
{'관련 전문가 사례:\n' + expert_ctx if expert_ctx else ''}
{'학생 관심 분야: ' + ', '.join(my_nodes) if my_nodes else ''}

형식:
Step 1 — [단계명]: [구체적 행동]
Step 2 — [단계명]: [구체적 행동]
Step 3 — [단계명]: [구체적 행동]
Step 4 — [단계명]: [구체적 행동]

각 단계는 1-2문장으로 간결하게."""

                with st.spinner("로드맵 생성 중..."):
                    if _has_usable_openai_key():
                        try:
                            resp = _openai_client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[
                                    {"role": "system", "content": "당신은 커리어 전문가입니다. 한국어로 답변하세요."},
                                    {"role": "user", "content": roadmap_prompt}
                                ],
                                max_tokens=500,
                                temperature=0.7
                            )
                            roadmap_text = resp.choices[0].message.content
                        except Exception:
                            roadmap_text = _local_roadmap(start_point, end_goal, my_nodes)
                    else:
                        roadmap_text = _local_roadmap(start_point, end_goal, my_nodes)

                st.divider()
                st.subheader(f"{start_point}  →  {end_goal} 활동 분야")

                # 단계별 파싱 및 표시
                steps = [l.strip() for l in roadmap_text.split("\n") if l.strip().startswith("Step")]
                if steps:
                    for s in steps:
                        parts = s.split(":", 1)
                        title = parts[0].strip()
                        desc  = parts[1].strip() if len(parts) > 1 else ""
                        with st.expander(title):
                            st.write(desc)
                    # 타임라인 시각화
                    fig = go.Figure(data=[go.Scatter(
                        x=list(range(1, len(steps)+1)), y=[1]*len(steps),
                        mode='lines+markers+text',
                        text=[s.split("—")[0].strip() for s in steps],
                        textposition="top center",
                        marker=dict(size=20, color="#4A90FF")
                    )])
                    fig.update_layout(height=180, showlegend=False,
                                      xaxis=dict(visible=False), yaxis=dict(visible=False),
                                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write(roadmap_text)

                # 관련 전문가 표시
                if not df_career.empty:
                    rel = df_career[df_career["현재 직업"] == end_goal].head(3)
                    if not rel.empty:
                        st.divider()
                        st.markdown("**이 직업의 전문가**")
                        for _, r in rel.iterrows():
                            st.caption(f"⭐ {r['이름']} — {r['전공']} 전공 · {r['활동 분야']}")


# ══════════════════════════════════════════
# PAGE: 관리자 대시보드
# ══════════════════════════════════════════
elif st.session_state.page == "admin_dashboard":
    if not st.session_state.account or st.session_state.account.get("role") != "admin":
        st.error("관리자만 접근할 수 있는 페이지입니다.")
        st.stop()

    st.title("관리자 대시보드")
    st.caption("설문 응답 분석 및 원데이터 다운로드")
    st.divider()

    conn = get_conn()
    participants_df = pd.read_sql("SELECT * FROM survey_participants", conn)
    questions_df = pd.read_sql("SELECT * FROM survey_questions ORDER BY respondent_type, order_num", conn)
    responses_df = pd.read_sql("SELECT * FROM survey_responses", conn)
    conn.close()

    total = len(participants_df)
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("총 응답자 수", f"{total}명")
    col_m2.metric("응답자 유형", f"{participants_df['respondent_type'].nunique()}종")
    st.divider()

    all_types   = sorted(participants_df["respondent_type"].dropna().unique().tolist())
    tab_labels  = ["전체"] + all_types
    tabs        = st.tabs(tab_labels)

    for i, tab_label in enumerate(tab_labels):
        with tabs[i]:
            if tab_label == "전체":
                u_df = participants_df
                q_df = questions_df
                r_df = responses_df
            else:
                u_df = participants_df[participants_df["respondent_type"] == tab_label]
                q_df = questions_df[questions_df["respondent_type"] == tab_label]
                valid_uids = u_df["id"].tolist()
                valid_qids = q_df["id"].tolist()
                r_df = responses_df[
                    responses_df["participant_id"].isin(valid_uids) &
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
                    index="participant_id", columns="문항",
                    values="response_value", aggfunc="first"
                )
                participant_info = u_df[["id", "name", "gender", "school", "grade", "age", "respondent_type"]].set_index("id")
                result = participant_info.join(pivot)
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


# ══════════════════════════════════════════
# PAGE: 섭외 인사이트
# ══════════════════════════════════════════
elif st.session_state.page == "admin_gap_insights":
    if not st.session_state.account or st.session_state.account.get("role") != "admin":
        st.error("관리자만 접근할 수 있는 페이지입니다.")
        st.stop()

    st.title("섭외 인사이트")
    st.caption("학생 관심 저장 수와 승인 전문가 연결 수를 비교해 전문가 섭외 우선순위를 판단합니다.")
    st.divider()

    init_db()
    conn = get_conn()
    interest_df = pd.read_sql("""
        SELECT node_name AS 관심노드, COUNT(*) AS 저장수
        FROM my_universe
        GROUP BY node_name
    """, conn)
    expert_node_df = pd.read_sql("""
        SELECT en.node_name AS 관심노드, COUNT(*) AS 전문가수
        FROM expert_nodes en
        JOIN expert_profiles ep ON ep.id = en.expert_id
        WHERE ep.is_approved = 1
        GROUP BY en.node_name
    """, conn)
    survey_hint_df = pd.read_sql("""
        SELECT sq.respondent_type, sq.question_text, sr.response_value, sr.created_at
        FROM survey_responses sr
        JOIN survey_questions sq ON sq.id = sr.question_id
        ORDER BY sr.created_at DESC
    """, conn)
    conn.close()

    all_nodes = pd.DataFrame({"관심노드": get_all_universe_nodes()})
    gap_df = all_nodes.merge(interest_df, on="관심노드", how="left").merge(
        expert_node_df, on="관심노드", how="left"
    ).fillna({"저장수": 0, "전문가수": 0})
    gap_df["저장수"] = gap_df["저장수"].astype(int)
    gap_df["전문가수"] = gap_df["전문가수"].astype(int)
    gap_df["부족도"] = gap_df["저장수"] - gap_df["전문가수"]
    gap_df["표시크기"] = gap_df["저장수"].clip(lower=1)

    g1, g2, g3 = st.columns(3)
    g1.metric("전체 저장 노드", f"{gap_df['저장수'].sum():,}개")
    g2.metric("전문가 연결 노드", f"{(gap_df['전문가수'] > 0).sum():,}개")
    g3.metric("전문가 공백 노드", f"{((gap_df['저장수'] > 0) & (gap_df['전문가수'] == 0)).sum():,}개")

    c1, c2 = st.columns([2, 1])
    with c1:
        fig = px.scatter(
            gap_df,
            x="전문가수",
            y="저장수",
            size="표시크기",
            color="부족도",
            hover_name="관심노드",
            color_continuous_scale="RdYlGn_r",
        )
        fig.update_layout(xaxis_title="연결된 전문가 수", yaxis_title="학생 저장 수")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("**우선 섭외 후보**")
        priority = gap_df.sort_values(["부족도", "저장수"], ascending=[False, False]).head(8)
        if priority["저장수"].sum() == 0:
            st.caption("아직 관심 저장 데이터가 부족합니다.")
        else:
            for _, row in priority.iterrows():
                st.write(f"- **{row['관심노드']}**: 저장 {row['저장수']} / 전문가 {row['전문가수']}")

    st.markdown("**노드별 섭외 현황**")
    st.dataframe(
        gap_df.sort_values(["부족도", "저장수"], ascending=[False, False]),
        use_container_width=True,
        hide_index=True,
    )

    if not survey_hint_df.empty:
        st.divider()
        st.markdown("**최근 설문 응답 힌트**")
        st.dataframe(
            survey_hint_df.head(10)[["respondent_type", "question_text", "response_value"]],
            use_container_width=True,
            hide_index=True,
        )


# ══════════════════════════════════════════
# PAGE: DB 관리
# ══════════════════════════════════════════
elif st.session_state.page == "admin_db_viewer":
    if not st.session_state.account or st.session_state.account.get("role") != "admin":
        st.error("관리자만 접근할 수 있는 페이지입니다.")
        st.stop()

    st.title("DB 관리")
    st.caption("SQLite 데이터베이스의 테이블 내용을 확인하고 CSV로 내려받을 수 있습니다.")
    st.divider()

    init_accounts()
    init_db()

    st.divider()

    conn = get_conn()
    table_rows = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()
    table_names = [r[0] for r in table_rows]

    if not table_names:
        conn.close()
        st.info("표시할 테이블이 없습니다.")
        st.stop()

    selected_table = st.selectbox("테이블 선택", table_names)
    table_info = conn.execute(f'PRAGMA table_info("{selected_table}")').fetchall()
    row_count = conn.execute(f'SELECT COUNT(*) FROM "{selected_table}"').fetchone()[0]

    col_a, col_b = st.columns(2)
    col_a.metric("선택 테이블", selected_table)
    col_b.metric("행 수", f"{row_count:,}")

    with st.expander("컬럼 정보"):
        col_info_df = pd.DataFrame(
            table_info,
            columns=["cid", "name", "type", "notnull", "default_value", "pk"]
        )
        st.dataframe(col_info_df, use_container_width=True, hide_index=True)

    page_size = st.selectbox("표시 개수", [50, 100, 300, 1000], index=1)
    page_count = max((row_count - 1) // page_size + 1, 1)
    page_no = st.number_input("페이지", min_value=1, max_value=page_count, value=1, step=1)
    offset = (page_no - 1) * page_size

    df_table = pd.read_sql(
        f'SELECT * FROM "{selected_table}" LIMIT ? OFFSET ?',
        conn,
        params=(page_size, offset)
    )
    df_all = pd.read_sql(f'SELECT * FROM "{selected_table}"', conn)
    conn.close()

    st.dataframe(df_table, use_container_width=True, hide_index=True)

    csv = df_all.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        "CSV 다운로드",
        data=csv,
        file_name=f"{selected_table}.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ══════════════════════════════════════════
# PAGE: 전문가 승인
# ══════════════════════════════════════════
elif st.session_state.page == "admin_expert_approval":
    if not st.session_state.account or st.session_state.account.get("role") != "admin":
        st.error("관리자만 접근할 수 있는 페이지입니다.")
        st.stop()

    st.title("전문가 승인 관리")

    tab_approval, tab_nodes = st.tabs(["전문가 승인", "활동 분야 관리"])

    with tab_nodes:
        st.subheader("활동 분야 목록 관리")
        st.caption("여기서 추가한 분야는 전문가·학생 선택 목록에 즉시 반영됩니다.")

        all_nodes_now = get_all_universe_nodes()
        custom_nodes_db = [r for r in all_nodes_now if r not in UNIVERSE_NODES]

        col_a, col_b = st.columns([3, 2])
        with col_a:
            with st.form("add_node_form"):
                new_node_name = st.text_input("새 활동 분야 이름", placeholder="예: 디지털트윈, 메타버스교육, 해양생물학")
                if st.form_submit_button("추가", type="primary", use_container_width=True):
                    val = new_node_name.strip()
                    if not val:
                        st.error("분야 이름을 입력해 주세요.")
                    elif val in all_nodes_now:
                        st.warning("이미 존재하는 분야입니다.")
                    elif add_universe_node(val):
                        st.success(f"'{val}' 추가 완료")
                        st.rerun()

        with col_b:
            st.markdown("**관리자 추가 분야**")
            if not custom_nodes_db:
                st.caption("아직 추가된 분야가 없습니다.")
            else:
                for node in custom_nodes_db:
                    c1, c2 = st.columns([3, 1])
                    c1.write(node)
                    if c2.button("삭제", key=f"del_node_{node}", use_container_width=True):
                        delete_universe_node(node)
                        st.rerun()

        st.divider()

        # ── 전문가 승인 요청 내역 ──────────────────────────
        st.subheader("활동 분야 추가 요청")
        all_node_reqs = get_node_requests()
        pending_reqs  = [r for r in all_node_reqs if r['status'] == 'pending']
        done_reqs     = [r for r in all_node_reqs if r['status'] != 'pending']

        if not all_node_reqs:
            st.info("아직 추가 요청이 없습니다.")
        else:
            if pending_reqs:
                st.markdown("**대기 중**")
                for req in pending_reqs:
                    with st.container(border=True):
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.markdown(f"**{req['node_name']}**")
                            st.caption(f"요청자: {req['expert_name']}  ·  {req['requested_at'][:10]}")
                        with c2:
                            if st.button("✅ 승인", key=f"tab_nr_approve_{req['id']}", use_container_width=True, type="primary"):
                                handle_node_request(req['id'], approve=True)
                                st.rerun()
                            if st.button("❌ 거절", key=f"tab_nr_reject_{req['id']}", use_container_width=True):
                                handle_node_request(req['id'], approve=False)
                                st.rerun()

            if done_reqs:
                with st.expander(f"처리 완료 내역 ({len(done_reqs)}건)"):
                    for req in done_reqs:
                        badge = "✅ 승인됨" if req['status'] == 'approved' else "❌ 거절됨"
                        st.caption(f"{badge}  **{req['node_name']}**  —  {req['expert_name']}  ·  {req['requested_at'][:10]}")

        st.divider()
        with st.expander(f"기본 분야 전체 보기 ({len(UNIVERSE_NODES)}개)"):
            st.write(" · ".join(UNIVERSE_NODES))

    with tab_approval:
        st.caption("가입한 전문가 계정을 검토하고 승인 또는 거절합니다.")
        st.divider()

        conn = get_conn()
        experts = conn.execute("""
            SELECT ep.id, a.id AS account_id, a.login_id,
                   ep.display_name, ep.title, ep.organization,
                   ep.field, ep.description, ep.contact_email,
                   ep.is_approved, ep.created_at
            FROM expert_profiles ep
            JOIN accounts a ON a.login_id = ep.login_id
            ORDER BY ep.is_approved ASC, ep.created_at DESC
        """).fetchall()
        conn.close()

        cols = ['id','account_id','login_id','display_name','title','organization',
                'field','description','contact_email','is_approved','created_at']

        pending   = [dict(zip(cols, r)) for r in experts if r[9] == 0]
        approved  = [dict(zip(cols, r)) for r in experts if r[9] == 1]

        m1, m2, m3 = st.columns(3)
        m1.metric("전체 전문가", f"{len(experts)}명")
        m2.metric("승인 대기", f"{len(pending)}명")
        m3.metric("승인 완료", f"{len(approved)}명")
        st.divider()

        # ── 승인 대기 목록 ─────────────────────────────────
        st.subheader("승인 대기")
        if not pending:
            st.info("대기 중인 전문가가 없습니다.")
        else:
            for ep in pending:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**{ep['display_name']}** ({ep['login_id']})")
                        st.caption(f"{ep['title']} · {ep['organization']} · {ep['field']}")
                        if ep['description']:
                            st.write(ep['description'])
                        if ep['contact_email']:
                            st.caption(f"✉ {ep['contact_email']}")
                        conn = get_conn()
                        nodes_list = conn.execute(
                            "SELECT node_name FROM expert_nodes WHERE expert_id=?", (ep['id'],)
                        ).fetchall()
                        conn.close()
                        if nodes_list:
                            st.caption("활동분야: " + ", ".join(r[0] for r in nodes_list))
                        st.caption(f"가입일: {ep['created_at'][:10]}")
                    with c2:
                        if st.button("✅ 승인", key=f"approve_{ep['id']}", use_container_width=True, type="primary"):
                            conn = get_conn()
                            conn.execute("UPDATE expert_profiles SET is_approved=1 WHERE id=?", (ep['id'],))
                            conn.commit()
                            conn.close()
                            st.success(f"{ep['display_name']} 승인 완료")
                            st.rerun()
                        if st.button("❌ 거절", key=f"reject_{ep['id']}", use_container_width=True):
                            conn = get_conn()
                            conn.execute("DELETE FROM expert_nodes WHERE expert_id=?", (ep['id'],))
                            conn.execute("DELETE FROM expert_profiles WHERE id=?", (ep['id'],))
                            conn.execute("UPDATE accounts SET role='student' WHERE id=?", (ep['account_id'],))
                            conn.commit()
                            conn.close()
                            st.warning(f"{ep['display_name']} 거절 — 학생으로 전환됨")
                            st.rerun()

        # ── 활동 분야 추가 요청 ────────────────────────────
        st.divider()
        st.subheader("활동 분야 추가 요청")
        pending_node_reqs = get_node_requests(status='pending')
        if not pending_node_reqs:
            st.info("대기 중인 분야 추가 요청이 없습니다.")
        else:
            for req in pending_node_reqs:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**{req['node_name']}**")
                        st.caption(f"요청자: {req['expert_name']}  ·  요청일: {req['requested_at'][:10]}")
                    with c2:
                        if st.button("✅ 승인", key=f"nr_approve_{req['id']}", use_container_width=True, type="primary"):
                            handle_node_request(req['id'], approve=True)
                            st.success(f"'{req['node_name']}' 승인 완료")
                            st.rerun()
                        if st.button("❌ 거절", key=f"nr_reject_{req['id']}", use_container_width=True):
                            handle_node_request(req['id'], approve=False)
                            st.warning(f"'{req['node_name']}' 거절됨")
                            st.rerun()

        # ── 승인 완료 목록 ─────────────────────────────────
        st.divider()
        st.subheader("승인 완료")
        if not approved:
            st.info("승인된 전문가가 없습니다.")
        else:
            for ep in approved:
                with st.container(border=True):
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        st.markdown(f"**{ep['display_name']}** ({ep['login_id']})")
                        st.caption(f"{ep['title']} · {ep['organization']} · {ep['field']}")
                        conn = get_conn()
                        nodes_list = conn.execute(
                            "SELECT node_name FROM expert_nodes WHERE expert_id=?", (ep['id'],)
                        ).fetchall()
                        conn.close()
                        if nodes_list:
                            st.caption("활동분야: " + ", ".join(r[0] for r in nodes_list))
                    with c2:
                        if st.button("승인 취소", key=f"revoke_{ep['id']}", use_container_width=True):
                            conn = get_conn()
                            conn.execute("UPDATE expert_profiles SET is_approved=0 WHERE id=?", (ep['id'],))
                            conn.commit()
                            conn.close()
                            st.rerun()


# ══════════════════════════════════════════
# PAGE: 내 프로필
# ══════════════════════════════════════════
elif st.session_state.page == "profile":
    account = st.session_state.get("account")
    if not account:
        st.error("로그인이 필요합니다.")
        st.stop()

    role = account["role"]

    # ── 토큰 현황 (공통) ──────────────────────────────────
    balance  = get_token_balance(account["account_id"])
    history  = get_token_history(account["account_id"])
    st.markdown(
        f"""<div style='background:linear-gradient(135deg,#1a3a6e,#0f2244);
            border:1px solid rgba(255,215,0,0.55);border-radius:10px;
            padding:1.2rem 1.8rem;margin-bottom:1.2rem;display:flex;
            align-items:center;gap:1.5rem;'>
            <div>
                <div style='color:rgba(255,215,0,0.75);font-size:0.8rem;
                            font-weight:600;letter-spacing:1px;text-transform:uppercase;'>
                    보유 토큰</div>
                <div style='color:#FFD700;font-size:2rem;font-weight:800;
                            letter-spacing:-1px;'>{balance:,} T</div>
            </div>
        </div>""",
        unsafe_allow_html=True
    )
    with st.expander("토큰 사용/적립 내역"):
        if not history:
            st.caption("내역이 없습니다.")
        else:
            for amount, reason, created_at in history:
                sign  = "+" if amount > 0 else ""
                color = "#4ade80" if amount > 0 else "#f87171"
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;"
                    f"padding:6px 0;border-bottom:1px solid rgba(165,195,255,0.30);'>"
                    f"<span style='color:#c0d2f5;'>{reason}</span>"
                    f"<span style='color:{color};font-weight:700;'>{sign}{amount:,} T</span>"
                    f"<span style='color:#AFC2EF;font-size:0.8rem;'>{created_at[:10]}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
    st.divider()

    # ── 전문가 프로필 ─────────────────────────────────────
    if role == "expert":
        st.title("내 프로필 — 전문가")

        ep = get_expert_profile(account["account_id"])
        if not ep:
            st.warning("전문가 프로필 정보가 없습니다. 관리자에게 문의하세요.")
            st.stop()

        # 승인 상태 배지
        if ep["is_approved"]:
            st.success("승인 완료 — 3D 유니버스에 표시 중입니다.")
        else:
            st.warning("승인 대기 중 — 관리자 검토 후 유니버스에 표시됩니다.")

        st.divider()

        # ── 기본 정보 ──────────────────────────────────────
        st.subheader("기본 정보")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**닉네임** : {ep['display_name']}")
            st.markdown(f"**직함** : {ep['title'] or '—'}")
            st.markdown(f"**소속** : {ep['organization'] or '—'}")
        with c2:
            st.markdown(f"**전공/학과** : {ep.get('major') or '—'}")
            st.markdown(f"**대분류 분야** : {ep['field'] or '—'}")
            st.markdown(f"**연락처** : {ep['contact_email'] or '—'}")
        if ep["description"]:
            st.markdown(f"**소개** : {ep['description']}")

        with st.expander("닉네임 변경"):
            with st.form("expert_nickname_edit"):
                new_nick = st.text_input("새 닉네임", value=ep["display_name"], max_chars=10,
                                         help="한글과 숫자만, 띄어쓰기 없이 최대 10자")
                if st.form_submit_button("저장", type="primary", use_container_width=True):
                    new_nick = new_nick.strip()
                    if not re.fullmatch(r"[가-힣0-9]{1,10}", new_nick):
                        st.error("한글과 숫자만, 띄어쓰기 없이 최대 10자입니다.")
                    else:
                        update_display_name(account["account_id"], "expert", new_nick)
                        st.session_state.account["display_name"] = new_nick
                        st.success("닉네임이 변경되었습니다.")
                        st.rerun()

        st.divider()

        # ── 활동 분야 (수정 가능) ─────────────────────
        st.subheader("활동 분야")
        current_nodes = get_expert_nodes(ep["id"])

        st.caption(f"현재 활동 분야 ({len(current_nodes)}개): " +
                   (", ".join(f"**{n}**" for n in current_nodes) if current_nodes else "없음"))
        st.info("활동 분야를 수정하면 관리자 재승인이 필요합니다. 활동 분야는 가입 후 이메일을 통해 인증서류를 요청합니다.")

        with st.form("expert_node_edit"):
            expert_node_options = list(dict.fromkeys(get_all_universe_nodes() + current_nodes))
            selected_nodes = st.multiselect(
                "활동 분야 선택",
                expert_node_options,
                default=current_nodes,
                help="직업명이 아닌 관심사·전문 주제를 선택하세요."
            )
            if st.form_submit_button("활동 분야 수정 저장", type="primary", use_container_width=True):
                if not selected_nodes:
                    st.error("최소 1개 이상 선택해야 합니다.")
                else:
                    update_expert_nodes(ep["id"], selected_nodes)
                    st.success("저장 완료! 관리자 승인 후 유니버스에 반영됩니다.")
                    st.rerun()

        st.divider()

        # ── 활동 분야 추가 요청 ───────────────────────
        st.subheader("활동 분야 추가 요청")
        st.caption("목록에 없는 분야를 요청하면 관리자 승인 후 내 활동 분야에 추가됩니다.")

        pending_requests = [r for r in get_node_requests() if r['expert_profile_id'] == ep['id'] and r['status'] == 'pending']
        if pending_requests:
            st.info("대기 중인 요청: " + ", ".join(f"**{r['node_name']}**" for r in pending_requests))

        with st.form("node_request_form"):
            requested_node = st.text_input(
                "추가할 분야 이름",
                placeholder="예: 데이터저널리즘, 과학일러스트, 양자암호학"
            )
            if st.form_submit_button("추가 요청 보내기", use_container_width=True):
                node_val = requested_node.strip()
                if not node_val:
                    st.error("분야 이름을 입력해 주세요.")
                elif node_val in current_nodes:
                    st.warning("이미 등록된 활동 분야입니다.")
                elif request_node(ep["id"], node_val):
                    st.success(f"'{node_val}' 추가 요청이 전송되었습니다. 관리자 승인 후 반영됩니다.")
                    st.rerun()
                else:
                    st.warning("이미 동일한 요청이 대기 중입니다.")

    # ── 학생 프로필 ─────────────────────────────────
    elif role == "student":
        st.title("내 프로필")

        # 프로필 진입 시 새 답변 읽음 처리
        mark_answers_read(account["login_id"])

        up = get_student_profile(account["account_id"])

        st.divider()
        st.subheader("기본 정보")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**닉네임** : {up.get('display_name') or account.get('display_name') or '—'}")
            st.markdown(f"**로그인 ID** : `{account['login_id']}`")
        with c2:
            st.markdown(f"**학교급** : {up.get('school_level') or '—'}")
            st.markdown(f"**학교** : {up.get('school_name') or '—'}")
            st.markdown(f"**학년** : {up.get('grade') or '—'}")

        with st.expander("닉네임 변경"):
            with st.form("student_nickname_edit"):
                cur_nick = up.get("display_name") or account.get("display_name") or ""
                new_nick = st.text_input("새 닉네임", value=cur_nick, max_chars=10,
                                         help="한글과 숫자만, 띄어쓰기 없이 최대 10자")
                if st.form_submit_button("저장", type="primary", use_container_width=True):
                    new_nick = new_nick.strip()
                    if not re.fullmatch(r"[가-힣0-9]{1,10}", new_nick):
                        st.error("한글과 숫자만, 띄어쓰기 없이 최대 10자입니다.")
                    else:
                        update_display_name(account["account_id"], "student", new_nick)
                        st.session_state.account["display_name"] = new_nick
                        st.success("닉네임이 변경되었습니다.")
                        st.rerun()

        st.divider()

        # ── 마이유니버스 ────────────────────────────────────
        st.subheader("✨ 나만의 우주")
        saved_nodes = load_my_universe(account)

        if not saved_nodes:
            st.caption("아직 선택한 노드가 없습니다. 3D 탐색기에서 관심 노드를 저장해보세요.")
        else:
            st.caption(f"저장된 관심 노드 {len(saved_nodes)}개")

            # 노드 카드 그리드
            cols = st.columns(3)
            for i, node in enumerate(saved_nodes):
                with cols[i % 3]:
                    st.markdown(
                        f"""<div style='background:rgba(74,144,255,0.1);
                            border:1px solid rgba(150,190,255,0.42);
                            border-radius:8px;padding:10px 14px;
                            margin-bottom:8px;text-align:center;
                            color:#C8DCFF;font-weight:600;'>
                            🔵 {node}</div>""",
                        unsafe_allow_html=True
                    )

            st.divider()

            # 수정 폼
            with st.form("student_universe_edit"):
                universe_edit_options = list(dict.fromkeys(get_all_universe_nodes() + saved_nodes))
                updated = st.multiselect(
                    "관심 노드 수정",
                    universe_edit_options,
                    default=saved_nodes
                )
                if st.form_submit_button("저장", use_container_width=True, type="primary"):
                    save_my_universe(account, updated)
                    st.success("저장되었습니다.")
                    st.rerun()

        # ── 내가 남긴 질문 & 답변 ──────────────────────────
        st.divider()
        st.subheader("내 질문")
        conn = get_conn()
        my_qs = conn.execute("""
            SELECT q.id, ep.display_name, q.question_text, q.is_public,
                   q.created_at, qa.answer_text, qa.created_at as answered_at
            FROM questions q
            JOIN expert_profiles ep ON ep.id = q.to_expert_id
            LEFT JOIN question_answers qa ON qa.question_id = q.id
            WHERE q.from_login_id = ?
            ORDER BY q.created_at DESC
        """, (account["login_id"],)).fetchall()
        conn.close()

        if not my_qs:
            st.caption("아직 남긴 질문이 없습니다.")
        else:
            for qid, expert_name, q_text, is_pub, created, ans_text, ans_at in my_qs:
                with st.container(border=True):
                    pub_badge = "🌐 공개" if is_pub else "🔒 비공개"
                    st.markdown(f"{pub_badge} · **{expert_name}** · {created[:10]}")
                    st.markdown(f"> {q_text}")
                    if ans_text:
                        st.success(f"**답변 ({ans_at[:10]}):** {ans_text}")
                    else:
                        st.caption("아직 답변이 없습니다.")

    # ── 전문가: 받은 질문 목록도 표시 ────────────────────
    if role == "expert" and ep:
        st.divider()
        st.subheader("받은 질문")
        my_questions = get_questions_for_expert(
            ep["id"],
            viewer_login_id=account["login_id"],
            viewer_role=account["role"]
        )
        if not my_questions:
            st.caption("아직 받은 질문이 없습니다.")
        for q in my_questions:
            with st.container(border=True):
                badge = "🔒 비공개" if not q["is_public"] else "🌐 공개"
                st.markdown(f"{badge} · **{q['asker_nickname']}** · {q['created_at'][:10]}")
                st.markdown(f"> {q['question_text']}")
                if q["answer_text"]:
                    st.success(f"**답변:** {q['answer_text']}")
                else:
                    with st.form(f"answer_form_{q['id']}"):
                        ans = st.text_area("답변 작성", placeholder="답변을 입력하세요.", label_visibility="collapsed")
                        if st.form_submit_button("답변 등록", type="primary"):
                            if ans.strip():
                                post_answer(q["id"], ans.strip(), account["account_id"])
                                st.success("답변이 등록되었습니다.")
                                st.rerun()
                            else:
                                st.error("답변 내용을 입력하세요.")

    # ── 관리자 ────────────────────────────────────────────
    elif role == "admin":
        st.title("내 프로필 — 관리자")
        st.info(f"아이디: **{account['login_id']}** · 역할: 관리자")
        st.caption("관리자 계정은 별도 프로필이 없습니다.")


# ══════════════════════════════════════════
# PAGE: Contact Us
# ══════════════════════════════════════════
elif st.session_state.page == "contact":
    st.title("Contact Us")
    st.caption("Future Universe에 대한 문의, 제안, 협업 이야기를 남겨주세요.")

    profile = CONTACT_PROFILE
    account = st.session_state.get("account")

    st.markdown(f"""
    <div class="cta-banner">
        <div class="cta-title">{profile["name"]}</div>
        <p class="cta-desc">{profile["role"]}</p>
        <p class="cta-desc" style="margin-bottom:0;">{profile["message"]}</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    col_about, col_contact = st.columns([1.2, 1], gap="large")

    with col_about:
        with st.container(border=True):
            st.subheader("만든 사람")
            st.markdown(f"**이름**: {profile['name']}")
            st.markdown(f"**역할**: {profile['role']}")
            st.markdown("**관심사**: 진로교육, 데이터 기반 탐색, 3D 인터랙션, 전문가 연결")
            st.markdown("**목표**: 학생이 막연한 직업 이름이 아니라 실제 사람과 경험을 통해 진로를 탐색하게 만드는 것")

    with col_contact:
        with st.container(border=True):
            st.subheader("문의")
            st.markdown(f"**이메일**: `{profile['email']}`")
            st.markdown("**문의 주제**: 전문가 등록, 학교 활용, 기능 제안, 오류 제보")
            st.caption("실제 운영 이메일이 정해지면 위 주소만 바꾸면 됩니다.")

    st.divider()
    st.subheader("빠른 문의")
    with st.form("contact_form"):
        default_name = (account.get("display_name") or get_account_display_name(account["account_id"], account["login_id"])) if account else ""
        contact_name = st.text_input("닉네임", value=default_name, placeholder="웹 안에서 표시될 이름")
        contact_email = st.text_input("연락처 또는 이메일", placeholder="답변 받을 이메일을 입력하세요")
        contact_topic = st.selectbox("문의 유형", ["기능 제안", "오류 제보", "전문가 등록", "학교/기관 활용", "기타"])
        contact_message = st.text_area("내용", placeholder="문의 내용을 적어주세요.")
        submitted = st.form_submit_button("문의 내용 확인", type="primary", use_container_width=True)

    if submitted:
        if not contact_name.strip() or not contact_message.strip():
            st.error("이름과 문의 내용을 입력해 주세요.")
        else:
            st.success("문의 내용이 확인되었습니다. 실제 발송 기능은 이메일/DB 저장 방식이 정해지면 연결할 수 있습니다.")
            with st.expander("작성 내용 보기", expanded=True):
                st.markdown(f"**이름**: {contact_name}")
                st.markdown(f"**연락처/이메일**: {contact_email or '미입력'}")
                st.markdown(f"**문의 유형**: {contact_topic}")
                st.markdown(f"**내용**: {contact_message}")


# ══════════════════════════════════════════
# PAGE: 질문하기
# ══════════════════════════════════════════
elif st.session_state.page == "questions":
    st.title("전문가 Q&A")
    st.caption("공개 답변을 탐색하고, 전문가에게 질문하고, 내가 남긴 질문의 상태를 확인합니다.")

    account = st.session_state.get("account")
    if not account:
        st.warning("전문가 Q&A는 로그인 후 이용할 수 있습니다.")
        st.caption("왼쪽 사이드바에서 로그인 또는 회원가입을 진행해 주세요.")
        st.stop()

    experts = search_experts()

    if not experts:
        st.info("아직 승인된 전문가가 없습니다.")
    else:
        def expert_label(e):
            parts = [e['display_name']]
            if e.get('title'):
                parts.append(e['title'])
            if e.get('organization'):
                parts.append(e['organization'])
            return " · ".join(parts)

        expert_map = {expert_label(e): e for e in experts}
        expert_labels = list(expert_map.keys())

        conn = get_conn()
        board_rows = conn.execute("""
            SELECT q.id, q.question_title, q.question_text, q.created_at, q.is_public,
                   COALESCE(NULLIF(sp.display_name, ''), NULLIF(ep_asker.display_name, ''), a.login_id) AS asker_nickname,
                   ep.id AS expert_id, ep.display_name AS expert_name,
                   ep.current_job, ep.field,
                   qa.answer_text, qa.created_at AS answered_at
            FROM questions q
            JOIN accounts a ON a.login_id = q.from_login_id
            LEFT JOIN student_profiles sp ON sp.login_id = a.login_id
            LEFT JOIN expert_profiles ep_asker ON ep_asker.login_id = a.login_id
            JOIN expert_profiles ep ON ep.id = q.to_expert_id
            LEFT JOIN question_answers qa ON qa.question_id = q.id
            WHERE q.is_public = 1
            ORDER BY q.created_at DESC
        """).fetchall()
        conn.close()
        board_cols = [
            "id", "question_title", "question_text", "created_at", "is_public", "asker_nickname",
            "expert_id", "expert_name", "current_job", "field", "answer_text", "answered_at"
        ]
        board_df = pd.DataFrame([dict(zip(board_cols, r)) for r in board_rows], columns=board_cols)

        success_message = st.session_state.pop("qa_submit_success", None)
        if success_message:
            question_submit_dialog(success_message)

        qa_tabs = ["공개 Q&A", "질문하기", "내 질문"]
        active_tab = st.session_state.get("qa_active_tab", "공개 Q&A")
        if active_tab not in qa_tabs:
            active_tab = "공개 Q&A"
        selected_qa_tab = st.radio(
            "Q&A 보기",
            qa_tabs,
            index=qa_tabs.index(active_tab),
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state.qa_active_tab = selected_qa_tab

        if selected_qa_tab == "공개 Q&A":
            st.subheader("공개 Q&A")
            filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
            with filter_col1:
                selected_filter = st.selectbox("전문가 필터", ["전체"] + expert_labels, key="qa_expert_filter")
            with filter_col2:
                status_filter = st.selectbox("답변 상태", ["전체", "답변 완료", "미답변"], key="qa_status_filter")
            with filter_col3:
                keyword = st.text_input("검색", placeholder="질문 검색", key="qa_keyword")

            filtered_df = board_df.copy()
            if not filtered_df.empty:
                if selected_filter != "전체":
                    filtered_df = filtered_df[filtered_df["expert_id"] == expert_map[selected_filter]["id"]]
                if status_filter == "답변 완료":
                    filtered_df = filtered_df[filtered_df["answer_text"].notna()]
                elif status_filter == "미답변":
                    filtered_df = filtered_df[filtered_df["answer_text"].isna()]
                if keyword.strip():
                    kw = keyword.strip()
                    filtered_df = filtered_df[
                        filtered_df["question_title"].str.contains(kw, case=False, na=False)
                        | filtered_df["question_text"].str.contains(kw, case=False, na=False)
                        | filtered_df["expert_name"].str.contains(kw, case=False, na=False)
                    ]

            answered_count = int(filtered_df["answer_text"].notna().sum()) if not filtered_df.empty else 0
            m1, m2, m3 = st.columns(3)
            m1.metric("공개 질문", f"{len(filtered_df):,}개")
            m2.metric("답변 완료", f"{answered_count:,}개")
            m3.metric("미답변", f"{max(len(filtered_df) - answered_count, 0):,}개")

            if filtered_df.empty:
                st.info("조건에 맞는 공개 질문이 없습니다.")
            else:
                render_qa_toggle_board(filtered_df, "qa_public", mine=False)

        if selected_qa_tab == "질문하기":
            st.subheader("질문하기")
            prefill_expert_id = st.session_state.pop("qa_prefill_expert_id", None)
            if prefill_expert_id:
                for _label, _expert in expert_map.items():
                    if _expert.get("id") == prefill_expert_id:
                        st.session_state.qa_write_expert = _label
                        break

            if not account:
                st.warning("질문을 남기려면 로그인이 필요합니다.")
            else:
                balance = get_token_balance(account["login_id"])
                st.markdown(f"**보유 토큰**  {balance:,} T")
                selected_label = st.selectbox("질문할 전문가", expert_labels, key="qa_write_expert")
                selected_expert = expert_map[selected_label]

                if balance < 1000:
                    st.error("토큰이 부족합니다. 질문을 등록할 수 없습니다.")
                else:
                    with st.form("question_form"):
                        q_title = st.text_input("질문 제목", placeholder="예: AI 연구원이 되려면 수학을 잘해야 하나요?")
                        q_text = st.text_area("질문 내용", placeholder="상황, 궁금한 점, 원하는 조언을 자세히 작성하세요.")
                        submitted = st.form_submit_button("질문 등록", type="primary", use_container_width=True)

                    if submitted:
                        if not q_title.strip():
                            st.error("질문 제목을 입력하세요.")
                        elif not q_text.strip():
                            st.error("질문 내용을 입력하세요.")
                        else:
                            ok = post_question(
                                from_login_id=account["login_id"],
                                to_expert_id=selected_expert["id"],
                                title=q_title.strip(),
                                text=q_text.strip(),
                                is_public=True
                            )
                            if ok:
                                st.session_state.qa_active_tab = "내 질문"
                                st.session_state.qa_submit_success = "질문이 등록되었습니다! 전문가의 답변을 기다려주세요."
                                st.rerun()
                            else:
                                st.error("토큰이 부족합니다.")

        if selected_qa_tab == "내 질문":
            st.subheader("내 질문")
            if not account:
                st.warning("내 질문을 확인하려면 로그인이 필요합니다.")
            else:
                conn = get_conn()
                my_rows = conn.execute("""
                    SELECT q.id, q.question_title, q.question_text, q.is_public,
                           q.created_at, ep.display_name AS expert_name,
                           ep.current_job, qa.answer_text, qa.created_at AS answered_at
                    FROM questions q
                    JOIN expert_profiles ep ON ep.id = q.to_expert_id
                    LEFT JOIN question_answers qa ON qa.question_id = q.id
                    WHERE q.from_login_id = ?
                    ORDER BY q.created_at DESC
                """, (account["login_id"],)).fetchall()
                conn.close()
                my_cols = ["id", "question_title", "question_text", "is_public", "created_at",
                           "expert_name", "current_job", "answer_text", "answered_at"]
                my_df = pd.DataFrame([dict(zip(my_cols, r)) for r in my_rows], columns=my_cols)

                if my_df.empty:
                    st.info("아직 남긴 질문이 없습니다.")
                else:
                    done = int(my_df["answer_text"].notna().sum())
                    wait = len(my_df) - done
                    c1, c2, c3 = st.columns(3)
                    c1.metric("전체 질문", f"{len(my_df):,}개")
                    c2.metric("답변 완료", f"{done:,}개")
                    c3.metric("답변 대기", f"{wait:,}개")

                    render_qa_toggle_board(my_df, "qa_my", mine=True)
