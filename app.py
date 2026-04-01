import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import hashlib
import time

# yfinance 세션 - rate limit 방지용 retry 설정
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    _session = requests.Session()
    _retry = Retry(total=5, backoff_factor=1.5, status_forcelist=[429, 500, 502, 503, 504])
    _session.mount("https://", HTTPAdapter(max_retries=_retry))
    _session.headers.update({"User-Agent": "Mozilla/5.0"})
except:
    _session = None

def get_ticker(symbol):
    """rate limit 방지 헬퍼 - yf.Ticker에 세션 주입"""
    try:
        return get_ticker(symbol, session=_session)
    except:
        return get_ticker(symbol)

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

[data-testid="stAppViewContainer"] { background: #0a0e1a; color: #e8eaf0; }
[data-testid="stSidebar"] { background: #0d1221; border-right: 1px solid #1e2a3a; }
[data-testid="stSidebar"] * { color: #c8cdd8 !important; }

h1, h2, h3 { font-family: 'Syne', sans-serif !important; color: #e8eaf0 !important; letter-spacing: -0.5px; }
h1 { font-weight: 800; font-size: 2rem !important; }
h2 { font-weight: 600; font-size: 1.4rem !important; }

[data-testid="stMetric"] { background: #111827; border: 1px solid #1e2a3a; border-radius: 12px; padding: 16px 20px; }
[data-testid="stMetricLabel"] { color: #7a8499 !important; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetricValue"] { color: #e8eaf0 !important; font-family: 'Space Mono', monospace !important; font-size: 1.6rem !important; }
[data-testid="stMetricDelta"] { font-family: 'Space Mono', monospace !important; }

[data-testid="stDataFrame"] { border: 1px solid #1e2a3a; border-radius: 12px; overflow: hidden; }

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #111827 !important; border: 1px solid #1e2a3a !important;
    color: #e8eaf0 !important; border-radius: 8px !important;
}

[data-testid="stFormSubmitButton"] button, .stButton button {
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important; font-weight: 700 !important;
    letter-spacing: 0.5px !important; padding: 0.5rem 1.5rem !important; transition: opacity 0.2s !important;
}
[data-testid="stFormSubmitButton"] button:hover, .stButton button:hover { opacity: 0.85 !important; }

hr { border-color: #1e2a3a !important; }
[data-testid="stSelectbox"] > div { background: #111827 !important; border: 1px solid #1e2a3a !important; border-radius: 8px !important; }

[data-testid="stSuccess"] { background: #0d2a1a !important; border-left: 3px solid #22c55e !important; border-radius: 8px; }
[data-testid="stInfo"]    { background: #0d1a2a !important; border-left: 3px solid #3b82f6 !important; border-radius: 8px; }
[data-testid="stWarning"] { background: #2a1a0d !important; border-left: 3px solid #f59e0b !important; border-radius: 8px; }

.sidebar-title { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.3rem; color: #3b82f6 !important; letter-spacing: -0.5px; margin-bottom: 1rem; }

.principle-card { background: #111827; border: 1px solid #1e2a3a; border-radius: 12px; padding: 16px 20px; margin-bottom: 10px; }
.principle-pass { border-left: 4px solid #22c55e; }
.principle-fail { border-left: 4px solid #ef4444; }
.principle-warn { border-left: 4px solid #f59e0b; }

.tag { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.72rem; font-family: 'Space Mono', monospace; font-weight: 700; margin-left: 8px; }
.tag-pass { background: #0d2a1a; color: #22c55e; border: 1px solid #22c55e; }
.tag-fail { background: #2a0d0d; color: #ef4444; border: 1px solid #ef4444; }
.tag-warn { background: #2a1a0d; color: #f59e0b; border: 1px solid #f59e0b; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 비밀번호 기반 사용자 분리
# ─────────────────────────────────────────
def get_user_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()[:16]

def get_data_path(user_hash: str) -> str:
    return f"data/journal_{user_hash}.csv"

COLUMNS = ['매수일', '티커', '매수이유', '매수단가', '매수갯수', '목표가', '예상투자기간']

def load_journal(path):
    if os.path.exists(path):
        df = pd.read_csv(path)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)

def save_journal(df, path):
    os.makedirs("data", exist_ok=True)
    df.to_csv(path, index=False, encoding='utf-8-sig')

# ─────────────────────────────────────────
# 로그인 화면
# ─────────────────────────────────────────
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_hash = None
    st.session_state.data_path = None
    st.session_state.journal = None

if not st.session_state.authenticated:
    # 로그인 UI
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("""
        <div style="background:#111827;border:1px solid #1e2a3a;border-radius:16px;padding:40px 36px;text-align:center;">
            <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.8rem;color:#3b82f6;margin-bottom:8px;">📈 Investment Hub</div>
            <div style="font-size:0.85rem;color:#7a8499;margin-bottom:24px;">나만의 비밀번호로 개인 데이터 공간에 접속하세요</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form"):
            pw = st.text_input("🔑 비밀번호", type="password", placeholder="본인만 아는 비밀번호 입력 (4자 이상)")
            login_btn = st.form_submit_button("입장하기", use_container_width=True)

        st.caption("💡 처음 입력하는 비밀번호로 새 데이터 공간이 자동 생성됩니다.")
        st.caption("⚠️ 비밀번호를 잊으면 데이터를 복구할 수 없습니다.")

        if login_btn:
            if not pw or len(pw) < 4:
                st.error("비밀번호는 4자 이상 입력해주세요.")
            else:
                user_hash = get_user_hash(pw)
                data_path = get_data_path(user_hash)
                st.session_state.authenticated = True
                st.session_state.user_hash = user_hash
                st.session_state.data_path = data_path
                st.session_state.journal = load_journal(data_path)
                st.rerun()
    st.stop()

# ─────────────────────────────────────────
# 로그인 후 메인 앱
# ─────────────────────────────────────────
DATA_PATH = st.session_state.data_path

with st.sidebar:
    st.markdown('<div class="sidebar-title">📈 Investment Hub</div>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.selectbox("메뉴", ["📝 매매일지", "📊 포트폴리오", "🔍 기업 원칙 분석"], label_visibility="collapsed")
    st.markdown("---")
    st.caption(f"일지 수: {len(st.session_state.journal)}건")
    st.caption(f"ID: `{st.session_state.user_hash[:8]}...`")
    if st.button("🚪 로그아웃"):
        for key in ['authenticated', 'user_hash', 'data_path', 'journal']:
            del st.session_state[key]
        st.rerun()

# ═══════════════════════════════════════════════════════
# 1. 매매일지
# ═══════════════════════════════════════════════════════
if menu == "📝 매매일지":
    st.title("📝 매매일지")
    st.caption("매매 내역을 기록하고 CSV로 저장합니다.")
    st.markdown("---")

    _, col_delete = st.columns([5, 1])
    with col_delete:
        if st.button("🗑️ 전체 초기화"):
            st.session_state.journal = pd.DataFrame(columns=COLUMNS)
            save_journal(st.session_state.journal, DATA_PATH)
            st.rerun()

    with st.form("journal_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            date   = st.date_input("📅 매수일", datetime.now())
            ticker = st.text_input("🏷️ 티커", placeholder="예: AAPL, NVDA").upper()
        with col2:
            price = st.number_input("💵 매수단가 ($)", min_value=0.0, format="%.2f")
            count = st.number_input("🔢 매수 수량 (주)", min_value=0, step=1)
        with col3:
            target = st.number_input("🎯 목표가 ($)", min_value=0.0, format="%.2f")
            period = st.text_input("⏳ 예상 투자기간", placeholder="예: 3년, 장기보유")

        reason    = st.text_area("📌 매수 이유", height=100, placeholder="예: 높은 ROCE, 지속적 FCF 성장, 해자 보유...")
        submitted = st.form_submit_button("💾 일지 저장")

        if submitted:
            if not ticker:
                st.error("티커를 입력해주세요.")
            else:
                new_row = {'매수일': str(date), '티커': ticker, '매수이유': reason,
                           '매수단가': price, '매수갯수': count, '목표가': target, '예상투자기간': period}
                st.session_state.journal = pd.concat(
                    [st.session_state.journal, pd.DataFrame([new_row])], ignore_index=True)
                save_journal(st.session_state.journal, DATA_PATH)
                st.success(f"✅ {ticker} 매매일지가 저장되었습니다!")

    st.markdown("---")
    st.subheader("📋 저장된 일지")
    df_show = st.session_state.journal.copy()
    if df_show.empty:
        st.info("아직 저장된 일지가 없습니다.")
    else:
        df_show.insert(0, '삭제', False)
        edited = st.data_editor(df_show, use_container_width=True, hide_index=True,
                                column_config={'삭제': st.column_config.CheckboxColumn("삭제")})
        if st.button("선택 항목 삭제"):
            st.session_state.journal = edited[~edited['삭제']].drop(columns=['삭제']).reset_index(drop=True)
            save_journal(st.session_state.journal, DATA_PATH)
            st.rerun()

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
        df_j['목표가']   = pd.to_numeric(df_j['목표가'],   errors='coerce').fillna(0)
        df_j['투자금액'] = df_j['매수단가'] * df_j['매수갯수']

        df_p = df_j.groupby('티커').agg(
            매수갯수=('매수갯수', 'sum'), 투자금액=('투자금액', 'sum'), 목표가=('목표가', 'last')
        ).reset_index()
        df_p['평균단가'] = df_p['투자금액'] / df_p['매수갯수'].replace(0, 1)

        with st.spinner('현재가 불러오는 중...'):
            import time
            current_prices, sectors, names = [], [], []
            for i_t, t in enumerate(df_p['티커']):
                for attempt in range(3):
                    try:
                        s      = get_ticker(t)
                        hist   = s.history(period="2d")
                        p      = float(hist['Close'].iloc[-1]) if not hist.empty else 0
                        info_t = s.info
                        current_prices.append(p)
                        sectors.append(info_t.get('sector', 'Unknown'))
                        names.append(info_t.get('shortName', t))
                        if i_t > 0:
                            time.sleep(0.5)
                        break
                    except Exception as e:
                        if 'too many requests' in str(e).lower() or 'rate limit' in str(e).lower():
                            if attempt < 2:
                                time.sleep(5 * (attempt + 1))
                            else:
                                current_prices.append(0); sectors.append('Unknown'); names.append(t)
                        else:
                            current_prices.append(0); sectors.append('Unknown'); names.append(t)
                            break

            df_p['현재가']        = current_prices
            df_p['섹터']          = sectors
            df_p['기업명']        = names
            df_p['평가금액']      = df_p['현재가'] * df_p['매수갯수']
            df_p['수익금']        = df_p['평가금액'] - df_p['투자금액']
            df_p['수익률(%)']     = ((df_p['현재가'] - df_p['평균단가']) / df_p['평균단가'].replace(0,1)) * 100
            df_p['목표가달성률(%)'] = (df_p['현재가'] / df_p['목표가'].replace(0,1)) * 100

        total_invest = df_p['투자금액'].sum()
        total_eval   = df_p['평가금액'].sum()
        total_profit = total_eval - total_invest
        total_return = (total_profit / total_invest * 100) if total_invest > 0 else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 투자금액",  f"${total_invest:,.0f}")
        m2.metric("총 평가금액",  f"${total_eval:,.0f}")
        m3.metric("총 수익금",    f"${total_profit:,.0f}", delta=f"{total_return:.2f}%")
        m4.metric("보유 종목 수", f"{len(df_p)}개")

        st.markdown("---")
        st.subheader("종목별 현황")
        disp = df_p[['티커','기업명','섹터','매수갯수','평균단가','현재가','평가금액','수익률(%)','목표가달성률(%)']].copy()
        st.dataframe(
            disp.style
                .format({'평균단가':'${:.2f}','현재가':'${:.2f}','평가금액':'${:,.0f}',
                         '수익률(%)':'{:.2f}%','목표가달성률(%)':'{:.1f}%'})
                .applymap(lambda v: 'color:#22c55e' if isinstance(v,(int,float)) and v>0
                          else ('color:#ef4444' if isinstance(v,(int,float)) and v<0 else ''), subset=['수익률(%)']),
            use_container_width=True, hide_index=True)

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            fig_pie = px.pie(df_p, values='평가금액', names='티커', title="포트폴리오 비중",
                             color_discrete_sequence=px.colors.sequential.Blues_r, hole=0.45)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf0')
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            fig_bar = px.bar(df_p, x='티커', y='수익률(%)', title="종목별 수익률",
                             color='수익률(%)', color_continuous_scale=['#ef4444','#111827','#22c55e'],
                             color_continuous_midpoint=0, text='수익률(%)')
            fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  font_color='#e8eaf0', yaxis=dict(gridcolor='#1e2a3a'), showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.subheader("📈 주가 추이")
        sel = st.multiselect("비교할 종목 선택", df_p['티커'].tolist(), default=df_p['티커'].tolist()[:3])
        period_opt = st.select_slider("기간", options=["1mo","3mo","6mo","1y","2y","5y"], value="1y")
        if sel:
            hist_data = {t: get_ticker(t).history(period=period_opt)['Close'] for t in sel}
            hist_df   = pd.DataFrame(hist_data)
            fig_line  = go.Figure()
            colors    = ['#3b82f6','#6366f1','#22c55e','#f59e0b','#ef4444','#8b5cf6']
            for i, col in enumerate(hist_df.columns):
                fig_line.add_trace(go.Scatter(x=hist_df.index, y=hist_df[col], name=col,
                                              line=dict(color=colors[i%len(colors)], width=2)))
            fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                   font_color='#e8eaf0', hovermode='x unified',
                                   xaxis=dict(gridcolor='#1e2a3a'), yaxis=dict(gridcolor='#1e2a3a'),
                                   legend=dict(bgcolor='rgba(0,0,0,0)'))
            st.plotly_chart(fig_line, use_container_width=True)

# ═══════════════════════════════════════════════════════
# 3. 기업 원칙 분석
# ═══════════════════════════════════════════════════════
elif menu == "🔍 기업 원칙 분석":
    st.title("🔍 기업 투자 원칙 분석")
    st.caption("7가지 원칙 기반으로 기업의 투자 적합성을 검증합니다.")
    st.markdown("---")

    # ── 종목 리스트 로드 (S&P500 + NASDAQ100 + 다우존스) ─
    @st.cache_data(ttl=86400)
    def load_stock_list():
        stock_dict = {}

        # S&P 500
        try:
            df = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
            for _, row in df.iterrows():
                t = str(row["Symbol"]).replace(".", "-").strip()
                n = str(row["Security"]).strip()
                stock_dict[t] = f"{t} — {n} (S&P500)"
        except:
            pass

        # NASDAQ 100
        try:
            tables = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
            for tbl in tables:
                cols = [str(c).lower() for c in tbl.columns]
                if any("ticker" in c or "symbol" in c for c in cols):
                    ticker_col = next(c for c in tbl.columns if "ticker" in str(c).lower() or "symbol" in str(c).lower())
                    name_col   = next((c for c in tbl.columns if "company" in str(c).lower() or "security" in str(c).lower()), None)
                    for _, row in tbl.iterrows():
                        t = str(row[ticker_col]).strip()
                        n = str(row[name_col]).strip() if name_col else t
                        if t and t != "nan" and 1 <= len(t) <= 6 and t.isalpha():
                            if t not in stock_dict:
                                stock_dict[t] = f"{t} — {n} (NASDAQ100)"
                    break
        except:
            pass

        # 다우존스 30
        try:
            df = pd.read_html("https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average")[1]
            for _, row in df.iterrows():
                t = str(row.get("Symbol", row.get("Ticker", ""))).strip()
                n = str(row.get("Company", row.get("Name", ""))).strip()
                if t and t != "nan" and 1 <= len(t) <= 6:
                    if t not in stock_dict:
                        stock_dict[t] = f"{t} — {n} (DOW30)"
        except:
            pass

        return stock_dict

    with st.spinner("종목 리스트 불러오는 중..."):
        stock_dict = load_stock_list()

    # ── 검색 UI ───────────────────────────────────────
    st.caption(f"✅ 총 **{len(stock_dict):,}개** 종목 (S&P500 + NASDAQ100 + DOW30)")

    col_search, col_btn = st.columns([4, 1])
    with col_search:
        # 티커 직접 입력
        direct_input = st.text_input(
            "⌨️ 티커 직접 입력",
            placeholder="예: INTU, MSFT, AAPL  (모르면 아래 드롭다운 사용)"
        ).upper().strip()

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze = st.button("🔍 분석 시작", use_container_width=True)

    # 드롭다운 검색 (회사명으로 찾기)
    options      = [""] + sorted(stock_dict.values())
    selected_opt = st.selectbox(
        "📋 회사명으로 검색 (드롭다운)",
        options,
        format_func=lambda x: "회사명 또는 티커로 검색..." if x == "" else x
    )

    # 티커 결정: 직접입력 우선, 없으면 드롭다운
    if direct_input:
        target_ticker = direct_input
    elif selected_opt:
        target_ticker = selected_opt.split(" — ")[0].strip()
    else:
        target_ticker = ""

    with st.expander("📖 7가지 투자 원칙 보기"):
        st.markdown("""
| # | 원칙 | 기준 |
|---|------|------|
| 1 | **ROCE** (자본수익률) | 15% 이상 |
| 2 | **매출 성장률** | 3년 평균 7% 이상 |
| 3 | **FCF** (잉여현금흐름) | 3년 연속 양(+) |
| 4 | **부채비율** (D/E) | 1.0 이하 |
| 5 | **영업이익률** | 15% 이상 |
| 6 | **이평선 이격도** | 20일≤5% / 50일≤8% / 200일≤15% |
| 7 | **주주환원율** | 10년물 채권금리 대비 초과 여부 |
        """)

    if target_ticker and analyze:
        with st.spinner(f"{target_ticker} 데이터 불러오는 중..."):
            try:
                # ── 데이터 로드 (지수 백오프 재시도) ────────
                def safe_fetch(fn, label="데이터"):
                    for attempt in range(4):
                        try:
                            result = fn()
                            if result is not None:
                                return result
                        except Exception:
                            pass
                        time.sleep(2 ** attempt)  # 1→2→4→8초
                    st.warning(f"⚠️ {label} 불러오기 실패. 일부 지표가 N/A로 표시됩니다.")
                    return pd.DataFrame()

                stock      = get_ticker(target_ticker)
                info       = safe_fetch(lambda: stock.info,         "기업정보") or {}
                financials = safe_fetch(lambda: stock.financials,   "재무제표")
                balance    = safe_fetch(lambda: stock.balance_sheet,"대차대조표")
                cashflow   = safe_fetch(lambda: stock.cashflow,     "현금흐름표")

                company_name = info.get('shortName', target_ticker)
                sector       = info.get('sector',   'N/A')
                industry     = info.get('industry', 'N/A')
                market_cap   = info.get('marketCap', 0)
                description  = info.get('longBusinessSummary', '')

                st.markdown(f"## {company_name} `{target_ticker}`")
                st.caption(f"섹터: **{sector}** | 업종: **{industry}** | 시가총액: **${market_cap/1e9:.1f}B**")
                if description:
                    with st.expander("기업 소개"):
                        st.write(description[:500] + "...")

                st.markdown("---")
                st.subheader("✅ 투자 원칙 체크리스트")

                results = {}

                # 1. ROCE
                try:
                    ebit = (financials.loc['EBIT'].iloc[0] if 'EBIT' in financials.index
                            else financials.loc['Operating Income'].iloc[0])
                    total_assets = balance.loc['Total Assets'].iloc[0]
                    curr_liab = next((balance.loc[k].iloc[0]
                                      for k in ['Current Liabilities','Total Current Liabilities']
                                      if k in balance.index), 0)
                    cap_emp = total_assets - curr_liab
                    roce    = (ebit / cap_emp) * 100 if cap_emp != 0 else 0
                    results['ROCE'] = {'pass': roce >= 15, 'label': f"{roce:.1f}%",
                                       'desc': "EBIT / (총자산 - 유동부채) | 기준: 15% 이상"}
                except:
                    results['ROCE'] = {'pass': None, 'label': 'N/A', 'desc': "데이터 없음"}

                # 2. 매출 성장률
                try:
                    rev_row = next((financials.loc[k] for k in ['Total Revenue','Revenue']
                                    if k in financials.index), None)
                    if rev_row is not None and len(rev_row) >= 3:
                        rv = rev_row.iloc[:3].values
                        gr = [(rv[i]-rv[i+1])/abs(rv[i+1])*100 for i in range(2) if rv[i+1]!=0]
                        avg_growth = sum(gr)/len(gr) if gr else 0
                    else:
                        avg_growth = 0
                    results['매출성장률'] = {'pass': avg_growth >= 7, 'label': f"{avg_growth:.1f}% (3Y avg)",
                                              'desc': "최근 3년 평균 YoY 매출 성장률 | 기준: 7% 이상"}
                except:
                    results['매출성장률'] = {'pass': None, 'label': 'N/A', 'desc': "데이터 없음"}

                # 3. FCF
                try:
                    fcf_row = next((cashflow.loc[k] for k in ['Free Cash Flow','FreeCashFlow']
                                    if k in cashflow.index), None)
                    if fcf_row is None:
                        op_cf  = cashflow.loc['Operating Cash Flow'].iloc[:3] if 'Operating Cash Flow' in cashflow.index else None
                        capex  = next((cashflow.loc[k].iloc[:3]
                                       for k in ['Capital Expenditure','CapEx','Purchase Of Plant And Equipment']
                                       if k in cashflow.index), None)
                        fcf_vals = (op_cf.values + capex.values) if (op_cf is not None and capex is not None) else []
                    else:
                        fcf_vals = fcf_row.iloc[:3].values

                    if len(fcf_vals) >= 1:
                        all_pos = all(v > 0 for v in fcf_vals)
                        results['FCF'] = {
                            'pass': all_pos,
                            'label': f"${fcf_vals[0]/1e9:.2f}B (최근) | 3년 연속 양(+): {'✓' if all_pos else '✗'}",
                            'desc': "잉여현금흐름 3년 연속 양(+) 여부"}
                    else:
                        results['FCF'] = {'pass': None, 'label': 'N/A', 'desc': "데이터 없음"}
                except:
                    results['FCF'] = {'pass': None, 'label': 'N/A', 'desc': "데이터 없음"}

                # 4. 부채비율
                try:
                    de = info.get('debtToEquity', None)
                    if de is None:
                        debt   = next((balance.loc[k].iloc[0] for k in ['Long Term Debt','Total Debt'] if k in balance.index), None)
                        equity = next((balance.loc[k].iloc[0] for k in ['Stockholders Equity','Total Stockholders Equity','Common Stock Equity'] if k in balance.index), None)
                        de = (debt / equity * 100) if (debt and equity and equity != 0) else 0
                    de_x = de / 100 if de and de > 10 else de
                    results['부채비율'] = {'pass': (de_x <= 1.0) if de_x else None,
                                           'label': f"D/E {de_x:.2f}x" if de_x else 'N/A',
                                           'desc': "부채/자본 비율 | 기준: 1.0 이하"}
                except:
                    results['부채비율'] = {'pass': None, 'label': 'N/A', 'desc': "데이터 없음"}

                # 5. 영업이익률
                try:
                    om = info.get('operatingMargins', None)
                    if om is None:
                        oi  = next((financials.loc[k].iloc[0] for k in ['Operating Income','EBIT'] if k in financials.index), None)
                        rev = next((financials.loc[k].iloc[0] for k in ['Total Revenue','Revenue'] if k in financials.index), None)
                        om  = (oi / rev) if (oi and rev and rev != 0) else 0
                    om_pct = om * 100 if om and abs(om) < 10 else (om or 0)
                    results['영업이익률'] = {'pass': om_pct >= 15, 'label': f"{om_pct:.1f}%",
                                              'desc': "지속 가능한 비즈니스 모델 | 기준: 15% 이상"}
                except:
                    results['영업이익률'] = {'pass': None, 'label': 'N/A', 'desc': "데이터 없음"}

                # 6. 이평선 이격도
                try:
                    hist_1y = stock.history(period="1y")['Close']
                    cur     = float(hist_1y.iloc[-1])
                    ma20    = float(hist_1y.rolling(20).mean().iloc[-1])
                    ma50    = float(hist_1y.rolling(50).mean().iloc[-1])
                    ma200   = float(hist_1y.rolling(200).mean().iloc[-1]) if len(hist_1y) >= 200 else None

                    g20  = abs(cur - ma20) / ma20 * 100
                    g50  = abs(cur - ma50) / ma50 * 100
                    g200 = abs(cur - ma200) / ma200 * 100 if ma200 else None

                    t20  = g20  <= 5
                    t50  = g50  <= 8
                    t200 = (g200 <= 15) if g200 is not None else True

                    results['이평선 이격도'] = {
                        'pass': t20 and t50 and t200,
                        'label': f"20일: {g20:.1f}%{'✓' if t20 else '✗'}  |  50일: {g50:.1f}%{'✓' if t50 else '✗'}  |  200일: {f'{g200:.1f}%' if g200 else 'N/A'}{'✓' if t200 else '✗'}",
                        'desc': "현재가와 이동평균선 이격 | 기준: 20일≤5% / 50일≤8% / 200일≤15% (이격 좁을수록 매수 타이밍)",
                        '_hist': hist_1y,
                        '_ma20':  hist_1y.rolling(20).mean(),
                        '_ma50':  hist_1y.rolling(50).mean(),
                        '_ma200': hist_1y.rolling(200).mean() if len(hist_1y) >= 200 else None,
                    }
                except Exception as e:
                    results['이평선 이격도'] = {'pass': None, 'label': 'N/A', 'desc': f"데이터 없음 ({e})"}

                # 7. 주주환원율 vs 채권금리
                try:
                    # yfinance dividendYield는 소수 비율로 반환 (예: 0.005 = 0.5%)
                    # 단, 간혹 이미 % 형태(예: 0.5)로 반환하는 경우도 있어 1 미만일 때만 ×100
                    raw_div = info.get('dividendYield', 0) or 0
                    div_yield = raw_div * 100 if raw_div < 1 else raw_div

                    # 자사주소각률 = (전년 발행주식수 - 금년 발행주식수) / 전년 발행주식수 × 100
                    # yfinance balance sheet의 'Ordinary Shares Number' 활용
                    buyback_yield = 0
                    try:
                        shares_keys = ['Ordinary Shares Number', 'Share Issued', 'Common Stock']
                        shares_row  = next((balance.loc[k] for k in shares_keys if k in balance.index), None)
                        if shares_row is not None and len(shares_row) >= 2:
                            shares_curr = float(shares_row.iloc[0])  # 금년
                            shares_prev = float(shares_row.iloc[1])  # 전년
                            if shares_prev > 0 and shares_curr < shares_prev:
                                # 주식수가 실제로 줄었을 때만 계산 (소각)
                                buyback_yield = (shares_prev - shares_curr) / shares_prev * 100
                        # balance sheet에 없으면 info의 floatShares / sharesOutstanding 비교
                        if buyback_yield == 0:
                            shares_out = info.get('sharesOutstanding', 0)
                            shares_float = info.get('floatShares', 0)
                            # 연간 주식수 감소율을 yfinance shares_history로 시도
                            try:
                                sh = stock.get_shares_full(start="2022-01-01")
                                if sh is not None and len(sh) >= 2:
                                    sh = sh.dropna().sort_index()
                                    s_latest = float(sh.iloc[-1])
                                    s_year_ago = float(sh.iloc[max(0, len(sh)-252)])  # 약 1년 전
                                    if s_year_ago > 0 and s_latest < s_year_ago:
                                        buyback_yield = (s_year_ago - s_latest) / s_year_ago * 100
                            except:
                                pass
                    except:
                        buyback_yield = 0

                    mkt_cap  = info.get('marketCap', 0)
                    total_sy = div_yield + buyback_yield

                    # 채권 금리
                    bond_rates = {}
                    for bname, bticker in [('미국 10년물','^TNX'), ('회사채(LQD)','LQD'), ('하이일드(HYG)','HYG')]:
                        try:
                            bi   = get_ticker(bticker).info
                            rate = bi.get('regularMarketPrice') or bi.get('previousClose')
                            if bticker != '^TNX' and rate and rate > 10:
                                # LQD/HYG의 경우 yield 필드 사용
                                rate = bi.get('yield') or bi.get('trailingAnnualDividendYield')
                                if rate and rate < 1:
                                    rate = rate * 100
                            bond_rates[bname] = round(float(rate), 2) if rate else None
                        except:
                            bond_rates[bname] = None

                    tnx    = bond_rates.get('미국 10년물')
                    passes = (total_sy > tnx) if tnx else None
                    rate_desc = " | ".join([f"{n}: {r:.2f}%" if r else f"{n}: N/A" for n, r in bond_rates.items()])

                    results['주주환원율'] = {
                        'pass': passes,
                        'label': f"주주환원율 {total_sy:.2f}%  (배당 {div_yield:.2f}% + 자사주소각 {buyback_yield:.2f}%)",
                        'desc': rate_desc + " | 기준: 10년물 금리 초과 여부 | 자사주소각률 = 발행주식수 감소 기준",
                        '_bond_rates': bond_rates,
                        '_total_sy':   total_sy,
                    }
                except Exception as e:
                    results['주주환원율'] = {'pass': None, 'label': 'N/A', 'desc': f"데이터 없음 ({e})"}

                # ── 스코어보드 ────────────────────────────
                pass_c = sum(1 for v in results.values() if v.get('pass') is True)
                fail_c = sum(1 for v in results.values() if v.get('pass') is False)
                na_c   = sum(1 for v in results.values() if v.get('pass') is None)

                s1, s2, s3, s4 = st.columns(4)
                s1.metric("통과 ✅",        f"{pass_c}개")
                s2.metric("미통과 ❌",      f"{fail_c}개")
                s3.metric("데이터 없음 ⚠️", f"{na_c}개")
                s4.metric("종합 점수",      f"{pass_c}/{pass_c+fail_c}점")
                st.markdown("")

                # ── 원칙 카드 ─────────────────────────────
                icons = {'ROCE':'📐','매출성장률':'📈','FCF':'💵','부채비율':'🏦',
                         '영업이익률':'💹','이평선 이격도':'📉','주주환원율':'💰'}
                for name, r in results.items():
                    if r['pass'] is True:
                        cls, tag = "principle-card principle-pass", '<span class="tag tag-pass">PASS ✓</span>'
                    elif r['pass'] is False:
                        cls, tag = "principle-card principle-fail", '<span class="tag tag-fail">FAIL ✗</span>'
                    else:
                        cls, tag = "principle-card principle-warn", '<span class="tag tag-warn">N/A</span>'

                    st.markdown(f"""
                    <div class="{cls}">
                        <div style="display:flex;align-items:center;margin-bottom:4px;">
                            <span style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;">
                                {icons.get(name,'•')} {name}
                            </span>{tag}
                        </div>
                        <div style="font-family:'Space Mono',monospace;font-size:1.05rem;color:#e8eaf0;margin-bottom:4px;">
                            {r['label']}
                        </div>
                        <div style="font-size:0.78rem;color:#7a8499;">{r['desc']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # ── 이평선 차트 ───────────────────────────
                st.markdown("---")
                st.subheader("📉 이동평균선 차트")
                ir = results.get('이평선 이격도', {})
                if '_hist' in ir:
                    fig_ma = go.Figure()
                    fig_ma.add_trace(go.Scatter(x=ir['_hist'].index, y=ir['_hist'].values,
                                                name='주가', line=dict(color='#e8eaf0', width=1.5)))
                    fig_ma.add_trace(go.Scatter(x=ir['_ma20'].index, y=ir['_ma20'].values,
                                                name='MA20', line=dict(color='#3b82f6', width=1.5, dash='dot')))
                    fig_ma.add_trace(go.Scatter(x=ir['_ma50'].index, y=ir['_ma50'].values,
                                                name='MA50', line=dict(color='#f59e0b', width=1.5, dash='dot')))
                    if ir['_ma200'] is not None:
                        fig_ma.add_trace(go.Scatter(x=ir['_ma200'].index, y=ir['_ma200'].values,
                                                    name='MA200', line=dict(color='#ef4444', width=1.5, dash='dot')))
                    fig_ma.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                         font_color='#e8eaf0', hovermode='x unified', height=350,
                                         xaxis=dict(gridcolor='#1e2a3a'), yaxis=dict(gridcolor='#1e2a3a'),
                                         legend=dict(bgcolor='rgba(0,0,0,0)'))
                    st.plotly_chart(fig_ma, use_container_width=True)

                # ── 주주환원율 vs 채권금리 차트 ───────────
                st.subheader("💰 주주환원율 vs 채권금리")
                sr = results.get('주주환원율', {})
                if '_bond_rates' in sr:
                    br  = sr['_bond_rates']
                    sy  = sr['_total_sy']
                    lbs = ['주주환원율'] + [k for k, v in br.items() if v is not None]
                    vls = [sy]           + [v for v in br.values()   if v is not None]
                    fig_bond = go.Figure(go.Bar(
                        x=lbs, y=vls,
                        marker_color=['#3b82f6'] + ['#4b5563']*(len(lbs)-1),
                        text=[f"{v:.2f}%" for v in vls], textposition='outside'
                    ))
                    fig_bond.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                           font_color='#e8eaf0', yaxis=dict(gridcolor='#1e2a3a', title='금리 (%)'),
                                           showlegend=False, height=300)
                    st.plotly_chart(fig_bond, use_container_width=True)
                    st.caption("💡 주주환원율(배당+자사주매입)이 채권금리보다 높을수록 주식 투자 매력 ↑")

                # ── 3개년 재무 추세 ───────────────────────
                st.markdown("---")
                st.subheader("📊 3개년 재무 추세")
                try:
                    rev_c = next((financials.loc[k] for k in ['Total Revenue','Revenue'] if k in financials.index), None)
                    op_c  = next((financials.loc[k] for k in ['Operating Income','EBIT'] if k in financials.index), None)
                    fcf_c = next((cashflow.loc[k]   for k in ['Free Cash Flow']           if k in cashflow.index),  None)

                    cdata, years = {}, []
                    if rev_c is not None:
                        cdata['매출 ($B)']     = (rev_c.iloc[:4]/1e9).values[::-1]
                        years                  = [str(d.year) for d in rev_c.index[:4]][::-1]
                    if op_c  is not None: cdata['영업이익 ($B)'] = (op_c.iloc[:4]/1e9).values[::-1]
                    if fcf_c is not None: cdata['FCF ($B)']      = (fcf_c.iloc[:4]/1e9).values[::-1]

                    if cdata and years:
                        cdf      = pd.DataFrame(cdata, index=years)
                        fig_trend = go.Figure()
                        cmap = {'매출 ($B)':'#3b82f6','영업이익 ($B)':'#22c55e','FCF ($B)':'#f59e0b'}
                        for col in cdf.columns:
                            fig_trend.add_trace(go.Bar(name=col, x=cdf.index, y=cdf[col],
                                                       marker_color=cmap.get(col,'#6366f1')))
                        fig_trend.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)',
                                                plot_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf0',
                                                xaxis=dict(gridcolor='#1e2a3a'), yaxis=dict(gridcolor='#1e2a3a'),
                                                legend=dict(bgcolor='rgba(0,0,0,0)'))
                        st.plotly_chart(fig_trend, use_container_width=True)
                except Exception as e:
                    st.warning(f"재무 추세 차트 생성 실패: {e}")

                # ── 종합 판정 ─────────────────────────────
                st.markdown("---")
                if pass_c >= 6:
                    st.success(f"🟢 **{company_name}** — {pass_c}/7개 원칙 충족. 투자 원칙에 **강하게 부합**합니다.")
                elif pass_c >= 4:
                    st.warning(f"🟡 **{company_name}** — {pass_c}/7개 원칙 충족. 추가 검토를 권장합니다.")
                else:
                    st.error(f"🔴 **{company_name}** — {pass_c}/7개 원칙 충족. 투자 원칙에 **미달**합니다.")

            except Exception as e:
                st.error(f"데이터를 불러오지 못했습니다: {e}")
                st.caption("티커가 올바른지 확인해주세요.")
