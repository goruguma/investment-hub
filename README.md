# 📈 My Investment Hub

매매일지 작성 · 포트폴리오 관리 · 기업 투자 원칙 분석 앱

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## 🚀 배포 방법 (GitHub + Streamlit Cloud)

### 1단계: GitHub 레포지터리 생성

```bash
# 로컬에서
git init
git add .
git commit -m "init: Investment Hub"

# GitHub에서 새 레포 만든 후
git remote add origin https://github.com/[내아이디]/investment-hub.git
git push -u origin main
```

### 2단계: Streamlit Cloud 배포

1. [share.streamlit.io](https://share.streamlit.io) 접속
2. **New app** 클릭
3. GitHub 계정 연동
4. Repository: `investment-hub` 선택
5. Branch: `main`
6. Main file path: `app.py`
7. **Deploy!** 클릭

---

## 📁 파일 구조

```
investment-hub/
├── app.py              # 메인 앱
├── requirements.txt    # 패키지 목록
├── data/
│   └── journal.csv     # 매매일지 데이터 (자동 생성)
└── README.md
```

> ⚠️ **주의**: `data/journal.csv`는 Streamlit Cloud에서 앱 재시작 시 초기화됩니다.
> 영구 저장을 원하면 CSV 다운로드 버튼으로 백업하거나 Google Sheets 연동을 추가하세요.

---

## ✨ 주요 기능

### 📝 매매일지
- 매수일, 티커, 매수단가, 수량, 목표가, 예상기간, 매수이유 기록
- CSV 저장 및 다운로드
- 개별/전체 삭제

### 📊 포트폴리오 현황
- yfinance 기반 실시간 현재가 반영
- 가중평균 단가 자동 계산
- 수익률, 평가금액, 섹터 분석
- 주가 추이 비교 차트

### 🔍 기업 투자 원칙 분석 (5가지 원칙)
| # | 원칙 | 기준 |
|---|------|------|
| 1 | ROCE (자본수익률) | 15% 이상 |
| 2 | 매출 성장률 | 3년 평균 7% 이상 |
| 3 | FCF (잉여현금흐름) | 3년 연속 양(+) |
| 4 | 부채비율 (D/E) | 1.0 이하 |
| 5 | 영업이익률 | 15% 이상 |

---

## 🛠 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```
