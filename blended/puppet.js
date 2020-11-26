const puppeteer = require("puppeteer");
const axios = require("axios");
const dotenv = require("dotenv");

dotenv.config();

const { FNGUIDE_USER, FNGUIDE_PASSWORD } = process.env;

class Puppet {
	constructor(taskName) {
		this.taskName = taskName;
		this.id = FNGUIDE_USER;
		this.pw = FNGUIDE_PASSWORD;
		this.width = 1920;
		this.height = 1080;
		this.todayDate = new Date().toISOString().slice(0, 10).replace(/-/gi, "");
	}

	async startBrowser(headlessBool, slowMoTime = 100) {
		const width = this.width;
		const height = this.height;

		let puppeteerConfig = {
			headless: headlessBool,
			args: ["--no-sandbox"],
			slowMo: slowMoTime,
		};

		if (!headlessBool) {
			puppeteerConfig['args'] = [`--window-size=${width}, ${height}`];
		}

		this.browser = await puppeteer.launch(puppeteerConfig);
		this.page = await this.browser.newPage();

		await this.page.setViewport({ width, height });
		return true;
	}

	async login() {
		// 로그인 페이지로 가서 로그인한다
		const { page } = this;

		const IDInputSelector = "#txtID";
		const PWInputSelector = "#txtPW";
		const loginBtnSelector =
			"#container > div > div > div.log--wrap > div.log--area > form > div > fieldset > button";
		const logoutOtherIPUserBtnSelector =
			"#divLogin > div.lay--popFooter > form > button.btn--back";
		const FnguideLogoSelector = "body > div.header > div > h1 > a";

		await page.goto("https://www.fnguide.com/home/login");
		await page.waitForSelector(IDInputSelector);
		await page.click(IDInputSelector);
		await page.type(IDInputSelector, this.id);
		await page.click(PWInputSelector);
		await page.type(PWInputSelector, this.pw);
		await page.click(loginBtnSelector);

		const logoutOtherIPUserBtnExists = await page
			.$eval(logoutOtherIPUserBtnSelector, (el) => !!el)
			.catch((error) => {
				console.log(error);
			});
		if (logoutOtherIPUserBtnExists) {
			await page.click(logoutOtherIPUserBtnSelector);
		}

		// waitForSelector 메소드에 문제가 있어서, 강제로 5초를 쉬게 하고 waitForSelector를 실행시킨다
		await page.waitFor(5000).then(async () => {
			await page.waitForSelector(FnguideLogoSelector);
		});
	}

	async requestData(name = '', referer, url) {
		console.log(`[Data Request] (${name}) ${url}`);
		const { page } = this;

		// set headers to fool Fnguide
		await page.setExtraHTTPHeaders({
			Referer: referer,
			"X-Requested-With": "XMLHttpRequest",
		});
		await page.goto(url, {
			waitUntil: "networkidle2",
			timeout: 3000000,
		})
		return await page.evaluate(() => {
			return JSON.parse(document.querySelector("body").innerText);
		});
	}

	getFundamentalData(ticker, period = 'yearly', years = '100', type = '10') {
		ticker = `A${ticker}`;
		period = (period == 'yearly') ? 'D' : 'Q';
		years = (period == 'yearly') ? '100' : '70';
		if (type == 'financial_statement') {
			type = '10';
		}
		if (type == 'income_statement') {
			type = '20';
		}
		if (type == 'cash_flow') {
			type = '30';
		}
		if (type == 'capital_changes') {
			type = '40';
		}
		if (type == 'financial_ratio') {
			type = '99';
			years = '20';
		}
		return `https://www.fnguide.com/api/fgdd/GetFinByIndiv?IN_GICODE=${ticker}&IN_GS_GB=${period}&IN_ACCT_STD=I&IN_CONSOLIDATED=1&IN_ACNT_CODE=${type}&IN_DETAIL=10&IN_MAXYEAR=${years}`;
	}

	async massDateCrawl() {
		return await this.requestData(
			'Mass Date Crawl',
			"http://www.fnguide.com/fgdd/StkIndmByTime",
			`http://www.fnguide.com/api/Fgdd/StkIndMByTimeGrdData?IN_MULTI_VALUE=CJA005930%2CCII.001&IN_START_DT=19900101&IN_END_DT=${this.todayDate}&IN_DATE_TYPE=D&IN_ADJ_YN=Y`
		);
	}

	async getKospiTickers(date) {
		return await this.requestData(
			'Get Kospi Tickers',
			"http://www.fnguide.com/fgdd/StkIndByTime",
			`http://www.fnguide.com/api/Fgdd/StkIndByTimeGrdDataDate?IN_SEARCH_DT=${date}&IN_SEARCH_TYPE=J&IN_KOS_VALUE=1`
		);
	}

	async getKosdaqTickers(date) {
		return await this.requestData(
			'Get Kosdaq Tickers',
			"http://www.fnguide.com/fgdd/StkIndByTime",
			`http://www.fnguide.com/api/Fgdd/StkIndByTimeGrdDataDate?IN_SEARCH_DT=${date}&IN_SEARCH_TYPE=J&IN_KOS_VALUE=2`
		);
	}

	async getETFTickers(date) {
		return await this.requestData(
			'Get ETF Tickers',
			"http://fnguide.com/fgdd/StkEtf",
			`http://www.fnguide.com/api/Fgdd/StkEtfGrdDataDate?IN_TRD_DT=${date}&IN_MKT_GB=0`
		);
	}

	async getStockInfo() {
		return await this.requestData(
			'Get Stock Info',
			"http://fnguide.com/fgdd/StkAllItemInfo",
			"http://www.fnguide.com/api/Fgdd/StkAllItemInfoGrdData?IN_KOS_VALUE=0"
		);
	}

	async massIndexCrawl(date) {
		return await this.requestData(
			'Mass Index Crawl',
			"http://www.fnguide.com/fgdd/StkIndByTime",
			`http://www.fnguide.com/api/Fgdd/StkIndByTimeGrdDataDate?IN_SEARCH_DT=${date}&IN_SEARCH_TYPE=I&IN_KOS_VALUE=0`
		);
	}

	async massETFCrawl(date) {
		return await this.requestData(
			'Mass ETF Crawl',
			"http://fnguide.com/fgdd/StkEtf",
			`http://www.fnguide.com/api/Fgdd/StkEtfGrdDataDate?IN_TRD_DT=${date}&IN_MKT_GB=0`
		);
	}

	async massOHLCVCrawl(date) {
		return await this.requestData(
			'Mass OHLCV Crawl',
			"http://fnguide.com/fgdd/StkIndByTime",
			`http://www.fnguide.com/api/Fgdd/StkIndByTimeGrdDataDate?IN_SEARCH_DT=${date}&IN_SEARCH_TYPE=J&IN_KOS_VALUE=0`
		);
	}

	async massMktCapCrawl(date) {
		return await this.requestData(
			'Mass Mkt Cap Crawl',
			"http://fnguide.com/fgdd/StkItemDateCap",
			`http://www.fnguide.com/api/Fgdd/StkItemDateCapGrdDataDate?IN_MKT_TYPE=0&IN_SEARCH_DT=${date}`
		);
	}

	async massBuysellCrawl(date) {
		return await this.requestData(
			'Mass Buysell Crawl',
			"http://fnguide.com/fgdd/StkJInvTrdTrend",
			`http://www.fnguide.com/api/Fgdd/StkJInvTrdTrendGrdDataDate?IN_MKT_TYPE=0&IN_TRD_DT=${date}&IN_UNIT_GB=2`
		);
	}

	async massFactorCrawl(date) {
		return await this.requestData(
			'Mass Factor Crawl',
			"http://www.fnguide.com/fgdd/StkDateShareIndx",
			`http://www.fnguide.com/api/Fgdd/StkDateShareIndxGrdDataDate?IN_SEARCH_DT=${date}&IN_MKT_TYPE=0&IN_CONSOLIDATED=1`
		);
	}

	async done() {
		await this.browser.close();
	}
}

module.exports = {
	Puppet
};