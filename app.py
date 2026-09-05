import urllib.parse
import feedparser
import pandas as pd
import streamlit as st
import yfinance as yf

# 페이지 설정 (와이드 모드)
st.set_page_config(
    page_title="AFK Market Intelligence Desk", page_icon="📈", layout="wide"
)

# 커스텀 CSS (프로페셔널 금융 다크/라이트 밸런스 스타일)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    .main-header { background-color: #0f172a; padding: 20px; border-radius: 8px; color: #38bdf8; font-weight: 900; font-size: 24px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .sub-header { font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 10px; border-left: 4px solid #38bdf8; padding-left: 8px; }
    .headline-box { background-color: #f1f5f9; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #0f172a; border: 1px solid #e2e8f0; margin-bottom: 8px; }
    .alert-box { background-color: #fef2f2; border: 1px solid #fecaca; color: #991b1b; padding: 12px; border-radius: 6px; margin-bottom: 15px; font-weight: 600; }
    .safe-box { background-color: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 12px; border-radius: 6px; margin-bottom: 15px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 세션 상태 초기화 (내 관심 종목 리스트용)
if "watchlist" not in st.session_state:
  st.session_state.watchlist = ["TSLA", "AAPL", "NVDA", "005930.KS", "000660.KS"]

# 상단 배너
st.markdown("""
    <div class="main-header">
        <span>📈 AFK MARKET INTELLIGENCE DESK</span>
        <span style="font-size: 13px; background-color: #38bdf8; color: #0f172a; padding: 4px 10px; border-radius: 4px; font-weight: 700;">INVESTMENT TERMINAL v1.0</span>
    </div>
""", unsafe_allow_html=True)

# 화면 분할: 좌측(지수, 매크로, 관심종목, 뉴스), 우측(금융 퀵링크, 관심종목 관리 메모)
col_left, col_right = st.columns([3, 1])

with col_right:
  # 1. 필수 금융/증권 퀵링크
  st.markdown(
      '<div class="card"><div class="sub-header">🔗 금융 및 투자 퀵링크</div>',
      unsafe_allow_html=True,
  )
  st.markdown("- [네이버 증권](https://finance.naver.com)")
  st.markdown("- [인베스팅닷컴 (Investing)](https://www.investing.com)")
  st.markdown(
      "- [한경 마켓인사이트](https://marketinsight.hankyung.com)"
  )
  st.markdown("- [미국 인베스팅 (US Markets)](https://www.investing.com/indices)")
  st.markdown("- [전자공시시스템 (DART)](https://dart.fss.or.kr)")
  st.markdown("</div>", unsafe_allow_html=True)

  # 2. 관심 종목 편집 및 추가 툴
  st.markdown(
      '<div class="card"><div class="sub-header">⭐ 관심 종목 관리</div>',
      unsafe_allow_html=True,
  )
  new_ticker = st.text_input(
      "티커 추가 (Yahoo Finance 기준)", placeholder="예: MSFT 또는 035420.KS"
  )
  if st.button("관심 종목 등록", use_container_width=True):
    if new_ticker:
      upper_t = new_ticker.upper().strip()
      if upper_t not in st.session_state.watchlist:
        st.session_state.watchlist.append(upper_t)
        st.success(f"'{upper_t}'가 등록되었습니다!")

  if st.button("관심 종목 초기화", use_container_width=True):
    st.session_state.watchlist = ["TSLA", "AAPL", "NVDA"]
    st.success("관심 종목이 기본값으로 초기화되었습니다.")

  st.markdown("---")
  st.markdown(
      '<p style="font-size: 12px; color: #64748b;">현재 등록된 티커:<br>'
      + ", ".join(st.session_state.watchlist)
      + "</p>",
      unsafe_allow_html=True,
  )
  st.markdown("</div>", unsafe_allow_html=True)

with col_left:
  # 1. 글로벌 및 국내 핵심 지수 모니터링
  st.markdown(
      '<div class="card"><div class="sub-header">🌍 글로벌 & 국내 핵심 지수'
      " (The Big Indices)</div>",
      unsafe_allow_html=True,
  )

  market_indices = {
      "S&P 500": "^GSPC",
      "나스닥 종합": "^IXIC",
      "다우 존스": "^DJI",
      "코스피 (KOSPI)": "^KS11",
      "코스닥 (KOSDAQ)": "^KQ11",
  }

  index_data = []
  for name, ticker in market_indices.items():
    try:
      t = yf.Ticker(ticker)
      hist = t.history(period="5d")
      if not hist.empty:
        curr = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]
        chg = ((curr - prev) / prev) * 100
        index_data.append({
            "지수명": name,
            "현재 지수": round(curr, 2),
            "전일 대비 (%)": round(chg, 2),
        })
    except:
      pass

  if index_data:
    st.dataframe(
        pd.DataFrame(index_data), use_container_width=True, hide_index=True
    )

  st.markdown("</div>", unsafe_allow_html=True)

  # 2. 증시 영향 매크로 펀더멘털 지표 (환율, 금리, 원자재)
  st.markdown(
      '<div class="card"><div class="sub-header">📊 주가 영향 매크로 펀더멘털 지표'
      " & 리스크 감지</div>",
      unsafe_allow_html=True,
  )
  st.markdown(
      '<p style="font-size: 13px; color: #64748b; margin-bottom: 12px;">💡'
      " 외국인 수급에 직결되는 <b>원/달러 환율 기준선(1,350원)</b>과 증시"
      " 밸류에이션 척도인 <b>미국 10년물 국채금리</b>를 모니터링합니다.</p>",
      unsafe_allow_html=True,
  )

  macro_tickers = {
      "USD/KRW (원/달러 환율)": "KRW=X",
      "US 10Y Treasury (미국 10년물 국채금리)": "^TNX",
      "WTI Crude Oil (원유)": "CL=F",
      "Gold (금 안전자산)": "GC=F",
  }

  macro_data = []
  usd_krw_val = 0.0

  for name, ticker in macro_tickers.items():
    try:
      t = yf.Ticker(ticker)
      hist = t.history(period="5d")
      if not hist.empty:
        curr = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]
        chg = ((curr - prev) / prev) * 100

        if "USD/KRW" in name:
          usd_krw_val = curr

        macro_data.append({
            "매크로 지표": name,
            "현재 시세": round(curr, 2),
            "전일 대비 (%)": round(chg, 2),
        })
    except:
      pass

  if macro_data:
    st.dataframe(
        pd.DataFrame(macro_data), use_container_width=True, hide_index=True
    )

    if usd_krw_val > 0:
      if usd_krw_val >= 1350:
        st.markdown(
            f'<div class="alert-box">🚨 [환율 리스크 경보] 현재 원/달러 환율({usd_krw_val:.2f}원)이 1,350원을 상회하여 외국인 수급에 부정적 영향이 우려됩니다.</div>',
            unsafe_allow_html=True,
        )
      else:
        st.markdown(
            f'<div class="safe-box">✨ [환율 안정권] 현재 원/달러 환율({usd_krw_val:.2f}원)은 1,350원 미만으로 안정세를 보이고 있습니다.</div>',
            unsafe_allow_html=True,
        )

  st.markdown("</div>", unsafe_allow_html=True)

  # 3. 내 관심 종목 실시간 시세 테이블
  st.markdown(
      '<div class="card"><div class="sub-header">⭐ AFK 오피셜 관심 종목 라이브'
      " 포트폴리오</div>",
      unsafe_allow_html=True,
  )

  watchlist_data = []
  for ticker in st.session_state.watchlist:
    try:
      t = yf.Ticker(ticker)
      hist = t.history(period="5d")
      if not hist.empty:
        curr = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]
        chg = ((curr - prev) / prev) * 100
        watchlist_data.append({
            "종목 코드 (Ticker)": ticker,
            "현재가": round(curr, 2),
            "전일 대비 (%)": round(chg, 2),
        })
    except:
      watchlist_data.append(
          {"종목 코드 (Ticker)": ticker, "현재가": "조회 실패", "전일 대비 (%)": "-"}
      )

  if watchlist_data:
    st.dataframe(
        pd.DataFrame(watchlist_data), use_container_width=True, hide_index=True
    )

  st.markdown("</div>", unsafe_allow_html=True)

  # 4. 실시간 증권/경제 뉴스 헤드라인
  st.markdown("""
        <div class="card">
            <div class="sub-header">📰 필수 경제 및 증권 마켓 뉴스 헤드라인</div>
    """, unsafe_allow_html=True)


  @st.cache_data(ttl=600)
  def get_market_news():
    try:
      raw_query = "증권 주식 환율 연준 금리"
      encoded_query = urllib.parse.quote(raw_query)
      rss_url = (
          f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
      )
      feed = feedparser.parse(rss_url)
      articles = []
      for entry in feed.entries[:5]:
        articles.append({"title": entry.title, "url": entry.link})
      return articles
    except:
      return []


  live_market_news = get_market_news()

  if live_market_news:
    for idx, article in enumerate(live_market_news, 1):
      st.markdown(
          f"""
            <div class="headline-box">
                <b>📌 마켓 뉴스 {idx}</b><br>
                👉 <a href="{article['url']}" target="_blank" style="text-decoration: none; font-size: 14px; font-weight: 600; color: #0284c7;">{article['title']}</a>
            </div>
            """,
          unsafe_allow_html=True,
      )
  else:
    st.info("실시간 금융 기사를 불러오는 중입니다.")

  st.markdown("</div>", unsafe_allow_html=True)
