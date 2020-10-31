import puppeteer from "puppeteer";
import axios from "axios";
import dotenv from "dotenv";

dotenv.config();

const { FNGUIDE_USER, FNGUIDE_PASSWORD } = process.env;

String.prototype.format = function () {
	let formatted = this;
	for (let i = 0; i < arguments.length; i++) {
		const regexp = new RegExp(`\\{${i}\\}`, "gi");
		formatted = formatted.replace(regexp, arguments[i]);
	}
	return formatted;
};


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
		const page = this.page;

		const IDInputSelector = "#txtID";
		const PWInputSelector = "#txtPW";
		const loginBtnSelector =
			"#container > div > div > div.log--wrap > div.log--area > form > div > fieldset > button";
		const logoutOtherIPUserBtnSelector =
			"#divLogin > div.lay--popFooter > form > button.btn--back";
		const FnguideLogoSelector = "body > div.header > div > h1 > a";

		await page.goto(URL.LOGIN_PAGE);
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
		await page.waitFor(5000).then(() => {
			page.waitForSelector(FnguideLogoSelector).then().catch();
		});
	}
}

(async () => {
	const p = new Puppet('test');
	await p.startBrowser(false);
	await p.login();
})();