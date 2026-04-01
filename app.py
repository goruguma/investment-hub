import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import hashlib
import time
import requests

# ─────────────────────────────────────────
# FMP API 설정
# ─────────────────────────────────────────
FMP_BASE = "https://financialmodelingprep.com/api"

def get_api_key():
    try:
        return st.secrets["FMP_API_KEY"]
    except:
        return None

def fmp(endpoint, params=None, ver=3):
    """FMP API 호출 헬퍼"""
    key = get_api_key()
    if not key:
        return None
    p = {"apikey": key}
    if params:
        p.update(params)
    try:
        r = requests.get(f"{FMP_BASE}/v{ver}/{endpoint}", params=p, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                return data
            if isinstance(data, dict) and data:
                return data
        return None
    except:
        return None

# ─────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────
st.set_page_config(page_title="My Investment Hub", page_icon="📈", layout="wide")

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');
[data-testid="stAppViewContainer"] { background: #0a0e1a; color: #e8eaf0; }
[data-testid="stSidebar"] { background: #0d1221; border-right: 1px solid #1e2a3a; }
[data-testid="stSidebar"] * { color: #c8cdd8 !important; }
h1,h2,h3 { font-family:'Syne',sans-serif !important; color:#e8eaf0 !important; }
h1 { font-weight:800; font-size:2rem !important; }
h2 { font-weight:600; font-size:1.4rem !important; }
[data-testid="stMetric"] { background:#111827; border:1px solid #1e2a3a; border-radius:12px; padding:16px 20px; }
[data-testid="stMetricLabel"] { color:#7a8499 !important; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; }
[data-testid="stMetricValue"] { color:#e8eaf0 !important; font-family:'Space Mono',monospace !important; font-size:1.6rem !important; }
[data-testid="stDataFrame"] { border:1px solid #1e2a3a; border-radius:12px; overflow:hidden; }
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stTextArea"] textarea {
    background:#111827 !important; border:1px solid #1e2a3a !important; color:#e8eaf0 !important; border-radius:8px !important; }
[data-testid="stFormSubmitButton"] button,.stButton button {
    background:linear-gradient(135deg,#3b82f6,#6366f1) !important; color:white !important;
    border:none !important; border-radius:8px !important; font-family:'Space Mono',monospace !important;
    font-weight:700 !important; padding:0.5rem 1.5rem !important; }
hr { border-color:#1e2a3a !important; }
[data-testid="stSelectbox"] > div { background:#111827 !important; border:1px solid #1e2a3a !important; border-radius:8px !important; }
[data-testid="stSuccess"] { background:#0d2a1a !important; border-left:3px solid #22c55e !important; border-radius:8px; }
[data-testid="stInfo"]    { background:#0d1a2a !important; border-left:3px solid #3b82f6 !important; border-radius:8px; }
[data-testid="stWarning"] { background:#2a1a0d !important; border-left:3px solid #f59e0b !important; border-radius:8px; }
.sidebar-title { font-family:'Syne',sans-serif; font-weight:800; font-size:1.3rem; color:#3b82f6 !important; }
.principle-card { background:#111827; border:1px solid #1e2a3a; border-radius:12px; padding:16px 20px; margin-bottom:10px; }
.principle-pass { border-left:4px solid #22c55e; }
.principle-fail { border-left:4px solid #ef4444; }
.principle-warn { border-left:4px solid #f59e0b; }
.tag { display:inline-block; padding:2px 10px; border-radius:999px; font-size:0.72rem; font-family:'Space Mono',monospace; font-weight:700; margin-left:8px; }
.tag-pass { background:#0d2a1a; color:#22c55e; border:1px solid #22c55e; }
.tag-fail { background:#2a0d0d; color:#ef4444; border:1px solid #ef4444; }
.tag-warn { background:#2a1a0d; color:#f59e0b; border:1px solid #f59e0b; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 비밀번호 기반 사용자 분리
# ─────────────────────────────────────────
COLUMNS = ['매수일','티커','매수이유','매수단가','매수갯수','목표가','예상투자기간']

def get_user_hash(pw): return hashlib.sha256(pw.encode()).hexdigest()[:16]
def get_data_path(h):  return f"data/journal_{h}.csv"

def load_journal(path):
    if os.path.exists(path):
        df = pd.read_csv(path)
        for col in COLUMNS:
            if col not in df.columns: df[col] = ""
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)

def save_journal(df, path):
    os.makedirs("data", exist_ok=True)
    df.to_csv(path, index=False, encoding='utf-8-sig')

# ─────────────────────────────────────────
# 로그인
# ─────────────────────────────────────────
if 'authenticated' not in st.session_state:
    st.session_state.update(authenticated=False, user_hash=None, data_path=None, journal=None)

if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1,2,1])
    with col_m:
        st.markdown("""
        <div style="background:#111827;border:1px solid #1e2a3a;border-radius:16px;padding:40px 36px;text-align:center;">
            <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.8rem;color:#3b82f6;margin-bottom:8px;">📈 Investment Hub</div>
            <div style="font-size:0.85rem;color:#7a8499;">나만의 비밀번호로 개인 데이터 공간에 접속하세요</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("login_form"):
            pw = st.text_input("🔑 비밀번호", type="password", placeholder="4자 이상")
            if st.form_submit_button("입장하기", use_container_width=True):
                if len(pw) < 4:
                    st.error("비밀번호는 4자 이상입니다.")
                else:
                    h = get_user_hash(pw)
                    p = get_data_path(h)
                    st.session_state.update(authenticated=True, user_hash=h, data_path=p, journal=load_journal(p))
                    st.rerun()
        st.caption("💡 처음 입력하는 비밀번호로 새 공간이 자동 생성됩니다.")
        st.caption("⚠️ 비밀번호를 잊으면 데이터를 복구할 수 없습니다.")
    st.stop()

DATA_PATH = st.session_state.data_path

# ─────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">📈 Investment Hub</div>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.selectbox("메뉴", ["📝 매매일지","📊 포트폴리오","🔍 기업 원칙 분석"], label_visibility="collapsed")
    st.markdown("---")
    st.caption(f"일지 수: {len(st.session_state.journal)}건")
    st.caption(f"ID: `{st.session_state.user_hash[:8]}...`")
    if st.button("🚪 로그아웃"):
        for k in ['authenticated','user_hash','data_path','journal']: del st.session_state[k]
        st.rerun()

# API키 확인
if get_api_key() is None:
    st.error("⚠️ FMP API 키가 설정되지 않았습니다. Streamlit Secrets에 FMP_API_KEY를 등록해주세요.")
    st.stop()

# ═══════════════════════════════════════════════════════
# 1. 매매일지
# ═══════════════════════════════════════════════════════
if menu == "📝 매매일지":
    st.title("📝 매매일지")
    st.caption("매매 내역을 기록하고 CSV로 저장합니다.")
    st.markdown("---")

    _, col_del = st.columns([5,1])
    with col_del:
        if st.button("🗑️ 전체 초기화"):
            st.session_state.journal = pd.DataFrame(columns=COLUMNS)
            save_journal(st.session_state.journal, DATA_PATH)
            st.rerun()

    with st.form("journal_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            date   = st.date_input("📅 매수일", datetime.now())
            ticker = st.text_input("🏷️ 티커", placeholder="예: AAPL, NVDA").upper()
        with c2:
            price = st.number_input("💵 매수단가 ($)", min_value=0.0, format="%.2f")
            count = st.number_input("🔢 수량 (주)", min_value=0, step=1)
        with c3:
            target = st.number_input("🎯 목표가 ($)", min_value=0.0, format="%.2f")
            period = st.text_input("⏳ 예상 투자기간", placeholder="예: 3년, 장기보유")
        reason = st.text_area("📌 매수 이유", height=100)
        if st.form_submit_button("💾 일지 저장"):
            if not ticker:
                st.error("티커를 입력해주세요.")
            else:
                new_row = {'매수일':str(date),'티커':ticker,'매수이유':reason,
                           '매수단가':price,'매수갯수':count,'목표가':target,'예상투자기간':period}
                st.session_state.journal = pd.concat(
                    [st.session_state.journal, pd.DataFrame([new_row])], ignore_index=True)
                save_journal(st.session_state.journal, DATA_PATH)
                st.success(f"✅ {ticker} 저장 완료!")

    st.markdown("---")
    st.subheader("📋 저장된 일지")
    if st.session_state.journal.empty:
        st.info("아직 저장된 일지가 없습니다.")
    else:
        df_show = st.session_state.journal.copy()
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
    st.markdown("---")

    df_j = st.session_state.journal.copy()
    if df_j.empty:
        st.info("매매일지를 먼저 작성해주세요.")
    else:
        for col in ['매수단가','매수갯수','목표가']:
            df_j[col] = pd.to_numeric(df_j[col], errors='coerce').fillna(0)
        df_j['투자금액'] = df_j['매수단가'] * df_j['매수갯수']

        df_p = df_j.groupby('티커').agg(
            매수갯수=('매수갯수','sum'), 투자금액=('투자금액','sum'), 목표가=('목표가','last')
        ).reset_index()
        df_p['평균단가'] = df_p['투자금액'] / df_p['매수갯수'].replace(0,1)

        with st.spinner("현재가 불러오는 중... (FMP API)"):
            prices, sectors, names = [], [], []
            for t in df_p['티커']:
                try:
                    data = fmp(f"quote/{t}")
                    if data:
                        prices.append(float(data[0].get('price', 0)))
                        sectors.append(data[0].get('exchange', 'N/A'))
                        names.append(data[0].get('name', t))
                    else:
                        prices.append(0); sectors.append('N/A'); names.append(t)
                except:
                    prices.append(0); sectors.append('N/A'); names.append(t)

            df_p['현재가']   = prices
            df_p['섹터']     = sectors
            df_p['기업명']   = names
            df_p['평가금액'] = df_p['현재가'] * df_p['매수갯수']
            df_p['수익금']   = df_p['평가금액'] - df_p['투자금액']
            df_p['수익률(%)'] = ((df_p['현재가'] - df_p['평균단가']) / df_p['평균단가'].replace(0,1)) * 100
            df_p['목표가달성률(%)'] = (df_p['현재가'] / df_p['목표가'].replace(0,1)) * 100

        ti = df_p['투자금액'].sum(); te = df_p['평가금액'].sum()
        tp = te - ti; tr = (tp/ti*100) if ti > 0 else 0

        m1,m2,m3,m4 = st.columns(4)
        m1.metric("총 투자금액", f"${ti:,.0f}")
        m2.metric("총 평가금액", f"${te:,.0f}")
        m3.metric("총 수익금",   f"${tp:,.0f}", delta=f"{tr:.2f}%")
        m4.metric("보유 종목",   f"{len(df_p)}개")

        st.markdown("---")
        disp = df_p[['티커','기업명','섹터','매수갯수','평균단가','현재가','평가금액','수익률(%)','목표가달성률(%)']].copy()
        st.dataframe(disp.style.format({
            '평균단가':'${:.2f}','현재가':'${:.2f}','평가금액':'${:,.0f}',
            '수익률(%)':'{:.2f}%','목표가달성률(%)':'{:.1f}%'
        }).applymap(lambda v: 'color:#22c55e' if isinstance(v,(int,float)) and v>0
                    else ('color:#ef4444' if isinstance(v,(int,float)) and v<0 else ''),
                    subset=['수익률(%)']), use_container_width=True, hide_index=True)

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(df_p, values='평가금액', names='티커', title="포트폴리오 비중",
                         color_discrete_sequence=px.colors.sequential.Blues_r, hole=0.45)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf0')
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.bar(df_p, x='티커', y='수익률(%)', title="종목별 수익률",
                          color='수익률(%)', color_continuous_scale=['#ef4444','#111827','#22c55e'],
                          color_continuous_midpoint=0, text='수익률(%)')
            fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font_color='#e8eaf0', yaxis=dict(gridcolor='#1e2a3a'), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        # 주가 추이
        st.markdown("---")
        st.subheader("📈 주가 추이")
        sel = st.multiselect("비교 종목", df_p['티커'].tolist(), default=df_p['티커'].tolist()[:3])
        period_map = {"1개월":"1month","3개월":"3months","6개월":"6months","1년":"1year","2년":"2years","5년":"5years"}
        period_label = st.select_slider("기간", options=list(period_map.keys()), value="1년")
        period_val = period_map[period_label]

        if sel:
            fig3 = go.Figure()
            colors = ['#3b82f6','#6366f1','#22c55e','#f59e0b','#ef4444','#8b5cf6']
            for i, t in enumerate(sel):
                try:
                    data = fmp(f"historical-price-full/{t}", {"serietype":"line","timeseries":
                               {"1month":30,"3months":90,"6months":180,"1year":365,"2years":730,"5years":1825}[period_val]})
                    if data and 'historical' in data:
                        hist = pd.DataFrame(data['historical'])
                        hist['date'] = pd.to_datetime(hist['date'])
                        hist = hist.sort_values('date')
                        fig3.add_trace(go.Scatter(x=hist['date'], y=hist['close'], name=t,
                                                  line=dict(color=colors[i%len(colors)], width=2)))
                except:
                    pass
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font_color='#e8eaf0', hovermode='x unified',
                               xaxis=dict(gridcolor='#1e2a3a'), yaxis=dict(gridcolor='#1e2a3a'),
                               legend=dict(bgcolor='rgba(0,0,0,0)'))
            st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════
# 3. 기업 원칙 분석
# ═══════════════════════════════════════════════════════
elif menu == "🔍 기업 원칙 분석":
    st.title("🔍 기업 투자 원칙 분석")
    st.caption("7가지 원칙 기반으로 기업의 투자 적합성을 검증합니다.")
    st.markdown("---")

    # 종목 검색 리스트
    @st.cache_data(ttl=86400)
    def load_stock_list():
        stock_dict = {}
        try:
            df = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
            for _, row in df.iterrows():
                t = str(row["Symbol"]).replace(".", "-").strip()
                n = str(row["Security"]).strip()
                stock_dict[t] = f"{t} — {n} (S&P500)"
        except: pass
        try:
            tables = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
            for tbl in tables:
                cols = [str(c).lower() for c in tbl.columns]
                if any("ticker" in c or "symbol" in c for c in cols):
                    tc = next(c for c in tbl.columns if "ticker" in str(c).lower() or "symbol" in str(c).lower())
                    nc = next((c for c in tbl.columns if "company" in str(c).lower()), None)
                    for _, row in tbl.iterrows():
                        t = str(row[tc]).strip()
                        n = str(row[nc]).strip() if nc else t
                        if t and t != "nan" and 1 <= len(t) <= 6 and t.replace("-","").isalpha():
                            if t not in stock_dict:
                                stock_dict[t] = f"{t} — {n} (NASDAQ100)"
                    break
        except: pass
        try:
            df2 = pd.read_html("https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average")[1]
            for _, row in df2.iterrows():
                t = str(row.get("Symbol", row.get("Ticker",""))).strip()
                n = str(row.get("Company", row.get("Name",""))).strip()
                if t and t != "nan" and 1 <= len(t) <= 5:
                    if t not in stock_dict:
                        stock_dict[t] = f"{t} — {n} (DOW30)"
        except: pass
        return stock_dict

    with st.spinner("종목 리스트 불러오는 중..."):
        stock_dict = load_stock_list()

    st.caption(f"✅ 총 **{len(stock_dict):,}개** 종목 (S&P500 + NASDAQ100 + DOW30) | 목록에 없으면 직접 입력")

    col_inp, col_btn = st.columns([4,1])
    with col_inp:
        direct = st.text_input("⌨️ 티커 직접 입력", placeholder="예: INTU, MSFT, AAPL").upper().strip()
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze = st.button("🔍 분석 시작", use_container_width=True)

    options = [""] + sorted(stock_dict.values())
    selected = st.selectbox("📋 회사명으로 검색 (드롭다운)",options,
                            format_func=lambda x: "회사명 또는 티커로 검색..." if x=="" else x)

    target_ticker = direct if direct else (selected.split(" — ")[0].strip() if selected else "")

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
| 7 | **주주환원율** | 배당+자사주소각률 > 10년물 금리 |
        """)

    if target_ticker and analyze:
        with st.spinner(f"📊 {target_ticker} 분석 중..."):

            # ── 데이터 수집 ───────────────────────────
            profile    = fmp(f"profile/{target_ticker}")
            income_st  = fmp(f"income-statement/{target_ticker}",  {"limit":4})
            balance_st = fmp(f"balance-sheet-statement/{target_ticker}", {"limit":4})
            cashflow_st= fmp(f"cash-flow-statement/{target_ticker}",{"limit":4})
            quote      = fmp(f"quote/{target_ticker}")
            hist_data  = fmp(f"historical-price-full/{target_ticker}", {"serietype":"line","timeseries":365})
            shares_hist= fmp(f"historical/shares_float/{target_ticker}")

            if not profile:
                st.error(f"❌ '{target_ticker}' 데이터를 찾을 수 없습니다. 티커를 확인해주세요.")
                st.stop()

            p   = profile[0]
            inc = income_st  or []
            bal = balance_st or []
            cf  = cashflow_st or []
            q   = quote[0] if quote else {}

            company_name = p.get('companyName', target_ticker)
            sector       = p.get('sector', 'N/A')
            industry     = p.get('industry', 'N/A')
            mkt_cap      = p.get('mktCap', 0)
            description  = p.get('description', '')

            st.markdown(f"## {company_name} `{target_ticker}`")
            st.caption(f"섹터: **{sector}** | 업종: **{industry}** | 시가총액: **${mkt_cap/1e9:.1f}B**")
            if description:
                with st.expander("기업 소개"):
                    st.write(description[:500] + "...")

            st.markdown("---")
            st.subheader("✅ 투자 원칙 체크리스트")

            results = {}

            # 1. ROCE
            try:
                ebit      = inc[0].get('operatingIncome', 0)
                tot_asset = bal[0].get('totalAssets', 0)
                curr_liab = bal[0].get('totalCurrentLiabilities', 0)
                cap_emp   = tot_asset - curr_liab
                roce      = (ebit / cap_emp * 100) if cap_emp else 0
                results['ROCE'] = {'pass': roce >= 15, 'label': f"{roce:.1f}%",
                                   'desc': "EBIT / (총자산 - 유동부채) | 기준: 15% 이상"}
            except:
                results['ROCE'] = {'pass': None, 'label': 'N/A', 'desc': "데이터 없음"}

            # 2. 매출 성장률
            try:
                revs = [x.get('revenue', 0) for x in inc[:3]]
                if len(revs) >= 2 and revs[1]:
                    gr = [(revs[i]-revs[i+1])/abs(revs[i+1])*100 for i in range(len(revs)-1) if revs[i+1]]
                    avg_g = sum(gr)/len(gr) if gr else 0
                else:
                    avg_g = 0
                results['매출성장률'] = {'pass': avg_g >= 7, 'label': f"{avg_g:.1f}% (3Y avg)",
                                         'desc': "최근 3년 평균 YoY 매출 성장률 | 기준: 7% 이상"}
            except:
                results['매출성장률'] = {'pass': None, 'label': 'N/A', 'desc': "데이터 없음"}

            # 3. FCF
            try:
                fcfs     = [x.get('freeCashFlow', 0) for x in cf[:3]]
                all_pos  = all(v > 0 for v in fcfs) if fcfs else False
                fcf_last = fcfs[0]/1e9 if fcfs else 0
                results['FCF'] = {
                    'pass': all_pos,
                    'label': f"${fcf_last:.2f}B (최근) | 3년 연속 양(+): {'✓' if all_pos else '✗'}",
                    'desc': "잉여현금흐름 3년 연속 양(+) 여부"}
            except:
                results['FCF'] = {'pass': None, 'label': 'N/A', 'desc': "데이터 없음"}

            # 4. 부채비율 D/E
            try:
                debt   = bal[0].get('totalDebt', 0)
                equity = bal[0].get('totalStockholdersEquity', 0)
                de     = (debt / equity) if equity else 0
                results['부채비율'] = {'pass': de <= 1.0, 'label': f"D/E {de:.2f}x",
                                       'desc': "부채 / 자본 | 기준: 1.0 이하"}
            except:
                results['부채비율'] = {'pass': None, 'label': 'N/A', 'desc': "데이터 없음"}

            # 5. 영업이익률
            try:
                op_margin = inc[0].get('operatingIncomeRatio', 0) * 100
                results['영업이익률'] = {'pass': op_margin >= 15, 'label': f"{op_margin:.1f}%",
                                         'desc': "지속 가능한 비즈니스 모델 | 기준: 15% 이상"}
            except:
                results['영업이익률'] = {'pass': None, 'label': 'N/A', 'desc': "데이터 없음"}

            # 6. 이평선 이격도
            try:
                if hist_data and 'historical' in hist_data:
                    hist_df = pd.DataFrame(hist_data['historical'])
                    hist_df['date']  = pd.to_datetime(hist_df['date'])
                    hist_df = hist_df.sort_values('date').reset_index(drop=True)
                    prices_s = hist_df['close']
                    cur_p    = float(prices_s.iloc[-1])
                    ma20     = float(prices_s.rolling(20).mean().iloc[-1])
                    ma50     = float(prices_s.rolling(50).mean().iloc[-1])
                    ma200    = float(prices_s.rolling(200).mean().iloc[-1]) if len(prices_s)>=200 else None
                    g20  = abs(cur_p-ma20)/ma20*100
                    g50  = abs(cur_p-ma50)/ma50*100
                    g200 = abs(cur_p-ma200)/ma200*100 if ma200 else None
                    t20  = g20 <= 5; t50 = g50 <= 8; t200 = (g200 <= 15) if g200 else True
                    results['이평선 이격도'] = {
                        'pass': t20 and t50 and t200,
                        'label': f"20일:{g20:.1f}%{'✓' if t20 else '✗'} | 50일:{g50:.1f}%{'✓' if t50 else '✗'} | 200일:{f'{g200:.1f}%' if g200 else 'N/A'}{'✓' if t200 else '✗'}",
                        'desc': "현재가 vs 이동평균선 이격 | 기준: 20일≤5% / 50일≤8% / 200일≤15%",
                        '_hist': hist_df, '_prices': prices_s}
                else:
                    results['이평선 이격도'] = {'pass': None, 'label': 'N/A', 'desc': "주가 데이터 없음"}
            except Exception as e:
                results['이평선 이격도'] = {'pass': None, 'label': 'N/A', 'desc': f"데이터 없음"}

            # 7. 주주환원율 vs 채권금리
            try:
                # 배당수익률
                div_yield = (p.get('lastDiv', 0) or 0)
                cur_price = q.get('price', 1) or 1
                div_yield_pct = (div_yield / cur_price) * 100

                # 자사주소각률 (발행주식수 감소 기준)
                buyback_pct = 0
                if shares_hist and len(shares_hist) >= 2:
                    sh = sorted(shares_hist, key=lambda x: x.get('date',''), reverse=True)
                    s_now  = float(sh[0].get('floatShares', 0) or 0)
                    s_prev = float(sh[-1].get('floatShares', 0) or 0)
                    if s_prev > 0 and s_now < s_prev:
                        buyback_pct = (s_prev - s_now) / s_prev * 100

                total_sy = div_yield_pct + buyback_pct

                # 채권금리 (FMP)
                bond_rates = {}
                tnx = fmp("quote/%5ETNX")
                if tnx: bond_rates['미국 10년물'] = round(float(tnx[0].get('price', 0)), 2)

                lqd = fmp("etf-holdings/LQD")
                if not lqd:
                    bond_rates['회사채(LQD)'] = None
                else:
                    lqd_q = fmp("quote/LQD")
                    bond_rates['회사채(LQD)'] = round(float((lqd_q[0].get('dividendYield') or 0)*100), 2) if lqd_q else None

                hyg_q = fmp("quote/HYG")
                bond_rates['하이일드(HYG)'] = round(float((hyg_q[0].get('dividendYield') or 0)*100), 2) if hyg_q else None

                tnx_rate = bond_rates.get('미국 10년물')
                passes   = (total_sy > tnx_rate) if tnx_rate else None
                rate_desc = " | ".join([f"{n}: {r:.2f}%" if r else f"{n}: N/A" for n,r in bond_rates.items()])

                results['주주환원율'] = {
                    'pass': passes,
                    'label': f"주주환원율 {total_sy:.2f}% (배당 {div_yield_pct:.2f}% + 자사주소각 {buyback_pct:.2f}%)",
                    'desc': rate_desc + " | 기준: 10년물 금리 초과 여부",
                    '_bond_rates': bond_rates, '_total_sy': total_sy}
            except:
                results['주주환원율'] = {'pass': None, 'label': 'N/A', 'desc': "데이터 없음"}

            # ── 스코어보드 ────────────────────────────
            pass_c = sum(1 for v in results.values() if v.get('pass') is True)
            fail_c = sum(1 for v in results.values() if v.get('pass') is False)
            na_c   = sum(1 for v in results.values() if v.get('pass') is None)

            s1,s2,s3,s4 = st.columns(4)
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
                            {icons.get(name,'•')} {name}</span>{tag}
                    </div>
                    <div style="font-family:'Space Mono',monospace;font-size:1.05rem;color:#e8eaf0;margin-bottom:4px;">
                        {r['label']}</div>
                    <div style="font-size:0.78rem;color:#7a8499;">{r['desc']}</div>
                </div>""", unsafe_allow_html=True)

            # ── 이평선 차트 ───────────────────────────
            st.markdown("---")
            st.subheader("📉 이동평균선 차트")
            ir = results.get('이평선 이격도', {})
            if '_prices' in ir:
                ps  = ir['_prices']
                hdf = ir['_hist']
                fig_ma = go.Figure()
                fig_ma.add_trace(go.Scatter(x=hdf['date'], y=ps.values, name='주가',
                                            line=dict(color='#e8eaf0', width=1.5)))
                fig_ma.add_trace(go.Scatter(x=hdf['date'], y=ps.rolling(20).mean().values,
                                            name='MA20', line=dict(color='#3b82f6', width=1.5, dash='dot')))
                fig_ma.add_trace(go.Scatter(x=hdf['date'], y=ps.rolling(50).mean().values,
                                            name='MA50', line=dict(color='#f59e0b', width=1.5, dash='dot')))
                if len(ps) >= 200:
                    fig_ma.add_trace(go.Scatter(x=hdf['date'], y=ps.rolling(200).mean().values,
                                                name='MA200', line=dict(color='#ef4444', width=1.5, dash='dot')))
                fig_ma.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                     font_color='#e8eaf0', hovermode='x unified', height=350,
                                     xaxis=dict(gridcolor='#1e2a3a'), yaxis=dict(gridcolor='#1e2a3a'),
                                     legend=dict(bgcolor='rgba(0,0,0,0)'))
                st.plotly_chart(fig_ma, use_container_width=True)
            else:
                st.info("이평선 데이터를 불러올 수 없습니다.")

            # ── 주주환원율 vs 채권금리 차트 ───────────
            st.subheader("💰 주주환원율 vs 채권금리")
            sr = results.get('주주환원율', {})
            if '_bond_rates' in sr:
                br  = sr['_bond_rates']
                sy  = sr['_total_sy']
                lbs = ['주주환원율'] + [k for k,v in br.items() if v is not None]
                vls = [sy]           + [v for v in br.values() if v is not None]
                fig_bond = go.Figure(go.Bar(x=lbs, y=vls,
                    marker_color=['#3b82f6']+['#4b5563']*(len(lbs)-1),
                    text=[f"{v:.2f}%" for v in vls], textposition='outside'))
                fig_bond.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                       font_color='#e8eaf0', yaxis=dict(gridcolor='#1e2a3a',title='금리 (%)'),
                                       showlegend=False, height=300)
                st.plotly_chart(fig_bond, use_container_width=True)
                st.caption("💡 주주환원율(배당+자사주소각)이 채권금리보다 높을수록 주식 투자 매력 ↑")

            # ── 3개년 재무 추세 ───────────────────────
            st.markdown("---")
            st.subheader("📊 3개년 재무 추세")
            if inc:
                years  = [x.get('calendarYear','') for x in inc[:4]][::-1]
                revs   = [x.get('revenue',0)/1e9 for x in inc[:4]][::-1]
                op_inc = [x.get('operatingIncome',0)/1e9 for x in inc[:4]][::-1]
                fcfs_c = [x.get('freeCashFlow',0)/1e9 for x in (cf[:4] if cf else inc[:4])][::-1]
                fig_trend = go.Figure()
                for label, vals, color in [('매출($B)', revs,'#3b82f6'),
                                            ('영업이익($B)', op_inc,'#22c55e'),
                                            ('FCF($B)', fcfs_c,'#f59e0b')]:
                    fig_trend.add_trace(go.Bar(name=label, x=years, y=vals, marker_color=color))
                fig_trend.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf0',
                                        xaxis=dict(gridcolor='#1e2a3a'), yaxis=dict(gridcolor='#1e2a3a'),
                                        legend=dict(bgcolor='rgba(0,0,0,0)'))
                st.plotly_chart(fig_trend, use_container_width=True)

            # ── 종합 판정 ─────────────────────────────
            st.markdown("---")
            if pass_c >= 6:
                st.success(f"🟢 **{company_name}** — {pass_c}/7개 원칙 충족. 투자 원칙에 **강하게 부합**합니다.")
            elif pass_c >= 4:
                st.warning(f"🟡 **{company_name}** — {pass_c}/7개 원칙 충족. 추가 검토를 권장합니다.")
            else:
                st.error(f"🔴 **{company_name}** — {pass_c}/7개 원칙 충족. 투자 원칙에 **미달**합니다.")
