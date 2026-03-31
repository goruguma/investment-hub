import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# ─────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────
st.set_page_config(
    page_title="My Investment Hub",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# 커스텀 CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

/* 전체 배경 */
[data-testid="stAppViewContainer"] {
    background: #0a0e1a;
    color: #e8eaf0;
}
[data-testid="stSidebar"] {
    background: #0d1221;
    border-right: 1px solid #1e2a3a;
}
[data-testid="stSidebar"] * {
    color: #c8cdd8 !important;
}

/* 헤더 */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #e8eaf0 !important;
    letter-spacing: -0.5px;
}
h1 { font-weight: 800; font-size: 2rem !important; }
h2 { font-weight: 600; font-size: 1.4rem !important; }

/* 메트릭 카드 */
[data-testid="stMetric"] {
    background: #111827;
    border: 1px solid #1e2a3a;
    border-radius: 12px;
    padding: 16px 20px;
}
[data-testid="stMetricLabel"] { color: #7a8499 !important; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetricValue"] { color: #e8eaf0 !important; font-family: 'Space Mono', monospace !important; font-size: 1.6rem !important; }
[data-testid="stMetricDelta"] { font-family: 'Space Mono', monospace !important; }

/* 데이터프레임 */
[data-testid="stDataFrame"] { border: 1px solid #1e2a3a; border-radius: 12px; overflow: hidden; }

/* 인풋 */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #111827 !important;
    border: 1px solid #1e2a3a !important;
    color: #e8eaf0 !important;
    border-radius: 8px !important;
}

/* 버튼 */
[data-testid="stFormSubmitButton"] button,
.stButton button {
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
[data-testid="stFormSubmitButton"] button:hover,
.stButton button:hover { opacity: 0.85 !important; }

/* 구분선 */
hr { border-color: #1e2a3a !important; }

/* 셀렉트박스 */
[data-testid="stSelectbox"] > div { background: #111827 !important; border: 1px solid #1e2a3a !important; border-radius: 8px !important; }

/* 성공/정보 메시지 */
[data-testid="stSuccess"] { background: #0d2a1a !important; border-left: 3px solid #22c55e !important; border-radius: 8px; }
[data-testid="stInfo"] { background: #0d1a2a !important; border-left: 3px solid #3b82f6 !important; border-radius: 8px; }
[data-testid="stWarning"] { background: #2a1a0d !important; border-left: 3px solid #f59e0b !important; border-radius: 8px; }

/* 사이드바 메뉴 타이틀 */
.sidebar-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.3rem;
    color: #3b82f6 !important;
    letter-spacing: -0.5px;
    margin-bottom: 1rem;
}

/* 원칙 카드 */
.principle-card {
    background: #111827;
    border: 1px solid #1e2a3a;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
}
.principle-pass { border-left: 4px solid #22c55e; }
.principle-fail { border-left: 4px solid #ef4444; }
.principle-warn { border-left: 4px solid #f59e0b; }

/* 태그 */
.tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    margin-left: 8px;
}
.tag-pass { background: #0d2a1a; color: #22c55e; border: 1px solid #22c55e; }
.tag-fail { background: #2a0d0d; color: #ef4444; border: 1px solid #ef4444; }
.tag-warn { background: #2a1a0d; color: #f59e0b; border: 1px solid #f59e0b; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# CSV 저장/불러오기
# ─────────────────────────────────────────
DATA_PATH = "data/journal.csv"
COLUMNS = ['매수일', '티커', '매수이유', '매수단가', '매수갯수', '목표가', '예상투자기간']

def load_journal():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        # 컬럼이 없으면 빈 df
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)

def save_journal(df):
    os.makedirs("data", exist_ok=True)
    df.to_csv(DATA_PATH, index=False, encoding='utf-8-sig')

# 세션 초기화
if 'journal' not in st.session_state:
    st.session_state.journal = load_journal()

# ─────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">📈 Investment Hub</div>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.selectbox(
        "메뉴",
        ["📝 매매일지", "📊 포트폴리오", "🔍 기업 원칙 분석"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption(f"데이터: `{DATA_PATH}`")
    st.caption(f"일지 수: {len(st.session_state.journal)}건")

# ═══════════════════════════════════════════════════════
# 1. 매매일지
# ═══════════════════════════════════════════════════════
if menu == "📝 매매일지":
    st.title("📝 매매일지")
    st.caption("매매 내역을 기록하고 CSV로 저장합니다.")
    st.markdown("---")

    # 삭제 기능
    col_title, col_delete = st.columns([5, 1])
    with col_delete:
        if st.button("🗑️ 전체 초기화", help="저장된 일지를 모두 삭제합니다"):
            st.session_state.journal = pd.DataFrame(columns=COLUMNS)
            save_journal(st.session_state.journal)
            st.rerun()

    with st.form("journal_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("📅 매수일", datetime.now())
            ticker = st.text_input("🏷️ 티커", placeholder="예: AAPL, NVDA").upper()
        with col2:
            price = st.number_input("💵 매수단가 ($)", min_value=0.0, format="%.2f")
            count = st.number_input("🔢 매수 수량 (주)", min_value=0, step=1)
        with col3:
            target = st.number_input("🎯 목표가 ($)", min_value=0.0, format="%.2f")
            period = st.text_input("⏳ 예상 투자기간", placeholder="예: 3년, 장기보유")

        reason = st.text_area("📌 매수 이유 (투자 근거)", height=100,
                              placeholder="예: 높은 ROCE, 지속적 FCF 성장, 해자 보유...")
        submitted = st.form_submit_button("💾 일지 저장")

        if submitted:
            if not ticker:
                st.error("티커를 입력해주세요.")
            else:
                new_row = {
                    '매수일': str(date), '티커': ticker, '매수이유': reason,
                    '매수단가': price, '매수갯수': count, '목표가': target, '예상투자기간': period
                }
                st.session_state.journal = pd.concat(
                    [st.session_state.journal, pd.DataFrame([new_row])], ignore_index=True
                )
                save_journal(st.session_state.journal)
                st.success(f"✅ {ticker} 매매일지가 저장되었습니다!")

    st.markdown("---")
    st.subheader("📋 저장된 일지")

    df_show = st.session_state.journal.copy()
    if df_show.empty:
        st.info("아직 저장된 일지가 없습니다. 위에서 작성해보세요.")
    else:
        # 개별 삭제
        df_show.insert(0, '삭제', False)
        edited = st.data_editor(df_show, use_container_width=True, hide_index=True,
                                column_config={'삭제': st.column_config.CheckboxColumn("삭제")})
        if st.button("선택 항목 삭제"):
            keep = ~edited['삭제']
            st.session_state.journal = edited[keep].drop(columns=['삭제']).reset_index(drop=True)
            save_journal(st.session_state.journal)
            st.rerun()

        # CSV 다운로드
        csv = st.session_state.journal.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("⬇️ CSV 다운로드", csv, "journal.csv", "text/csv")

# ═══════════════════════════════════════════════════════
# 2. 포트폴리오
# ═══════════════════════════════════════════════════════
elif menu == "📊 포트폴리오":
    st.title("📊 포트폴리오 현황")
    st.caption("yfinance 기준 실시간 평가금액 및 수익률")
    st.markdown("---")

    df_j = st.session_state.journal.copy()
    if df_j.empty:
        st.info("매매일지를 먼저 작성해주세요.")
    else:
        df_j['매수단가'] = pd.to_numeric(df_j['매수단가'], errors='coerce').fillna(0)
        df_j['매수갯수'] = pd.to_numeric(df_j['매수갯수'], errors='coerce').fillna(0)
        df_j['목표가'] = pd.to_numeric(df_j['목표가'], errors='coerce').fillna(0)

        # 가중평균 단가 집계
        df_j['투자금액'] = df_j['매수단가'] * df_j['매수갯수']
        df_p = df_j.groupby('티커').agg(
            매수갯수=('매수갯수', 'sum'),
            투자금액=('투자금액', 'sum'),
            목표가=('목표가', 'last')
        ).reset_index()
        df_p['평균단가'] = df_p['투자금액'] / df_p['매수갯수'].replace(0, 1)

        with st.spinner('현재가 불러오는 중...'):
            current_prices, sectors, names = [], [], []
            for t in df_p['티커']:
                try:
                    stock = yf.Ticker(t)
                    hist = stock.history(period="2d")
                    price = float(hist['Close'].iloc[-1]) if not hist.empty else 0
                    info = stock.info
                    sector = info.get('sector', 'Unknown')
                    name = info.get('shortName', t)
                except:
                    price, sector, name = 0, 'Unknown', t
                current_prices.append(price)
                sectors.append(sector)
                names.append(name)

            df_p['현재가'] = current_prices
            df_p['섹터'] = sectors
            df_p['기업명'] = names
            df_p['평가금액'] = df_p['현재가'] * df_p['매수갯수']
            df_p['수익금'] = df_p['평가금액'] - df_p['투자금액']
            df_p['수익률(%)'] = ((df_p['현재가'] - df_p['평균단가']) / df_p['평균단가'].replace(0, 1)) * 100
            df_p['목표가달성률(%)'] = (df_p['현재가'] / df_p['목표가'].replace(0, 1)) * 100

        # 요약 메트릭
        total_invest = df_p['투자금액'].sum()
        total_eval = df_p['평가금액'].sum()
        total_profit = total_eval - total_invest
        total_return = (total_profit / total_invest * 100) if total_invest > 0 else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 투자금액", f"${total_invest:,.0f}")
        m2.metric("총 평가금액", f"${total_eval:,.0f}")
        m3.metric("총 수익금", f"${total_profit:,.0f}", delta=f"{total_return:.2f}%")
        m4.metric("보유 종목 수", f"{len(df_p)}개")

        st.markdown("---")

        # 종목별 테이블
        st.subheader("종목별 현황")
        display_df = df_p[['티커', '기업명', '섹터', '매수갯수', '평균단가', '현재가', '평가금액', '수익률(%)', '목표가달성률(%)']].copy()
        st.dataframe(
            display_df.style
                .format({
                    '평균단가': '${:.2f}', '현재가': '${:.2f}',
                    '평가금액': '${:,.0f}', '수익률(%)': '{:.2f}%', '목표가달성률(%)': '{:.1f}%'
                })
                .applymap(lambda v: 'color: #22c55e' if isinstance(v, (int, float)) and v > 0 else
                                    ('color: #ef4444' if isinstance(v, (int, float)) and v < 0 else ''),
                          subset=['수익률(%)'])
            ,
            use_container_width=True, hide_index=True
        )

        st.markdown("---")

        # 차트
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_pie = px.pie(
                df_p, values='평가금액', names='티커',
                title="포트폴리오 비중",
                color_discrete_sequence=px.colors.sequential.Blues_r,
                hole=0.45
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e8eaf0', title_font_size=14
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_c2:
            fig_bar = px.bar(
                df_p, x='티커', y='수익률(%)',
                title="종목별 수익률",
                color='수익률(%)',
                color_continuous_scale=['#ef4444', '#111827', '#22c55e'],
                color_continuous_midpoint=0,
                text='수익률(%)'
            )
            fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e8eaf0', title_font_size=14,
                yaxis=dict(gridcolor='#1e2a3a'), showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # 섹터별 비중
        fig_sector = px.bar(
            df_p.groupby('섹터')['평가금액'].sum().reset_index(),
            x='섹터', y='평가금액', title="섹터별 평가금액",
            color='평가금액', color_continuous_scale='Blues',
            text='평가금액'
        )
        fig_sector.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_sector.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e8eaf0', xaxis=dict(gridcolor='#1e2a3a'),
            yaxis=dict(gridcolor='#1e2a3a'), showlegend=False
        )
        st.plotly_chart(fig_sector, use_container_width=True)

        # 주가 히스토리 (멀티 티커)
        st.markdown("---")
        st.subheader("📈 주가 추이 (최근 1년)")
        selected_tickers = st.multiselect("비교할 종목 선택", df_p['티커'].tolist(), default=df_p['티커'].tolist()[:3])
        period_opt = st.select_slider("기간", options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], value="1y")

        if selected_tickers:
            hist_data = {}
            for t in selected_tickers:
                try:
                    h = yf.Ticker(t).history(period=period_opt)['Close']
                    hist_data[t] = h
                except:
                    pass
            if hist_data:
                hist_df = pd.DataFrame(hist_data)
                fig_line = go.Figure()
                colors = ['#3b82f6', '#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6']
                for i, col in enumerate(hist_df.columns):
                    fig_line.add_trace(go.Scatter(
                        x=hist_df.index, y=hist_df[col], name=col,
                        line=dict(color=colors[i % len(colors)], width=2)
                    ))
                fig_line.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#e8eaf0', legend=dict(bgcolor='rgba(0,0,0,0)'),
                    xaxis=dict(gridcolor='#1e2a3a'), yaxis=dict(gridcolor='#1e2a3a'),
                    hovermode='x unified'
                )
                st.plotly_chart(fig_line, use_container_width=True)

# ═══════════════════════════════════════════════════════
# 3. 기업 원칙 분석
# ═══════════════════════════════════════════════════════
elif menu == "🔍 기업 원칙 분석":
    st.title("🔍 기업 투자 원칙 분석")
    st.caption("5가지 원칙 기반으로 기업의 투자 적합성을 검증합니다.")
    st.markdown("---")

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        target_ticker = st.text_input("분석할 티커 입력", placeholder="예: MSFT, AAPL, NVDA").upper()
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze = st.button("🔍 분석 시작", use_container_width=True)

    # 원칙 설명
    with st.expander("📖 5가지 투자 원칙 보기"):
        st.markdown("""
        | # | 원칙 | 기준 |
        |---|------|------|
        | 1 | **ROCE (자본수익률)** | 15% 이상 |
        | 2 | **매출 성장률** | 최근 3년 평균 YoY 7% 이상 |
        | 3 | **FCF (잉여현금흐름)** | 3년 연속 양(+)의 FCF |
        | 4 | **부채비율** | D/E 비율 1.0 이하 (재무 건전성) |
        | 5 | **지속가능한 비즈니스** | 영업이익률 15% 이상 |
        """)

    if target_ticker and analyze:
        with st.spinner(f"{target_ticker} 재무 데이터 불러오는 중..."):
            try:
                stock = yf.Ticker(target_ticker)
                info = stock.info
                financials = stock.financials       # 연간 손익계산서 (컬럼=연도)
                balance = stock.balance_sheet
                cashflow = stock.cashflow

                company_name = info.get('shortName', target_ticker)
                sector = info.get('sector', 'N/A')
                industry = info.get('industry', 'N/A')
                market_cap = info.get('marketCap', 0)
                description = info.get('longBusinessSummary', '')

                st.markdown(f"## {company_name} `{target_ticker}`")
                st.caption(f"섹터: **{sector}** | 업종: **{industry}** | 시가총액: **${market_cap/1e9:.1f}B**")

                if description:
                    with st.expander("기업 소개"):
                        st.write(description[:500] + "...")

                st.markdown("---")
                st.subheader("✅ 투자 원칙 체크리스트")

                results = {}

                # ── 원칙 1: ROCE ──────────────────────
                try:
                    ebit = financials.loc['EBIT'].iloc[0] if 'EBIT' in financials.index else \
                           financials.loc['Operating Income'].iloc[0]
                    total_assets = balance.loc['Total Assets'].iloc[0]
                    curr_liab_keys = ['Current Liabilities', 'Total Current Liabilities']
                    curr_liab = next((balance.loc[k].iloc[0] for k in curr_liab_keys if k in balance.index), 0)
                    capital_employed = total_assets - curr_liab
                    roce = (ebit / capital_employed) * 100 if capital_employed != 0 else 0
                    results['ROCE'] = {
                        'value': roce, 'threshold': 15, 'unit': '%',
                        'pass': roce >= 15,
                        'label': f"{roce:.1f}%",
                        'desc': "EBIT / (총자산 - 유동부채)"
                    }
                except Exception as e:
                    results['ROCE'] = {'value': 0, 'threshold': 15, 'unit': '%', 'pass': None,
                                        'label': 'N/A', 'desc': f"데이터 없음 ({e})"}

                # ── 원칙 2: 매출 성장률 ─────────────────
                try:
                    rev_keys = ['Total Revenue', 'Revenue']
                    rev_row = next((financials.loc[k] for k in rev_keys if k in financials.index), None)
                    if rev_row is not None and len(rev_row) >= 3:
                        rev_vals = rev_row.iloc[:3].values  # 최근 3년 (내림차순)
                        growth_rates = [(rev_vals[i] - rev_vals[i+1]) / abs(rev_vals[i+1]) * 100
                                        for i in range(len(rev_vals)-1) if rev_vals[i+1] != 0]
                        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0
                    else:
                        avg_growth = 0
                    results['매출성장률'] = {
                        'value': avg_growth, 'threshold': 7, 'unit': '%',
                        'pass': avg_growth >= 7,
                        'label': f"{avg_growth:.1f}% (3Y avg)",
                        'desc': "최근 3년 평균 YoY 매출 성장률"
                    }
                except Exception as e:
                    results['매출성장률'] = {'value': 0, 'threshold': 7, 'unit': '%', 'pass': None,
                                               'label': 'N/A', 'desc': f"데이터 없음 ({e})"}

                # ── 원칙 3: FCF ──────────────────────────
                try:
                    fcf_keys = ['Free Cash Flow', 'FreeCashFlow']
                    fcf_row = next((cashflow.loc[k] for k in fcf_keys if k in cashflow.index), None)
                    if fcf_row is None:
                        # 영업CF - CapEx 계산
                        op_cf = cashflow.loc['Operating Cash Flow'].iloc[:3] if 'Operating Cash Flow' in cashflow.index else None
                        capex_keys = ['Capital Expenditure', 'CapEx', 'Purchase Of Plant And Equipment']
                        capex = next((cashflow.loc[k].iloc[:3] for k in capex_keys if k in cashflow.index), None)
                        if op_cf is not None and capex is not None:
                            fcf_vals = op_cf.values + capex.values  # capex는 보통 음수
                        else:
                            fcf_vals = []
                    else:
                        fcf_vals = fcf_row.iloc[:3].values

                    if len(fcf_vals) >= 1:
                        all_positive = all(v > 0 for v in fcf_vals)
                        fcf_latest = fcf_vals[0] / 1e9
                        results['FCF'] = {
                            'value': fcf_vals[0], 'threshold': 0, 'unit': '$B',
                            'pass': all_positive,
                            'label': f"${fcf_latest:.2f}B (최근) | 3년 연속 양(+): {'✓' if all_positive else '✗'}",
                            'desc': "잉여현금흐름 3년 연속 양(+) 여부"
                        }
                    else:
                        results['FCF'] = {'value': 0, 'pass': None, 'label': 'N/A', 'desc': '데이터 없음', 'unit': ''}
                except Exception as e:
                    results['FCF'] = {'value': 0, 'pass': None, 'label': 'N/A', 'desc': f"데이터 없음 ({e})", 'unit': ''}

                # ── 원칙 4: 부채비율 D/E ─────────────────
                try:
                    de_ratio = info.get('debtToEquity', None)
                    if de_ratio is None:
                        total_debt_keys = ['Long Term Debt', 'Total Debt']
                        equity_keys = ['Stockholders Equity', 'Total Stockholders Equity', 'Common Stock Equity']
                        debt = next((balance.loc[k].iloc[0] for k in total_debt_keys if k in balance.index), None)
                        equity = next((balance.loc[k].iloc[0] for k in equity_keys if k in balance.index), None)
                        de_ratio = (debt / equity * 100) if (debt and equity and equity != 0) else 0
                    else:
                        pass  # yfinance returns as percentage (e.g. 150 = 1.5x)
                    de_display = de_ratio / 100 if de_ratio and de_ratio > 10 else de_ratio  # normalize
                    results['부채비율'] = {
                        'value': de_display, 'threshold': 1.0, 'unit': 'x',
                        'pass': (de_display <= 1.0) if de_display else None,
                        'label': f"D/E {de_display:.2f}x" if de_display else 'N/A',
                        'desc': "부채/자본 비율 1.0 이하 (재무 건전성)"
                    }
                except Exception as e:
                    results['부채비율'] = {'value': 0, 'pass': None, 'label': 'N/A', 'desc': f"데이터 없음 ({e})", 'unit': ''}

                # ── 원칙 5: 영업이익률 (지속가능성) ───────
                try:
                    op_margin = info.get('operatingMargins', None)
                    if op_margin is None:
                        op_income_keys = ['Operating Income', 'EBIT']
                        op_income = next((financials.loc[k].iloc[0] for k in op_income_keys if k in financials.index), None)
                        rev_keys2 = ['Total Revenue', 'Revenue']
                        revenue = next((financials.loc[k].iloc[0] for k in rev_keys2 if k in financials.index), None)
                        op_margin = (op_income / revenue) if (op_income and revenue and revenue != 0) else 0
                    op_margin_pct = op_margin * 100 if op_margin and abs(op_margin) < 10 else (op_margin or 0)
                    results['영업이익률'] = {
                        'value': op_margin_pct, 'threshold': 15, 'unit': '%',
                        'pass': op_margin_pct >= 15,
                        'label': f"{op_margin_pct:.1f}%",
                        'desc': "지속 가능한 비즈니스 모델 (영업이익률 15% 이상)"
                    }
                except Exception as e:
                    results['영업이익률'] = {'value': 0, 'threshold': 15, 'unit': '%', 'pass': None,
                                               'label': 'N/A', 'desc': f"데이터 없음 ({e})"}

                # ── 결과 출력 ────────────────────────────
                pass_count = sum(1 for v in results.values() if v.get('pass') is True)
                fail_count = sum(1 for v in results.values() if v.get('pass') is False)
                na_count = sum(1 for v in results.values() if v.get('pass') is None)

                score_col1, score_col2, score_col3, score_col4 = st.columns(4)
                score_col1.metric("통과 ✅", f"{pass_count}개")
                score_col2.metric("미통과 ❌", f"{fail_count}개")
                score_col3.metric("데이터 없음 ⚠️", f"{na_count}개")
                score_col4.metric("종합 점수", f"{pass_count}/{pass_count+fail_count}점")

                st.markdown("")

                icons = {'ROCE': '📐', '매출성장률': '📈', 'FCF': '💵', '부채비율': '🏦', '영업이익률': '💹'}
                for name, r in results.items():
                    if r['pass'] is True:
                        card_class = "principle-card principle-pass"
                        tag = f'<span class="tag tag-pass">PASS ✓</span>'
                    elif r['pass'] is False:
                        card_class = "principle-card principle-fail"
                        tag = f'<span class="tag tag-fail">FAIL ✗</span>'
                    else:
                        card_class = "principle-card principle-warn"
                        tag = f'<span class="tag tag-warn">N/A</span>'

                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display:flex; align-items:center; margin-bottom:4px;">
                            <span style="font-family:'Syne',sans-serif; font-weight:700; font-size:1rem;">
                                {icons.get(name, '•')} {name}
                            </span>
                            {tag}
                        </div>
                        <div style="font-family:'Space Mono',monospace; font-size:1.2rem; color:#e8eaf0; margin-bottom:4px;">
                            {r['label']}
                        </div>
                        <div style="font-size:0.78rem; color:#7a8499;">{r['desc']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # ── 재무 추세 차트 ────────────────────────
                st.markdown("---")
                st.subheader("📊 3개년 재무 추세")

                try:
                    rev_keys_chart = ['Total Revenue', 'Revenue']
                    rev_row_c = next((financials.loc[k] for k in rev_keys_chart if k in financials.index), None)
                    op_keys_chart = ['Operating Income', 'EBIT']
                    op_row_c = next((financials.loc[k] for k in op_keys_chart if k in financials.index), None)
                    fcf_keys_chart = ['Free Cash Flow']
                    fcf_row_c = next((cashflow.loc[k] for k in fcf_keys_chart if k in cashflow.index), None)

                    chart_data = {}
                    if rev_row_c is not None:
                        chart_data['매출 ($B)'] = (rev_row_c.iloc[:4] / 1e9).values[::-1]
                        years = [str(d.year) for d in rev_row_c.index[:4]][::-1]
                    if op_row_c is not None:
                        chart_data['영업이익 ($B)'] = (op_row_c.iloc[:4] / 1e9).values[::-1]
                    if fcf_row_c is not None:
                        chart_data['FCF ($B)'] = (fcf_row_c.iloc[:4] / 1e9).values[::-1]

                    if chart_data and 'years' in dir():
                        chart_df = pd.DataFrame(chart_data, index=years)
                        fig_trend = go.Figure()
                        clr_map = {'매출 ($B)': '#3b82f6', '영업이익 ($B)': '#22c55e', 'FCF ($B)': '#f59e0b'}
                        for col in chart_df.columns:
                            fig_trend.add_trace(go.Bar(
                                name=col, x=chart_df.index, y=chart_df[col],
                                marker_color=clr_map.get(col, '#6366f1')
                            ))
                        fig_trend.update_layout(
                            barmode='group',
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#e8eaf0', legend=dict(bgcolor='rgba(0,0,0,0)'),
                            xaxis=dict(gridcolor='#1e2a3a'), yaxis=dict(gridcolor='#1e2a3a'),
                        )
                        st.plotly_chart(fig_trend, use_container_width=True)
                except Exception as e:
                    st.warning(f"재무 추세 차트 생성 실패: {e}")

                # ── 요약 코멘트 ──────────────────────────
                st.markdown("---")
                if pass_count >= 4:
                    st.success(f"🟢 **{company_name}** 은(는) {pass_count}/5개 원칙을 충족합니다. 투자 원칙에 **강하게 부합**합니다.")
                elif pass_count >= 3:
                    st.warning(f"🟡 **{company_name}** 은(는) {pass_count}/5개 원칙을 충족합니다. 추가 검토를 권장합니다.")
                else:
                    st.error(f"🔴 **{company_name}** 은(는) {pass_count}/5개 원칙을 충족합니다. 투자 원칙에 **미달**합니다.")

            except Exception as e:
                st.error(f"데이터를 불러오지 못했습니다: {e}")
                st.caption("티커가 올바른지, yfinance 연결 상태를 확인해주세요.")
