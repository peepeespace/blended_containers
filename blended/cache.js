const redis = require('redis');
const asyncRedis = require('async-redis');
const dotenv = require('dotenv');

dotenv.config();

const { REDIS_HOST, REDIS_PASSWORD } = process.env;

class RedisClient {
	constructor() {
		this.initialRedisClient = redis.createClient(6379, REDIS_HOST);
		this.redisClient = asyncRedis.decorate(this.initialRedisClient);
	}

	async auth() {
		const response = await this.redisClient.auth(REDIS_PASSWORD);
		return response;
	}

	async setKey(key, value) {
		const response = await this.redisClient.set(key, value);
		if (response === 'OK') {
			return true;
		}
		return false;
	}

	async getKey(key) {
		const response = await this.redisClient.get(key);
		return response;
	}

	async keyExists(key) {
		const exists = await this.redisClient.exists(key);
		return exists;
	}

	async delKey(key) {
		const response = await this.redisClient.del(key);
		return response;
	}

	async setList(data) {
		const response = await this.redisClient.rpush(data);
		return response;
	}

	async getList(key, type) {
		let response = await this.redisClient.lrange(key, 0, -1);
		if (type === 'int') {
			if (!isNaN(parseInt(response[0], 10))) {
				response = response.map(x => parseInt(x, 10));
			}
		}
		return response;
	}

	async addToList(key, data) {
		const response = await this.redisClient.rpush(key, data);
		return response;
	}

	async setJSON(key, json) {
		const response = this.redisClient.hset(key, 'a', JSON.stringify(json));
		return response;
	}

	async getJSON(key) {
		const response = await this.redisClient.hget(key, 'a');
		const json = JSON.parse(response);
		return json;
	}

	async delJSON(key) {
		const response = await this.redisClient.hdel(key, 'a');
		return response;
	}

	async end() {
		this.redisClient.quit();
	}
}

module.exports = {
	RedisClient
};