export const URL = {
	LOGIN_PAGE: "https://www.fnguide.com/home/login",
	DATE_PAGE:
		"http://www.fnguide.com/fgdd/StkIndmByTime#multivalue=CJA005930|CII.001&adjyn=Y&multiname=삼성전자|종합주가지수",
	MKTCAP_PAGE: "http://www.fnguide.com/fgdd/StkItemDateCap#tab=D&market=0",
	API: {
		// date의 URL에서 IN_START_DT=20130101 부분 때문에 20130101부터 데이터 수집 시작
		date:
			"http://www.fnguide.com/api/Fgdd/StkIndMByTimeGrdData?IN_MULTI_VALUE=CJA005930%2CCII.001&IN_START_DT=19900101&IN_END_DT={0}&IN_DATE_TYPE=D&IN_ADJ_YN=Y",
		kospi_tickers:
			"http://www.fnguide.com/api/Fgdd/StkIndByTimeGrdDataDate?IN_SEARCH_DT={0}&IN_SEARCH_TYPE=J&IN_KOS_VALUE=1",
		kosdaq_tickers:
			"http://www.fnguide.com/api/Fgdd/StkIndByTimeGrdDataDate?IN_SEARCH_DT={0}&IN_SEARCH_TYPE=J&IN_KOS_VALUE=2",
		stock_info:
			"http://www.fnguide.com/api/Fgdd/StkAllItemInfoGrdData?IN_KOS_VALUE=0",
		// index, ohlcv, mkt_cap, factor는 1990년부터 데이터 요청 가능
		index:
			"http://www.fnguide.com/api/Fgdd/StkIndByTimeGrdDataDate?IN_SEARCH_DT={0}&IN_SEARCH_TYPE=I&IN_KOS_VALUE=0",
		etf:
			"http://www.fnguide.com/api/Fgdd/StkEtfGrdDataDate?IN_TRD_DT={0}&IN_MKT_GB=0", // 2010년부터 제대로 데이터 존재
		ohlcv:
			"http://www.fnguide.com/api/Fgdd/StkIndByTimeGrdDataDate?IN_SEARCH_DT={0}&IN_SEARCH_TYPE=J&IN_KOS_VALUE=0",
		mkt_cap:
			"http://www.fnguide.com/api/Fgdd/StkItemDateCapGrdDataDate?IN_MKT_TYPE=0&IN_SEARCH_DT={0}",
		buysell:
			"http://www.fnguide.com/api/Fgdd/StkJInvTrdTrendGrdDataDate?IN_MKT_TYPE=0&IN_TRD_DT={0}&IN_UNIT_GB=2", // 19990101부터 데이터 있음
		factor:
			"http://www.fnguide.com/api/Fgdd/StkDateShareIndxGrdDataDate?IN_SEARCH_DT={0}&IN_MKT_TYPE=0&IN_CONSOLIDATED=1",
	},
	FINANCIAL_PAGE: "https://www.fnguide.com/api/fgdd/GetFinByIndiv?IN_GICODE=A{0}&IN_GS_GB={1}&IN_ACCT_STD=I&IN_CONSOLIDATED=1&IN_ACNT_CODE=10&IN_DETAIL=10&IN_MAXYEAR={2}"
};