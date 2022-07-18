import pyupbit

# Web socket 은 초당 5회, 분당 100회 연결 요청 가능
# 종목, 캔들, 체결, 티커, 호가 API 는 분당 600회, 초당 10회 사용 가능

# 암호화폐 목록
# get_tickers 함수는 업비트가 지원하는 모든 암호화폐 목록을 얻어옴.

tickets_list = pyupbit.get_tickers()
print(tickets_list)

# 업비트가 지원하는 암호화폐 목록 중 특정 시장(fiat) 에 매매가 가능한 목록만 얻어올 수 있음
# KRW/BTC/USDT 시장을 조회할 수 있음
# - KRW: 원화 마켓
# - BTC: 비트코인 마켓
# - USDT: 테더 마켓

upbit_tickers = pyupbit.get_tickers(fiat="KRW")
print(upbit_tickers)

# 최근 체결가격
# get_current_price 함수는 암호화폐의 현재가를 얻어옴.
# 함수로 티커를 넣어주어야 함
upbit_krw_btc_pr = pyupbit.get_current_price("KRW-BTC")
print(upbit_krw_btc_pr)

upbit_cur_pr = pyupbit.get_current_price(["KRW-BTC", "KRW-XRP"])
print(upbit_cur_pr)

# get_current_price 함수는 최대 100개의 암호화폐를 조회할 수 있음

# 차트 데이터.
# 고가/시가/저가/종가/거래량을 DataFrame 으로 반환함
df = pyupbit.get_ohlcv("KRW-BTC")
print(df.tail())

# count 파라미터는 조회 갯수를 지정.
# 최근 영업일부터 이전 count 만큼의 이전 영업일까지 조회
# count 파라미터를 입력하지 않는 경우 default value 는 200

df = pyupbit.get_ohlcv("KRW-BTC", count=5)
print(len(df))

