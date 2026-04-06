import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import hashlib
import json

# ══════════════════════════════════════════
# 페이지 설정
# ══════════════════════════════════════════
st.set_page_config(
    page_title="My Investment Hub",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════
# 파스텔 CSS 디자인
# ══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

/* 전체 배경 - 따뜻한 아이보리 */
[data-testid="stAppViewContainer"] {
    background: #faf8f5;
    color: #3d3530;
}
[data-testid="stSidebar"] {
    background: #f5f0ea;
    border-right: 1px solid #e8e0d5;
}
[data-testid="stSidebar"] * { color: #5a4f47 !important; }

/* 폰트 */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 {
    font-family: 'DM Serif Display', serif !important;
    color: #3d3530 !important;
    letter-spacing: -0.3px;
}
h1 { font-size: 2rem !important; }
h2 { font-size: 1.4rem !important; }

/* 메트릭 카드 */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #ece6de;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(180,160,140,0.08);
}
[data-testid="stMetricLabel"] {
    color: #9c8878 !important;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    color: #3d3530 !important;
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.7rem !important;
}
[data-testid="stMetricDelta"] { font-size: 0.85rem !important; }

/* 입력 필드 */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: white !important;
    border: 1.5px solid #e0d6cc !important;
    color: #3d3530 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #f4a58a !important;
    box-shadow: 0 0 0 3px rgba(244,165,138,0.15) !important;
}

/* 버튼 */
[data-testid="stFormSubmitButton"] button,
.stButton button {
    background: linear-gradient(135deg, #f4a58a, #e8856a) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    padding: 0.5rem 1.5rem !important;
    box-shadow: 0 2px 8px rgba(244,165,138,0.35) !important;
    transition: all 0.2s !important;
}
[data-testid="stFormSubmitButton"] button:hover,
.stButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(244,165,138,0.45) !important;
}

/* 구분선 */
hr { border-color: #ece6de !important; }

/* 셀렉트박스 */
[data-testid="stSelectbox"] > div {
    background: white !important;
    border: 1.5px solid #e0d6cc !important;
    border-radius: 10px !important;
}

/* 알림 메시지 */
[data-testid="stSuccess"] {
    background: #f0faf4 !important;
    border-left: 4px solid #6dbf8a !important;
    border-radius: 10px;
    color: #2d6b45 !important;
}
[data-testid="stInfo"] {
    background: #f0f6ff !important;
    border-left: 4px solid #7ab8f5 !important;
    border-radius: 10px;
    color: #2a5490 !important;
}
[data-testid="stWarning"] {
    background: #fffbf0 !important;
    border-left: 4px solid #f5c842 !important;
    border-radius: 10px;
    color: #7a5f10 !important;
}
[data-testid="stError"] {
    background: #fff5f5 !important;
    border-left: 4px solid #f5877a !important;
    border-radius: 10px;
    color: #8b2a22 !important;
}

/* 데이터프레임 */
[data-testid="stDataFrame"] {
    border: 1px solid #ece6de;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(180,160,140,0.08);
}

/* 사이드바 타이틀 */
.sidebar-logo {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #e8856a !important;
    letter-spacing: -0.3px;
    padding: 4px 0 8px 0;
}

/* 원칙 카드 */
.p-card {
    background: white;
    border: 1px solid #ece6de;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 10px;
    box-shadow: 0 2px 6px rgba(180,160,140,0.07);
}
.p-pass { border-left: 4px solid #6dbf8a; }
.p-fail { border-left: 4px solid #f5877a; }
.p-warn { border-left: 4px solid #f5c842; }

.tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 700;
    margin-left: 8px;
    letter-spacing: 0.5px;
}
.tag-pass { background: #edfaf2; color: #2d8a52; border: 1px solid #a8ddb8; }
.tag-fail { background: #fff0ef; color: #c0392b; border: 1px solid #f5b3ae; }
.tag-warn { background: #fefce8; color: #927a10; border: 1px solid #f0d87a; }

/* 페이지 상단 여백 */
.block-container { padding-top: 2rem !important; }

/* 라디오 버튼 */
[data-testid="stRadio"] label { font-size: 0.9rem; }

/* 익스팬더 */
[data-testid="stExpander"] {
    background: white;
    border: 1px solid #ece6de !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# 데이터 경로 & 유틸
# ══════════════════════════════════════════
JOURNAL_COLS = ['매수일','티커','매수이유','매수단가','매수갯수','목표가','예상투자기간']
ANALYSIS_COLS = ['분석일','티커','기업명','ROCE','매출성장률','FCF여부','부채비율DE',
                 '영업이익률','이평선이격','주주환원율','채권금리','메모','종합점수']

def get_hash(pw):   return hashlib.sha256(pw.encode()).hexdigest()[:16]
def journal_path(h): return f"data/journal_{h}.csv"
def analysis_path(h): return f"data/analysis_{h}.csv"

def load_csv(path, cols):
    if os.path.exists(path):
        df = pd.read_csv(path)
        for c in cols:
            if c not in df.columns: df[c] = ""
        return df[cols]
    return pd.DataFrame(columns=cols)

def save_csv(df, path):
    os.makedirs("data", exist_ok=True)
    df.to_csv(path, index=False, encoding='utf-8-sig')

# ══════════════════════════════════════════
# 로그인
# ══════════════════════════════════════════
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.4, 1])
    with col_m:
        st.markdown("""
        <div style="background:white;border:1px solid #ece6de;border-radius:20px;
                    padding:44px 40px;text-align:center;
                    box-shadow:0 4px 24px rgba(180,160,140,0.12);">
            <div style="font-family:'DM Serif Display',serif;font-size:2rem;
                        color:#e8856a;margin-bottom:6px;">📈 Investment Hub</div>
            <div style="font-size:0.88rem;color:#9c8878;margin-bottom:6px;">
                나만의 비밀번호로 개인 공간에 접속하세요
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("login"):
            pw = st.text_input("🔑 비밀번호", type="password", placeholder="4자 이상 입력")
            if st.form_submit_button("입장하기", use_container_width=True):
                if len(pw) < 4:
                    st.error("비밀번호는 4자 이상이어야 합니다.")
                else:
                    h = get_hash(pw)
                    st.session_state.auth     = True
                    st.session_state.uid      = h
                    st.session_state.journal  = load_csv(journal_path(h),  JOURNAL_COLS)
                    st.session_state.analysis = load_csv(analysis_path(h), ANALYSIS_COLS)
                    st.rerun()
        st.caption("💡 처음 입력하는 비밀번호로 새 공간이 자동 생성됩니다.")
        st.caption("⚠️ 비밀번호를 잊으면 데이터를 복구할 수 없습니다.")
    st.stop()

UID  = st.session_state.uid
JP   = journal_path(UID)
AP   = analysis_path(UID)

# ══════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-logo">📈 Investment Hub</div>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.selectbox("", ["📝 매매일지","📊 포트폴리오","🔍 기업 원칙 분석"],
                        label_visibility="collapsed")
    st.markdown("---")
    st.caption(f"일지 {len(st.session_state.journal)}건 · 분석 {len(st.session_state.analysis)}건")
    st.caption(f"ID `{UID[:8]}...`")
    if st.button("🚪 로그아웃", use_container_width=True):
        for k in ['auth','uid','journal','analysis']: st.session_state.pop(k,None)
        st.rerun()

# ══════════════════════════════════════════
# 1. 매매일지
# ══════════════════════════════════════════
if menu == "📝 매매일지":
    st.title("📝 매매일지")
    st.caption("매매 내역을 직접 기록하고 관리합니다.")
    st.markdown("---")

    # 새 일지 작성
    with st.form("jform", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            j_date   = st.date_input("📅 매수일", datetime.now())
            j_ticker = st.text_input("🏷️ 티커", placeholder="예: AAPL").upper()
        with c2:
            j_price = st.number_input("💵 매수단가 ($)", min_value=0.0, format="%.2f")
            j_count = st.number_input("🔢 수량 (주)",    min_value=0, step=1)
        with c3:
            j_target = st.number_input("🎯 목표가 ($)", min_value=0.0, format="%.2f")
            j_period = st.text_input("⏳ 투자기간", placeholder="예: 3년, 장기보유")
        j_reason = st.text_area("📌 매수 이유", height=90,
                                placeholder="예: ROCE 20% 이상, FCF 3년 연속 양(+), 해자 보유...")
        if st.form_submit_button("💾 저장", use_container_width=True):
            if not j_ticker:
                st.error("티커를 입력해주세요.")
            else:
                row = {'매수일':str(j_date),'티커':j_ticker,'매수이유':j_reason,
                       '매수단가':j_price,'매수갯수':j_count,
                       '목표가':j_target,'예상투자기간':j_period}
                st.session_state.journal = pd.concat(
                    [st.session_state.journal, pd.DataFrame([row])], ignore_index=True)
                save_csv(st.session_state.journal, JP)
                st.success(f"✅ {j_ticker} 저장 완료!")

    st.markdown("---")
    st.subheader("📋 저장된 일지")

    if st.session_state.journal.empty:
        st.info("아직 작성된 일지가 없습니다. 위에서 첫 매매를 기록해보세요!")
    else:
        # 삭제 기능
        df_view = st.session_state.journal.copy()
        df_view.insert(0, '삭제', False)
        edited = st.data_editor(
            df_view, use_container_width=True, hide_index=True,
            column_config={'삭제': st.column_config.CheckboxColumn("🗑️")}
        )
        col_del, col_dl = st.columns([1, 4])
        with col_del:
            if st.button("선택 삭제", use_container_width=True):
                st.session_state.journal = (
                    edited[~edited['삭제']].drop(columns=['삭제']).reset_index(drop=True))
                save_csv(st.session_state.journal, JP)
                st.rerun()
        with col_dl:
            csv_bytes = st.session_state.journal.to_csv(
                index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("⬇️ CSV 다운로드", csv_bytes, "journal.csv", "text/csv",
                               use_container_width=True)

# ══════════════════════════════════════════
# 2. 포트폴리오
# ══════════════════════════════════════════
elif menu == "📊 포트폴리오":
    st.title("📊 포트폴리오 현황")
    st.caption("매매일지 기반으로 보유 현황을 집계합니다. 현재가는 직접 입력해주세요.")
    st.markdown("---")

    df_j = st.session_state.journal.copy()
    if df_j.empty:
        st.info("매매일지를 먼저 작성해주세요.")
    else:
        for c in ['매수단가','매수갯수','목표가']:
            df_j[c] = pd.to_numeric(df_j[c], errors='coerce').fillna(0)
        df_j['투자금액'] = df_j['매수단가'] * df_j['매수갯수']

        df_p = df_j.groupby('티커').agg(
            매수갯수=('매수갯수','sum'),
            투자금액=('투자금액','sum'),
            목표가=('목표가','last')
        ).reset_index()
        df_p['평균단가'] = df_p['투자금액'] / df_p['매수갯수'].replace(0,1)

        st.subheader("💵 현재가 입력")
        st.caption("각 종목의 현재가를 직접 입력하세요.")

        # 현재가 입력 폼
        price_cols = st.columns(min(len(df_p), 4))
        cur_prices = {}
        for i, row in df_p.iterrows():
            col_idx = i % min(len(df_p), 4)
            with price_cols[col_idx]:
                saved_key = f"cp_{UID}_{row['티커']}"
                default_p = st.session_state.get(saved_key, float(row['평균단가']))
                cur_prices[row['티커']] = st.number_input(
                    f"**{row['티커']}** ($)",
                    value=default_p,
                    min_value=0.0, format="%.2f",
                    key=f"price_input_{row['티커']}"
                )

        if st.button("📊 계산하기", use_container_width=True):
            for t, p in cur_prices.items():
                st.session_state[f"cp_{UID}_{t}"] = p

        st.markdown("---")

        # 계산
        df_p['현재가'] = df_p['티커'].map(
            {t: st.session_state.get(f"cp_{UID}_{t}", float(df_p[df_p['티커']==t]['평균단가'].iloc[0]))
             for t in df_p['티커']}
        )
        df_p['평가금액']      = df_p['현재가'] * df_p['매수갯수']
        df_p['수익금']        = df_p['평가금액'] - df_p['투자금액']
        df_p['수익률(%)']     = ((df_p['현재가'] - df_p['평균단가']) / df_p['평균단가'].replace(0,1)) * 100
        df_p['목표가달성률(%)'] = (df_p['현재가'] / df_p['목표가'].replace(0,1)) * 100

        # 요약 지표
        ti = df_p['투자금액'].sum()
        te = df_p['평가금액'].sum()
        tp = te - ti
        tr = (tp/ti*100) if ti > 0 else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 투자금액",  f"${ti:,.0f}")
        m2.metric("총 평가금액",  f"${te:,.0f}")
        m3.metric("총 수익금",    f"${tp:+,.0f}", delta=f"{tr:+.2f}%")
        m4.metric("보유 종목 수", f"{len(df_p)}개")

        st.markdown("---")

        # 종목별 테이블
        disp = df_p[['티커','매수갯수','평균단가','현재가','평가금액','수익률(%)','목표가달성률(%)']].copy()

        def color_return(v):
            if isinstance(v, (int, float)):
                if v > 0:  return 'color: #2d8a52; font-weight:600'
                if v < 0:  return 'color: #c0392b; font-weight:600'
            return ''

        st.dataframe(
            disp.style
            .format({'평균단가':'${:.2f}','현재가':'${:.2f}','평가금액':'${:,.0f}',
                     '수익률(%)':'{:+.2f}%','목표가달성률(%)':'{:.1f}%'})
            .applymap(color_return, subset=['수익률(%)']),
            use_container_width=True, hide_index=True
        )

        st.markdown("---")

        # 차트
        c1, c2 = st.columns(2)
        with c1:
            fig_pie = px.pie(
                df_p, values='평가금액', names='티커',
                title="포트폴리오 비중",
                color_discrete_sequence=['#f4a58a','#a8d8b9','#93c5e8','#f5c842','#c4b5f4','#f9a8d4'],
                hole=0.42
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='DM Sans', color='#3d3530'),
                title_font=dict(family='DM Serif Display'),
                legend=dict(bgcolor='rgba(0,0,0,0)')
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            colors_bar = ['#6dbf8a' if v >= 0 else '#f5877a' for v in df_p['수익률(%)']]
            fig_bar = go.Figure(go.Bar(
                x=df_p['티커'], y=df_p['수익률(%)'],
                marker_color=colors_bar,
                text=[f"{v:+.1f}%" for v in df_p['수익률(%)']],
                textposition='outside'
            ))
            fig_bar.update_layout(
                title="종목별 수익률",
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='DM Sans', color='#3d3530'),
                title_font=dict(family='DM Serif Display'),
                yaxis=dict(gridcolor='#ece6de', zerolinecolor='#d4c9bc'),
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # 투자금액 vs 평가금액 비교
        fig_compare = go.Figure()
        fig_compare.add_trace(go.Bar(
            name='투자금액', x=df_p['티커'], y=df_p['투자금액'],
            marker_color='#c4b5f4', text=[f"${v:,.0f}" for v in df_p['투자금액']],
            textposition='outside'
        ))
        fig_compare.add_trace(go.Bar(
            name='평가금액', x=df_p['티커'], y=df_p['평가금액'],
            marker_color='#f4a58a', text=[f"${v:,.0f}" for v in df_p['평가금액']],
            textposition='outside'
        ))
        fig_compare.update_layout(
            barmode='group', title="투자금액 vs 평가금액",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='DM Sans', color='#3d3530'),
            title_font=dict(family='DM Serif Display'),
            yaxis=dict(gridcolor='#ece6de'),
            legend=dict(bgcolor='rgba(0,0,0,0)')
        )
        st.plotly_chart(fig_compare, use_container_width=True)

# ══════════════════════════════════════════
# 3. 기업 원칙 분석
# ══════════════════════════════════════════
elif menu == "🔍 기업 원칙 분석":
    st.title("🔍 기업 투자 원칙 분석")
    st.caption("7가지 투자 원칙에 따라 수치를 직접 입력하고 기업을 평가합니다.")
    st.markdown("---")

    with st.expander("📖 7가지 투자 원칙 기준", expanded=False):
        st.markdown("""
| # | 원칙 | 기준 | 판정 |
|---|------|------|------|
| 1 | **ROCE** (자본수익률) | **15% 이상** | PASS |
| 2 | **매출 성장률** | **연평균 7% 이상** | PASS |
| 3 | **FCF** (잉여현금흐름) | **3년 연속 양(+)** | PASS |
| 4 | **부채비율** D/E | **1.0 이하** | PASS |
| 5 | **영업이익률** | **15% 이상** | PASS |
| 6 | **이평선 이격도** | **현재가 ≤ MA20 5% 이내** | PASS |
| 7 | **주주환원율** | **배당+자사주소각 > 10년물 금리** | PASS |
        """)
        st.caption("💡 수치는 FMP, 네이버 증권, 마켓워치 등에서 직접 조회 후 입력하세요.")

    # ── 새 분석 입력 ──────────────────────────
    st.subheader("📝 새 기업 분석 입력")

    with st.form("aform", clear_on_submit=True):
        ca1, ca2 = st.columns(2)
        with ca1:
            a_date    = st.date_input("📅 분석일", datetime.now())
            a_ticker  = st.text_input("🏷️ 티커", placeholder="예: AAPL").upper()
            a_name    = st.text_input("🏢 기업명", placeholder="예: Apple Inc.")
        with ca2:
            st.markdown("**채권금리 기준값**")
            a_bond    = st.number_input("🏦 미국 10년물 금리 (%)", min_value=0.0,
                                        value=4.5, format="%.2f",
                                        help="현재 미국 10년물 국채 금리 입력")

        st.markdown("---")
        st.markdown("**7가지 원칙 수치 입력**")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            a_roce   = st.number_input("① ROCE (%)",       min_value=-999.0, value=0.0, format="%.1f",
                                        help="EBIT / (총자산 - 유동부채) × 100")
            a_margin = st.number_input("⑤ 영업이익률 (%)", min_value=-999.0, value=0.0, format="%.1f",
                                        help="영업이익 / 매출액 × 100")
        with col2:
            a_growth = st.number_input("② 매출성장률 (%)", min_value=-999.0, value=0.0, format="%.1f",
                                        help="최근 3년 평균 YoY 매출 성장률")
            a_gap    = st.number_input("⑥ MA20 이격도 (%)", min_value=0.0, value=0.0, format="%.1f",
                                        help="|(현재가 - MA20) / MA20| × 100")
        with col3:
            a_fcf    = st.selectbox("③ FCF 3년 연속 양(+)?", ["예 ✓", "아니오 ✗"])
            a_sr     = st.number_input("⑦ 주주환원율 (%)",   min_value=0.0, value=0.0, format="%.2f",
                                        help="(배당수익률 + 자사주소각률) × 100")
        with col4:
            a_de     = st.number_input("④ 부채비율 D/E (배)", min_value=0.0, value=0.0, format="%.2f",
                                        help="총부채 / 총자본")
            a_memo   = st.text_area("📌 메모", height=80, placeholder="추가 투자 근거...")

        if st.form_submit_button("🔍 원칙 분석 저장", use_container_width=True):
            if not a_ticker:
                st.error("티커를 입력해주세요.")
            else:
                # 원칙별 PASS/FAIL 계산
                checks = {
                    'ROCE':     a_roce   >= 15,
                    '매출성장률': a_growth >= 7,
                    'FCF':      a_fcf == "예 ✓",
                    '부채비율':  a_de    <= 1.0,
                    '영업이익률': a_margin >= 15,
                    '이평선':   a_gap   <= 5,
                    '주주환원율': a_sr    > a_bond,
                }
                score = sum(checks.values())

                row = {
                    '분석일': str(a_date), '티커': a_ticker, '기업명': a_name,
                    'ROCE': a_roce, '매출성장률': a_growth,
                    'FCF여부': "예" if a_fcf == "예 ✓" else "아니오",
                    '부채비율DE': a_de, '영업이익률': a_margin,
                    '이평선이격': a_gap, '주주환원율': a_sr,
                    '채권금리': a_bond, '메모': a_memo,
                    '종합점수': f"{score}/7"
                }
                st.session_state.analysis = pd.concat(
                    [st.session_state.analysis, pd.DataFrame([row])], ignore_index=True)
                save_csv(st.session_state.analysis, AP)

                # 결과 즉시 표시
                st.markdown("---")
                st.markdown(f"### {a_name or a_ticker} `{a_ticker}` 분석 결과")

                s1, s2, s3, s4 = st.columns(4)
                s1.metric("통과 ✅", f"{score}개")
                s2.metric("미통과 ❌", f"{7-score}개")
                s3.metric("종합 점수", f"{score}/7")
                s4.metric("채권금리 기준", f"{a_bond:.2f}%")

                st.markdown("")
                principle_data = [
                    ("📐", "ROCE (자본수익률)",  f"{a_roce:.1f}%",         checks['ROCE'],     "기준: 15% 이상"),
                    ("📈", "매출 성장률",         f"{a_growth:.1f}% (3Y)",  checks['매출성장률'], "기준: 연평균 7% 이상"),
                    ("💵", "FCF (잉여현금흐름)", a_fcf,                     checks['FCF'],      "기준: 3년 연속 양(+)"),
                    ("🏦", "부채비율 D/E",        f"{a_de:.2f}x",           checks['부채비율'],   "기준: 1.0 이하"),
                    ("💹", "영업이익률",          f"{a_margin:.1f}%",        checks['영업이익률'], "기준: 15% 이상"),
                    ("📉", "이평선 이격도",       f"MA20 이격 {a_gap:.1f}%", checks['이평선'],    "기준: MA20 이격 5% 이내"),
                    ("💰", "주주환원율",          f"{a_sr:.2f}% vs 채권 {a_bond:.2f}%", checks['주주환원율'], "기준: 10년물 금리 초과"),
                ]
                for icon, name, val, passed, desc in principle_data:
                    if passed:
                        cls, tag = "p-card p-pass", '<span class="tag tag-pass">PASS ✓</span>'
                    else:
                        cls, tag = "p-card p-fail", '<span class="tag tag-fail">FAIL ✗</span>'
                    st.markdown(f"""
                    <div class="{cls}">
                        <div style="display:flex;align-items:center;margin-bottom:4px;">
                            <span style="font-family:'DM Serif Display',serif;font-weight:400;font-size:1rem;">
                                {icon} {name}</span>{tag}
                        </div>
                        <div style="font-size:1.05rem;color:#3d3530;margin-bottom:3px;font-weight:600;">
                            {val}</div>
                        <div style="font-size:0.78rem;color:#9c8878;">{desc}</div>
                    </div>""", unsafe_allow_html=True)

                if score >= 6:
                    st.success(f"🟢 **{a_name or a_ticker}** — {score}/7개 원칙 충족. 투자 원칙에 **강하게 부합**합니다.")
                elif score >= 4:
                    st.warning(f"🟡 **{a_name or a_ticker}** — {score}/7개 원칙 충족. 추가 검토를 권장합니다.")
                else:
                    st.error(f"🔴 **{a_name or a_ticker}** — {score}/7개 원칙 충족. 투자 원칙에 **미달**합니다.")

    # ── 저장된 분석 목록 ──────────────────────
    st.markdown("---")
    st.subheader("📋 저장된 분석 이력")

    if st.session_state.analysis.empty:
        st.info("아직 저장된 분석이 없습니다. 위에서 첫 기업을 분석해보세요!")
    else:
        df_a = st.session_state.analysis.copy()

        # 점수별 컬러 표시
        def score_color(v):
            try:
                n = int(str(v).split('/')[0])
                if n >= 6: return 'color:#2d8a52;font-weight:700'
                if n >= 4: return 'color:#927a10;font-weight:700'
                return 'color:#c0392b;font-weight:700'
            except: return ''

        st.dataframe(
            df_a.style.applymap(score_color, subset=['종합점수']),
            use_container_width=True, hide_index=True
        )

        # 레이더 차트 (최근 분석 기업들 비교)
        if len(df_a) >= 1:
            st.markdown("---")
            st.subheader("📊 원칙 달성률 비교")
            compare_tickers = st.multiselect(
                "비교할 기업 선택",
                df_a['티커'].tolist(),
                default=df_a['티커'].tolist()[-min(3, len(df_a)):]
            )

            if compare_tickers:
                fig_radar = go.Figure()
                categories = ['ROCE\n≥15%','매출성장률\n≥7%','FCF\n연속양(+)',
                              '부채비율\n≤1.0x','영업이익률\n≥15%','이평선\n≤5%','주주환원율\n>채권금리']
                pastel_colors = ['#f4a58a','#6dbf8a','#93c5e8','#c4b5f4','#f5c842','#f9a8d4','#a8d8b9']

                for i, t in enumerate(compare_tickers):
                    rows = df_a[df_a['티커'] == t]
                    if rows.empty: continue
                    r = rows.iloc[-1]  # 가장 최근 분석

                    try: bond = float(r.get('채권금리', 4.5) or 4.5)
                    except: bond = 4.5

                    # 각 원칙 달성 여부를 0~100으로 변환
                    def pct(val, threshold, invert=False):
                        try:
                            v = float(val)
                            met = (v <= threshold) if invert else (v >= threshold)
                            return 100 if met else max(0, min(90, v/threshold*90))
                        except: return 0

                    vals = [
                        pct(r.get('ROCE',0), 15),
                        pct(r.get('매출성장률',0), 7),
                        100 if str(r.get('FCF여부','')) == '예' else 10,
                        pct(r.get('부채비율DE',99), 1.0, invert=True),
                        pct(r.get('영업이익률',0), 15),
                        pct(r.get('이평선이격',99), 5.0, invert=True),
                        100 if float(r.get('주주환원율',0) or 0) > bond else 30,
                    ]
                    vals_closed = vals + [vals[0]]
                    cats_closed = categories + [categories[0]]

                    fig_radar.add_trace(go.Scatterpolar(
                        r=vals_closed, theta=cats_closed,
                        fill='toself', name=t,
                        line_color=pastel_colors[i % len(pastel_colors)],
                        fillcolor=pastel_colors[i % len(pastel_colors)].replace(')', ',0.2)').replace('rgb', 'rgba') if 'rgb' in pastel_colors[i%len(pastel_colors)] else pastel_colors[i % len(pastel_colors)] + '33'
                    ))

                fig_radar.update_layout(
                    polar=dict(
                        bgcolor='white',
                        radialaxis=dict(visible=True, range=[0,100],
                                        tickfont=dict(size=9), gridcolor='#ece6de'),
                        angularaxis=dict(gridcolor='#ece6de', linecolor='#d4c9bc')
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='DM Sans', color='#3d3530', size=11),
                    legend=dict(bgcolor='rgba(255,255,255,0.8)', bordercolor='#ece6de', borderwidth=1),
                    height=440
                )
                st.plotly_chart(fig_radar, use_container_width=True)
                st.caption("💡 수치가 클수록 원칙 달성에 가깝습니다. 100 = 기준 완전 충족")

        # 삭제 및 다운로드
        col_adel, col_adl = st.columns([1, 4])
        with col_adel:
            if st.button("🗑️ 전체 삭제", use_container_width=True):
                st.session_state.analysis = pd.DataFrame(columns=ANALYSIS_COLS)
                save_csv(st.session_state.analysis, AP)
                st.rerun()
        with col_adl:
            a_csv = st.session_state.analysis.to_csv(
                index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("⬇️ 분석 이력 CSV 다운로드", a_csv,
                               "analysis.csv", "text/csv", use_container_width=True)
