const { SLEEP, getSleepTime } = require('./utils');
const { Puppet } = require('./puppet');
const { Processor } = require('./processor');
const { RedisClient } = require('./cache');

const main = async () => {
	const redis = new RedisClient();
	await redis.auth();

	const puppet = new Puppet('test');
	const processor = new Processor();
	const started = await puppet.startBrowser(false, 100);
	if (started) {
		await puppet.login();
	}

	let data;
	let processedData;

	////////
	// #1 //
	////////
	// date list for Korean stocks (005930 / 삼성전자를 기준으로 수집)
	data = await puppet.massDateCrawl();
	processor.setData(data);
	processedData = processor.processMassDate();
	await redis.setList(processedData);

	await puppet.done();
	return true;
};

main().then(res => process.exit())
	.catch(err => {
		console.log(err);
		process.exit();
	});