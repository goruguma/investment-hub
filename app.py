import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# yfinance import (Streamlit Cloud에서 정상 작동)
try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

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
# 파스텔 CSS
# ══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

[data-testid="stAppViewContainer"] { background: #faf8f5; color: #3d3530; }
[data-testid="stSidebar"]          { background: #f5f0ea; border-right: 1px solid #e8e0d5; }
[data-testid="stSidebar"] *        { color: #5a4f47 !important; }

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'DM Serif Display', serif !important; color: #3d3530 !important; }
h1 { font-size: 2rem !important; }
h2 { font-size: 1.4rem !important; }

[data-testid="stMetric"] {
    background: white; border: 1px solid #ece6de;
    border-radius: 16px; padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(180,160,140,0.08);
}
[data-testid="stMetricLabel"] { color: #9c8878 !important; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600; }
[data-testid="stMetricValue"] { color: #3d3530 !important; font-family: 'DM Serif Display', serif !important; font-size: 1.7rem !important; }

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: white !important; border: 1.5px solid #e0d6cc !important;
    color: #3d3530 !important; border-radius: 10px !important;
}

[data-testid="stFormSubmitButton"] button, .stButton button {
    background: linear-gradient(135deg, #f4a58a, #e8856a) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    box-shadow: 0 2px 8px rgba(244,165,138,0.35) !important;
}

hr { border-color: #ece6de !important; }

[data-testid="stSuccess"] { background: #f0faf4 !important; border-left: 4px solid #6dbf8a !important; border-radius: 10px; }
[data-testid="stInfo"]    { background: #f0f6ff !important; border-left: 4px solid #7ab8f5 !important; border-radius: 10px; }
[data-testid="stWarning"] { background: #fffbf0 !important; border-left: 4px solid #f5c842 !important; border-radius: 10px; }
[data-testid="stError"]   { background: #fff5f5 !important; border-left: 4px solid #f5877a !important; border-radius: 10px; }

[data-testid="stDataFrame"] { border: 1px solid #ece6de; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(180,160,140,0.08); }
[data-testid="stExpander"]  { background: white; border: 1px solid #ece6de !important; border-radius: 12px !important; }

.sidebar-logo { font-family: 'DM Serif Display', serif; font-size: 1.4rem; color: #e8856a !important; }

.p-card { background: white; border: 1px solid #ece6de; border-radius: 14px; padding: 16px 20px; margin-bottom: 10px; box-shadow: 0 2px 6px rgba(180,160,140,0.07); }
.p-pass { border-left: 4px solid #6dbf8a; }
.p-fail { border-left: 4px solid #f5877a; }
.p-warn { border-left: 4px solid #f5c842; }

.tag { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.7rem; font-weight: 700; margin-left: 8px; letter-spacing: 0.5px; }
.tag-pass { background: #edfaf2; color: #2d8a52; border: 1px solid #a8ddb8; }
.tag-fail { background: #fff0ef; color: #c0392b; border: 1px solid #f5b3ae; }
.tag-warn { background: #fefce8; color: #927a10; border: 1px solid #f0d87a; }

.block-container { padding-top: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# 데이터 경로 & 유틸
# ══════════════════════════════════════════
JOURNAL_COLS  = ['매수일','티커','매수이유','매수단가','매수갯수','목표가','예상투자기간']
ANALYSIS_COLS = ['분석일','티커','기업명','ROCE','매출성장률','FCF여부','부채비율DE',
                 '영업이익률','이평선이격','주주환원율','채권금리','메모','종합점수']

JOURNAL_PATH  = "data/journal.csv"
ANALYSIS_PATH = "data/analysis.csv"

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
# 세션 초기화 (앱 시작 시 1회)
# ══════════════════════════════════════════
if 'loaded' not in st.session_state:
    st.session_state.journal  = load_csv(JOURNAL_PATH,  JOURNAL_COLS)
    st.session_state.analysis = load_csv(ANALYSIS_PATH, ANALYSIS_COLS)
    st.session_state.loaded   = True

# ══════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-logo">📈 Investment Hub</div>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.selectbox("", ["📝 매매일지","📊 포트폴리오","🔍 기업 원칙 분석"],
                        label_visibility="collapsed")
    st.markdown("---")
    st.caption(f"일지 {len(st.session_state.journal)}건")
    st.caption(f"분석 {len(st.session_state.analysis)}건")

# ══════════════════════════════════════════
# yfinance 헬퍼 함수
# ══════════════════════════════════════════
def safe_val(val, default=0.0):
    """None/NaN 안전 처리"""
    try:
        v = float(val)
        return v if v == v else default  # NaN 체크
    except:
        return default

def fetch_financials(ticker_sym):
    """yfinance로 7가지 원칙 수치 자동 계산"""
    result = {
        'company_name': '', 'sector': '', 'industry': '',
        'roce': 0.0, 'revenue_growth': 0.0, 'fcf_positive': False,
        'de_ratio': 0.0, 'op_margin': 0.0, 'ma_gap': 0.0,
        'shareholder_yield': 0.0, 'div_yield': 0.0, 'buyback_yield': 0.0,
        'current_price': 0.0, 'error': None
    }
    try:
        t = yf.Ticker(ticker_sym)

        # 기본 정보
        info = t.info
        result['company_name'] = info.get('shortName', ticker_sym)
        result['sector']       = info.get('sector', 'N/A')
        result['industry']     = info.get('industry', 'N/A')
        result['current_price'] = safe_val(info.get('currentPrice') or info.get('regularMarketPrice'))

        # 재무제표
        fin = t.financials       # 손익계산서 (연간)
        bal = t.balance_sheet    # 대차대조표 (연간)
        cf  = t.cashflow         # 현금흐름표 (연간)

        # ── 1. ROCE ──────────────────────────────
        try:
            ebit_keys = ['EBIT', 'Operating Income']
            ebit = 0
            for k in ebit_keys:
                if k in fin.index:
                    ebit = safe_val(fin.loc[k].iloc[0])
                    break

            total_assets  = safe_val(bal.loc['Total Assets'].iloc[0]) if 'Total Assets' in bal.index else 0
            curr_liab_keys = ['Current Liabilities', 'Total Current Liabilities']
            curr_liab = 0
            for k in curr_liab_keys:
                if k in bal.index:
                    curr_liab = safe_val(bal.loc[k].iloc[0])
                    break

            cap_employed = total_assets - curr_liab
            result['roce'] = (ebit / cap_employed * 100) if cap_employed != 0 else 0
        except:
            result['roce'] = safe_val(info.get('returnOnEquity', 0)) * 100

        # ── 2. 매출 성장률 (3년 평균) ─────────────
        try:
            rev_keys = ['Total Revenue', 'Revenue']
            rev_row = None
            for k in rev_keys:
                if k in fin.index:
                    rev_row = fin.loc[k]
                    break
            if rev_row is not None and len(rev_row) >= 2:
                revs = [safe_val(rev_row.iloc[i]) for i in range(min(4, len(rev_row)))]
                gr = [(revs[i]-revs[i+1])/abs(revs[i+1])*100
                      for i in range(len(revs)-1) if revs[i+1] != 0]
                result['revenue_growth'] = sum(gr)/len(gr) if gr else 0
            else:
                result['revenue_growth'] = safe_val(info.get('revenueGrowth', 0)) * 100
        except:
            result['revenue_growth'] = safe_val(info.get('revenueGrowth', 0)) * 100

        # ── 3. FCF 3년 연속 양(+) ────────────────
        try:
            fcf_keys = ['Free Cash Flow', 'FreeCashFlow']
            fcf_row = None
            for k in fcf_keys:
                if k in cf.index:
                    fcf_row = cf.loc[k]
                    break
            if fcf_row is None:
                op_cf_keys = ['Operating Cash Flow', 'Total Cash From Operating Activities']
                capex_keys = ['Capital Expenditure', 'Capital Expenditures']
                op_cf, capex = None, None
                for k in op_cf_keys:
                    if k in cf.index: op_cf = cf.loc[k]; break
                for k in capex_keys:
                    if k in cf.index: capex = cf.loc[k]; break
                if op_cf is not None and capex is not None:
                    fcf_vals = [safe_val(op_cf.iloc[i]) + safe_val(capex.iloc[i])
                                for i in range(min(3, len(op_cf)))]
                else:
                    fcf_vals = []
            else:
                fcf_vals = [safe_val(fcf_row.iloc[i]) for i in range(min(3, len(fcf_row)))]

            result['fcf_positive'] = bool(fcf_vals) and all(v > 0 for v in fcf_vals)
        except:
            result['fcf_positive'] = safe_val(info.get('freeCashflow', 0)) > 0

        # ── 4. 부채비율 D/E ───────────────────────
        try:
            de = info.get('debtToEquity')
            if de is not None:
                result['de_ratio'] = safe_val(de) / 100
            else:
                debt_keys   = ['Total Debt', 'Long Term Debt']
                equity_keys = ['Total Stockholder Equity', 'Stockholders Equity',
                               'Total Stockholders Equity', 'Common Stock Equity']
                debt, equity = 0, 0
                for k in debt_keys:
                    if k in bal.index: debt = safe_val(bal.loc[k].iloc[0]); break
                for k in equity_keys:
                    if k in bal.index: equity = safe_val(bal.loc[k].iloc[0]); break
                result['de_ratio'] = (debt / equity) if equity != 0 else 0
        except:
            result['de_ratio'] = safe_val(info.get('debtToEquity', 0)) / 100

        # ── 5. 영업이익률 ────────────────────────
        try:
            om = info.get('operatingMargins')
            if om is not None:
                result['op_margin'] = safe_val(om) * 100
            else:
                op_keys  = ['Operating Income', 'EBIT']
                rev_keys2 = ['Total Revenue', 'Revenue']
                op_inc, rev = 0, 0
                for k in op_keys:
                    if k in fin.index: op_inc = safe_val(fin.loc[k].iloc[0]); break
                for k in rev_keys2:
                    if k in fin.index: rev = safe_val(fin.loc[k].iloc[0]); break
                result['op_margin'] = (op_inc / rev * 100) if rev != 0 else 0
        except:
            result['op_margin'] = safe_val(info.get('operatingMargins', 0)) * 100

        # ── 6. 이평선 이격도 (MA20) ───────────────
        try:
            hist = t.history(period="3mo")
            if not hist.empty and len(hist) >= 20:
                prices   = hist['Close']
                cur_p    = float(prices.iloc[-1])
                ma20     = float(prices.rolling(20).mean().iloc[-1])
                result['ma_gap'] = abs(cur_p - ma20) / ma20 * 100
                if result['current_price'] == 0:
                    result['current_price'] = cur_p
        except:
            result['ma_gap'] = 0

        # ── 7. 주주환원율 (배당 + 자사주소각) ──────
        try:
            # 배당수익률
            div_yield = safe_val(info.get('dividendYield', 0))
            div_yield_pct = div_yield * 100 if div_yield < 1 else div_yield
            result['div_yield'] = div_yield_pct

            # 자사주소각률 (가중평균 주식수 YoY 감소)
            bb_pct = 0.0
            wt_keys = ['Diluted Average Shares', 'Weighted Average Shares',
                       'Basic Average Shares', 'Ordinary Shares Number']
            wt_row = None
            for k in wt_keys:
                if k in fin.index: wt_row = fin.loc[k]; break
            if wt_row is not None and len(wt_row) >= 2:
                sh_now  = safe_val(wt_row.iloc[0])
                sh_prev = safe_val(wt_row.iloc[1])
                if sh_prev > 0 and sh_now < sh_prev:
                    bb_pct = (sh_prev - sh_now) / sh_prev * 100
            result['buyback_yield']      = bb_pct
            result['shareholder_yield']  = div_yield_pct + bb_pct
        except:
            result['div_yield']          = safe_val(info.get('dividendYield', 0)) * 100
            result['shareholder_yield']  = result['div_yield']

    except Exception as e:
        result['error'] = str(e)

    return result

# ══════════════════════════════════════════
# 1. 매매일지
# ══════════════════════════════════════════
if menu == "📝 매매일지":
    st.title("📝 매매일지")
    st.caption("매매 내역을 기록하고 관리합니다.")
    st.markdown("---")

    with st.form("jform", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            j_date   = st.date_input("📅 매수일", datetime.now())
            j_ticker = st.text_input("🏷️ 티커", placeholder="예: AAPL").upper()
        with c2:
            j_price = st.number_input("💵 매수단가 ($)", min_value=0.0, format="%.2f")
            j_count = st.number_input("🔢 수량 (주)", min_value=0, step=1)
        with c3:
            j_target = st.number_input("🎯 목표가 ($)", min_value=0.0, format="%.2f")
            j_period = st.text_input("⏳ 투자기간", placeholder="예: 3년, 장기보유")
        j_reason = st.text_area("📌 매수 이유", height=90,
                                placeholder="예: ROCE 20% 이상, FCF 3년 연속 양(+), 해자 보유...")
        if st.form_submit_button("💾 저장", use_container_width=True):
            if not j_ticker:
                st.error("티커를 입력해주세요.")
            else:
                row = {'매수일':str(j_date), '티커':j_ticker, '매수이유':j_reason,
                       '매수단가':j_price, '매수갯수':j_count,
                       '목표가':j_target, '예상투자기간':j_period}
                st.session_state.journal = pd.concat(
                    [st.session_state.journal, pd.DataFrame([row])], ignore_index=True)
                save_csv(st.session_state.journal, JOURNAL_PATH)
                st.success(f"✅ {j_ticker} 저장 완료!")

    st.markdown("---")
    st.subheader("📋 저장된 일지")

    if st.session_state.journal.empty:
        st.info("아직 작성된 일지가 없습니다.")
    else:
        df_view = st.session_state.journal.copy()
        df_view.insert(0, '삭제', False)
        edited = st.data_editor(df_view, use_container_width=True, hide_index=True,
                                column_config={'삭제': st.column_config.CheckboxColumn("🗑️")})
        col_del, col_dl = st.columns([1, 4])
        with col_del:
            if st.button("선택 삭제", use_container_width=True):
                st.session_state.journal = (
                    edited[~edited['삭제']].drop(columns=['삭제']).reset_index(drop=True))
                save_csv(st.session_state.journal, JOURNAL_PATH)
                st.rerun()
        with col_dl:
            csv_b = st.session_state.journal.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("⬇️ CSV 다운로드", csv_b, "journal.csv", "text/csv",
                               use_container_width=True)

# ══════════════════════════════════════════
# 2. 포트폴리오
# ══════════════════════════════════════════
elif menu == "📊 포트폴리오":
    st.title("📊 포트폴리오 현황")
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

        # 현재가 입력 (수동)
        st.subheader("💵 현재가 입력")
        price_cols = st.columns(min(len(df_p), 4))
        cur_prices = {}
        for i, row in df_p.iterrows():
            col_idx = i % min(len(df_p), 4)
            with price_cols[col_idx]:
                default_p = st.session_state.get(f"cp_{row['티커']}", float(row['평균단가']))
                cur_prices[row['티커']] = st.number_input(
                    f"**{row['티커']}** ($)", value=default_p,
                    min_value=0.0, format="%.2f",
                    key=f"price_input_{row['티커']}")

        if st.button("📊 계산하기", use_container_width=True):
            for t, p in cur_prices.items():
                st.session_state[f"cp_{t}"] = p

        st.markdown("---")

        df_p['현재가'] = df_p['티커'].map(
            {t: st.session_state.get(f"cp_{t}", float(df_p[df_p['티커']==t]['평균단가'].iloc[0]))
             for t in df_p['티커']})
        df_p['평가금액']        = df_p['현재가'] * df_p['매수갯수']
        df_p['수익금']          = df_p['평가금액'] - df_p['투자금액']
        df_p['수익률(%)']       = ((df_p['현재가']-df_p['평균단가']) / df_p['평균단가'].replace(0,1)) * 100
        df_p['목표가달성률(%)'] = (df_p['현재가'] / df_p['목표가'].replace(0,1)) * 100

        ti = df_p['투자금액'].sum(); te = df_p['평가금액'].sum()
        tp = te - ti; tr = (tp/ti*100) if ti > 0 else 0

        m1,m2,m3,m4 = st.columns(4)
        m1.metric("총 투자금액",  f"${ti:,.0f}")
        m2.metric("총 평가금액",  f"${te:,.0f}")
        m3.metric("총 수익금",    f"${tp:+,.0f}", delta=f"{tr:+.2f}%")
        m4.metric("보유 종목",    f"{len(df_p)}개")

        st.markdown("---")
        disp = df_p[['티커','매수갯수','평균단가','현재가','평가금액','수익률(%)','목표가달성률(%)']].copy()
        st.dataframe(
            disp.style
            .format({'평균단가':'${:.2f}','현재가':'${:.2f}','평가금액':'${:,.0f}',
                     '수익률(%)':'{:+.2f}%','목표가달성률(%)':'{:.1f}%'})
            .applymap(lambda v: 'color:#2d8a52;font-weight:600' if isinstance(v,(int,float)) and v>0
                      else ('color:#c0392b;font-weight:600' if isinstance(v,(int,float)) and v<0 else ''),
                      subset=['수익률(%)']),
            use_container_width=True, hide_index=True)

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            fig_pie = px.pie(df_p, values='평가금액', names='티커', title="포트폴리오 비중",
                             color_discrete_sequence=['#f4a58a','#a8d8b9','#93c5e8','#f5c842','#c4b5f4','#f9a8d4'],
                             hole=0.42)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans',color='#3d3530'),
                                  legend=dict(bgcolor='rgba(0,0,0,0)'))
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            clrs = ['#6dbf8a' if v >= 0 else '#f5877a' for v in df_p['수익률(%)']]
            fig_bar = go.Figure(go.Bar(x=df_p['티커'], y=df_p['수익률(%)'], marker_color=clrs,
                                       text=[f"{v:+.1f}%" for v in df_p['수익률(%)']],
                                       textposition='outside'))
            fig_bar.update_layout(title="종목별 수익률", paper_bgcolor='rgba(0,0,0,0)',
                                  plot_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans',color='#3d3530'),
                                  yaxis=dict(gridcolor='#ece6de', zerolinecolor='#d4c9bc'), showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

# ══════════════════════════════════════════
# 3. 기업 원칙 분석
# ══════════════════════════════════════════
elif menu == "🔍 기업 원칙 분석":
    st.title("🔍 기업 투자 원칙 분석")
    st.caption("티커를 입력하면 yfinance로 7가지 원칙 수치를 자동으로 불러옵니다.")
    st.markdown("---")

    with st.expander("📖 7가지 투자 원칙 기준"):
        st.markdown("""
| # | 원칙 | 기준 |
|---|------|------|
| 1 | **ROCE** (자본수익률) | 15% 이상 |
| 2 | **매출 성장률** | 연평균 7% 이상 |
| 3 | **FCF** (잉여현금흐름) | 3년 연속 양(+) |
| 4 | **부채비율** D/E | 1.0 이하 |
| 5 | **영업이익률** | 15% 이상 |
| 6 | **이평선 이격도** | MA20 이격 5% 이내 |
| 7 | **주주환원율** | 배당+자사주소각률 > 10년물 금리 |
        """)

    # ── 티커 입력 & 자동 조회 ─────────────────
    st.subheader("🔎 종목 검색")
    col_t, col_b, col_bond = st.columns([3, 1, 2])
    with col_t:
        input_ticker = st.text_input("티커 입력", placeholder="예: AAPL, MSFT, NVDA, INTU").upper().strip()
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        fetch_btn = st.button("📥 자동 조회", use_container_width=True)
    with col_bond:
        bond_rate = st.number_input("🏦 미국 10년물 금리 (%)", min_value=0.0,
                                    value=4.5, format="%.2f",
                                    help="현재 미국 10년물 국채 금리를 직접 입력하세요")

    # 자동 조회
    if fetch_btn and input_ticker:
        if not YF_AVAILABLE:
            st.error("yfinance 라이브러리가 설치되지 않았습니다. requirements.txt를 확인해주세요.")
        else:
            with st.spinner(f"📊 {input_ticker} 데이터 조회 중..."):
                fetched = fetch_financials(input_ticker)

            if fetched.get('error'):
                st.error(f"❌ 데이터 조회 실패: {fetched['error'][:100]}")
                st.info("💡 티커가 정확한지 확인하거나 수치를 직접 입력해주세요.")
            else:
                st.session_state['fetched'] = fetched
                st.session_state['fetched_ticker'] = input_ticker
                st.success(f"✅ {fetched.get('company_name', input_ticker)} 데이터 조회 완료!")

    # ── 분석 입력 폼 ──────────────────────────
    st.markdown("---")
    st.subheader("📝 원칙 분석 입력")
    st.caption("자동 조회 후 수치가 채워집니다. 필요시 직접 수정하세요.")

    # 자동 조회된 값 가져오기
    fd = st.session_state.get('fetched', {})
    ft = st.session_state.get('fetched_ticker', '')

    with st.form("aform", clear_on_submit=False):
        ca1, ca2 = st.columns(2)
        with ca1:
            a_date   = st.date_input("📅 분석일", datetime.now())
            a_ticker = st.text_input("🏷️ 티커",
                                     value=ft if ft else (input_ticker if input_ticker else ""))
            a_name   = st.text_input("🏢 기업명",
                                     value=fd.get('company_name', ''))
        with ca2:
            st.markdown(f"**현재 입력된 채권금리: {bond_rate:.2f}%**")
            st.caption(f"섹터: {fd.get('sector','—')} | 업종: {fd.get('industry','—')}")
            if fd.get('current_price', 0) > 0:
                st.caption(f"현재가: ${fd.get('current_price', 0):.2f}")

        st.markdown("---")
        st.markdown("**7가지 원칙 수치** (자동 조회 후 자동 입력 · 직접 수정 가능)")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            a_roce   = st.number_input("① ROCE (%)",
                                       value=round(fd.get('roce', 0.0), 1),
                                       format="%.1f",
                                       help="EBIT / (총자산 - 유동부채) × 100 | 기준: 15% 이상")
            a_margin = st.number_input("⑤ 영업이익률 (%)",
                                       value=round(fd.get('op_margin', 0.0), 1),
                                       format="%.1f",
                                       help="영업이익 / 매출액 × 100 | 기준: 15% 이상")
        with col2:
            a_growth = st.number_input("② 매출성장률 (%)",
                                       value=round(fd.get('revenue_growth', 0.0), 1),
                                       format="%.1f",
                                       help="최근 3년 평균 YoY 매출 성장률 | 기준: 7% 이상")
            a_gap    = st.number_input("⑥ MA20 이격도 (%)",
                                       value=round(fd.get('ma_gap', 0.0), 1),
                                       min_value=0.0, format="%.1f",
                                       help="|(현재가 - MA20) / MA20| × 100 | 기준: 5% 이내")
        with col3:
            fcf_default = "예 ✓" if fd.get('fcf_positive', False) else "아니오 ✗"
            a_fcf    = st.selectbox("③ FCF 3년 연속 양(+)?",
                                    ["예 ✓", "아니오 ✗"],
                                    index=0 if fd.get('fcf_positive', False) else 1,
                                    help="잉여현금흐름 3년 연속 양(+) 여부")
            a_sr     = st.number_input("⑦ 주주환원율 (%)",
                                       value=round(fd.get('shareholder_yield', 0.0), 2),
                                       min_value=0.0, format="%.2f",
                                       help=f"배당({fd.get('div_yield',0):.2f}%) + 자사주소각({fd.get('buyback_yield',0):.2f}%) | 기준: 채권금리({bond_rate:.2f}%) 초과")
        with col4:
            a_de     = st.number_input("④ 부채비율 D/E (배)",
                                       value=round(max(fd.get('de_ratio', 0.0), 0.0), 2),
                                       min_value=0.0, format="%.2f",
                                       help="총부채 / 총자본 | 기준: 1.0 이하")
            a_memo   = st.text_area("📌 메모", height=80,
                                    placeholder="추가 투자 근거 또는 메모...")

        if st.form_submit_button("🔍 분석 저장", use_container_width=True):
            ticker_val = a_ticker.strip().upper()
            if not ticker_val:
                st.error("티커를 입력해주세요.")
            else:
                checks = {
                    'ROCE':     a_roce   >= 15,
                    '매출성장률': a_growth >= 7,
                    'FCF':      a_fcf == "예 ✓",
                    '부채비율':  a_de    <= 1.0,
                    '영업이익률': a_margin >= 15,
                    '이평선':   a_gap   <= 5,
                    '주주환원율': a_sr    > bond_rate,
                }
                score = sum(checks.values())

                row = {
                    '분석일': str(a_date), '티커': ticker_val, '기업명': a_name,
                    'ROCE': round(a_roce,1), '매출성장률': round(a_growth,1),
                    'FCF여부': "예" if a_fcf=="예 ✓" else "아니오",
                    '부채비율DE': round(a_de,2), '영업이익률': round(a_margin,1),
                    '이평선이격': round(a_gap,1), '주주환원율': round(a_sr,2),
                    '채권금리': round(bond_rate,2), '메모': a_memo,
                    '종합점수': f"{score}/7"
                }
                st.session_state.analysis = pd.concat(
                    [st.session_state.analysis, pd.DataFrame([row])], ignore_index=True)
                save_csv(st.session_state.analysis, ANALYSIS_PATH)

                # 결과 카드 표시
                st.markdown("---")
                st.markdown(f"### {a_name or ticker_val} `{ticker_val}` 분석 결과")

                s1,s2,s3,s4 = st.columns(4)
                s1.metric("통과 ✅", f"{score}개")
                s2.metric("미통과 ❌", f"{7-score}개")
                s3.metric("종합 점수", f"{score}/7점")
                s4.metric("채권금리 기준", f"{bond_rate:.2f}%")
                st.markdown("")

                principles = [
                    ("📐","ROCE",         f"{a_roce:.1f}%",                    checks['ROCE'],     "기준: 15% 이상"),
                    ("📈","매출 성장률",   f"{a_growth:.1f}% (3Y avg)",         checks['매출성장률'], "기준: 연평균 7% 이상"),
                    ("💵","FCF",          a_fcf,                               checks['FCF'],      "기준: 3년 연속 양(+)"),
                    ("🏦","부채비율 D/E", f"{a_de:.2f}x",                      checks['부채비율'],   "기준: 1.0 이하"),
                    ("💹","영업이익률",   f"{a_margin:.1f}%",                   checks['영업이익률'], "기준: 15% 이상"),
                    ("📉","이평선 이격도",f"MA20 이격 {a_gap:.1f}%",            checks['이평선'],    "기준: 5% 이내"),
                    ("💰","주주환원율",   f"{a_sr:.2f}% vs 채권 {bond_rate:.2f}%", checks['주주환원율'], "기준: 채권금리 초과"),
                ]
                for icon, name, val, passed, desc in principles:
                    cls = "p-card p-pass" if passed else "p-card p-fail"
                    tag = '<span class="tag tag-pass">PASS ✓</span>' if passed else '<span class="tag tag-fail">FAIL ✗</span>'
                    st.markdown(f"""
                    <div class="{cls}">
                        <div style="display:flex;align-items:center;margin-bottom:4px;">
                            <span style="font-family:'DM Serif Display',serif;font-size:1rem;">
                                {icon} {name}</span>{tag}
                        </div>
                        <div style="font-size:1.05rem;color:#3d3530;margin-bottom:3px;font-weight:600;">{val}</div>
                        <div style="font-size:0.78rem;color:#9c8878;">{desc}</div>
                    </div>""", unsafe_allow_html=True)

                if score >= 6:
                    st.success(f"🟢 **{a_name or ticker_val}** — {score}/7개 원칙 충족. 투자 원칙에 **강하게 부합**합니다.")
                elif score >= 4:
                    st.warning(f"🟡 **{a_name or ticker_val}** — {score}/7개 원칙 충족. 추가 검토를 권장합니다.")
                else:
                    st.error(f"🔴 **{a_name or ticker_val}** — {score}/7개 원칙 충족. 투자 원칙에 **미달**합니다.")

                # 세션 초기화
                st.session_state.pop('fetched', None)
                st.session_state.pop('fetched_ticker', None)

    # ── 저장된 분석 이력 ──────────────────────
    st.markdown("---")
    st.subheader("📋 분석 이력")

    if st.session_state.analysis.empty:
        st.info("아직 저장된 분석이 없습니다.")
    else:
        df_a = st.session_state.analysis.copy()

        def score_color(v):
            try:
                n = int(str(v).split('/')[0])
                if n >= 6: return 'color:#2d8a52;font-weight:700'
                if n >= 4: return 'color:#927a10;font-weight:700'
                return 'color:#c0392b;font-weight:700'
            except: return ''

        st.dataframe(df_a.style.applymap(score_color, subset=['종합점수']),
                     use_container_width=True, hide_index=True)

        # 레이더 차트
        if len(df_a) >= 1:
            st.markdown("---")
            st.subheader("📊 원칙 달성률 레이더 차트")
            compare_list = st.multiselect(
                "비교할 기업 선택",
                df_a['티커'].tolist(),
                default=df_a['티커'].tolist()[-min(3,len(df_a)):]
            )
            if compare_list:
                fig_radar = go.Figure()
                cats = ['ROCE\n≥15%','매출성장률\n≥7%','FCF\n양(+)',
                        '부채비율\n≤1.0','영업이익률\n≥15%','이평선\n≤5%','주주환원율\n>채권금리']
                colors = ['#f4a58a','#6dbf8a','#93c5e8','#c4b5f4','#f5c842','#f9a8d4','#a8d8b9']

                for i, t in enumerate(compare_list):
                    rows = df_a[df_a['티커']==t]
                    if rows.empty: continue
                    r = rows.iloc[-1]

                    def to_score(val, thr, invert=False):
                        try:
                            v = float(val)
                            return 100 if ((v<=thr) if invert else (v>=thr)) else max(5, min(90, v/thr*85))
                        except: return 0

                    bond = float(r.get('채권금리', 4.5) or 4.5)
                    vals = [
                        to_score(r.get('ROCE',0), 15),
                        to_score(r.get('매출성장률',0), 7),
                        100 if str(r.get('FCF여부',''))=='예' else 5,
                        to_score(r.get('부채비율DE',99), 1.0, invert=True),
                        to_score(r.get('영업이익률',0), 15),
                        to_score(r.get('이평선이격',99), 5.0, invert=True),
                        100 if float(r.get('주주환원율',0) or 0) > bond else 5,
                    ]
                    v_closed = vals + [vals[0]]
                    c_closed = cats  + [cats[0]]
                    clr = colors[i % len(colors)]

                    fig_radar.add_trace(go.Scatterpolar(
                        r=v_closed, theta=c_closed,
                        fill='toself', name=t,
                        line_color=clr,
                        fillcolor=clr + '40'
                    ))

                fig_radar.update_layout(
                    polar=dict(
                        bgcolor='white',
                        radialaxis=dict(visible=True, range=[0,100],
                                        tickfont=dict(size=9, color='#9c8878'),
                                        gridcolor='#ece6de'),
                        angularaxis=dict(gridcolor='#e8e0d5', linecolor='#d4c9bc')
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='DM Sans', color='#3d3530', size=11),
                    legend=dict(bgcolor='rgba(255,255,255,0.9)',
                                bordercolor='#ece6de', borderwidth=1),
                    height=440, margin=dict(t=40)
                )
                st.plotly_chart(fig_radar, use_container_width=True)
                st.caption("💡 100점 = 원칙 완전 충족. 면적이 넓을수록 투자 원칙에 부합합니다.")

        col_adel, col_adl = st.columns([1,4])
        with col_adel:
            if st.button("🗑️ 전체 삭제", use_container_width=True):
                st.session_state.analysis = pd.DataFrame(columns=ANALYSIS_COLS)
                save_csv(st.session_state.analysis, ANALYSIS_PATH)
                st.rerun()
        with col_adl:
            a_csv = st.session_state.analysis.to_csv(
                index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("⬇️ 분석 이력 CSV 다운로드", a_csv, "analysis.csv",
                               "text/csv", use_container_width=True)
