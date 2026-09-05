import urllib.parse
import feedparser
import pandas as pd
import streamlit as st
import yfinance as yf

# 페이지 설정 (와이드 모드)
st.set_page_config(
    page_title="AFK Market Intelligence Desk", page_icon="📈", layout="wide"
)

# 커스텀 CSS
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

# 세션 상태 초기화 (관심 종목 리스트)
if "watchlist" not in st.session_state:
  st.session_state.watchlist = ["TSLA", "AAPL", "NVDA", "005930.KS"]

# 상단 배너
st.markdown("""
    <div class="main-header">
        <span>📈 AFK MARKET INTELLIGENCE DESK</span>
        <span style="font-size: 13px; background-color: #38bdf8; color: #0f172a; padding: 4px 10px; border-radius: 4px; font-weight: 700;">INVESTMENT TERMINAL v2.0</span>
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([3, 1])

with col_right:
  # 1. 금융 퀵링크
  st.markdown(
      '<div class="card"><div class="sub-header">🔗 금융 및 투자 퀵링크</div>',
      unsafe_allow_html=True,
  )
  st.markdown("- [네이버 증권](https://finance.naver.com)")
  st.markdown("- [인베스팅닷컴](https://www.investing.com)")
  st.markdown(
      "- [한경 마켓인사이트](https://marketinsight.hankyung.com)"
  )
  st.markdown("- [전자공시시스템 (DART)](https://dart.fss.or.kr)")
  st.markdown("</div>", unsafe_allow_html=True)

  # 2. 관심 종목 관리 툴
  st.markdown(
      '<div class="card"><div class="sub-header">⭐ 관심 종목 관리</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<p style="font-size: 11px; color: #64748b;">💡 <b>입력 팁</b>: 미국은'
      " 심볼 그대로 (예: <code>MSFT</code>), 국내 주식은 6자리 뒤에'
      " <code>.KS</code>(코스피) 또는 <code>.KQ</code>(코스닥)를 붙여주세요.</p>",
      unsafe_allow_html=True,
  )

  new_ticker = st.text_input(
      "티커 추가", placeholder="예: MSFT 또는 000660.KS"
  )
  if st.button("관심 종목 등록", use_container_width=True):
    if new_ticker:
      upper_t = new_ticker.upper().strip()
      if upper_t not in st.session_state.watchlist:
        st.session_state.watchlist.append(upper_t)
        st.success(f"'{upper_t}'가 등록되었습니다!")

  if st.button("관심 종목 초기화", use_container_width=True):
    st.session_state.watchlist = ["TSLA", "AAPL", "NVDA", "005930.KS"]
    st.success("초기화 완료되었습니다.")

  st.markdown("---")
  st.markdown(
      '<p style="font-size: 12px; color: #64748b;">등록된 티커 목록:<br>'
      + ", ".join(st.session_state.watchlist)
      + "</p>",
      unsafe_allow_html=True,
  )
  st.markdown("</div>", unsafe_allow_html=True)

with col_left:
  # 1. 글로벌 & 국내 핵심 지수
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

  # 2. 매크로 펀더멘털 지표
  st.markdown(
      '<div class="card"><div class="sub-header">📊 주가 영향 매크로 펀더멘털 지표'
      " & 리스크 감지</div>",
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
            f'<div class="alert-box">🚨 [환율 경보] 현재 환율({usd_krw_val:.2f}원)이'
            " 1,350원을 상회하여 외국인 수급에 부담을 줄 수 있습니다.</div>",
            unsafe_allow_html=True,
        )
      else:
        st.markdown(
            f'<div class="safe-box">✨ [환율 안정] 현재 환율({usd_krw_val:.2f}원)은'
            " 1,350원 미만 안정권입니다.</div>",
            unsafe_allow_html=True,
        )
  st.markdown("</div>", unsafe_allow_html=True)

  # 3. [신규 고도화] 관심 종목 라이브 포트폴리오 및 트렌드/거래량 그래프 시각화
  st.markdown(
      '<div class="card"><div class="sub-header">⭐ AFK 오피셜 관심 종목 포트폴리오'
      " 및 트렌드/거래량 분석</div>",
      unsafe_allow_html=True,
  )

  # 개별 종목 선택 셀렉트박스 추가 (차트로 상세히 볼 종목 선택)
  selected_stock = st.selectbox(
      "상세 트렌드 및 거래량 차트를 확인할 종목 선택",
      st.session_state.watchlist,
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
            "종목 코드": ticker,
            "현재가": round(curr, 2),
            "전일 대비 (%)": round(chg, 2),
        })
      else:
        watchlist_data.append(
            {"종목 코드": ticker, "현재가": "데이터 없음", "전일 대비 (%)": "-"}
        )
    except:
      watchlist_data.append(
            {"종목 코드": ticker, "현재가": "조회 실패", "전일 대비 (%)": "-"}
        )

  if watchlist_data:
    st.dataframe(
        pd.DataFrame(watchlist_data), use_container_width=True, hide_index=True
    )

  st.markdown("---")
  st.markdown(
      f"#### 📉 [{selected_stock}] 최근 1개월 주가 트렌드 및 거래량 추이",
      unsafe_allow_html=True,
  )

  try:
    chart_t = yf.Ticker(selected_stock)
    chart_hist = chart_t.history(period="1mo")  # 최근 1개월 데이터
    if not chart_hist.empty:
      # 스트림릿 내장 라인 차트로 주가 트렌드 표시
      st.markdown("**• 최근 1개월 종가(Close) 트렌드**")
      st.line_chart(chart_hist["Close"])

      # 거래량 바(Bar) 차트 표시
      st.markdown("**• 최근 1개월 거래량(Volume) 추이**")
      st.bar_chart(chart_hist["Volume"])
    else:
      st.warning(
          "해당 종목의 차트 데이터를 불러올 수 없습니다. 티커 형식을 다시"
          " 확인해주세요."
      )
  except Exception as e:
    st.error(f"차트 로딩 중 오류 발생: {e}")

  st.markdown("</div>", unsafe_allow_html=True)

  # 4. 경제 뉴스 헤드라인
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
                👉 <a href='{article['url']}' target='_blank' style='text-decoration: none; font-size: 14px; font-weight: 600; color: #0284c7;'>{article['title']}</a>
            </div>
            """,
          unsafe_allow_html=True,
      )
  else:
    st.info("실시간 금융 기사를 불러오는 중입니다.")

  st.markdown("</div>", unsafe_allow_html=True)
