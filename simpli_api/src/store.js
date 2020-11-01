import asyncRedis from 'async-redis';
import dotenv from "dotenv";

dotenv.config();

const { REDIS_HOST, REDIS_PASSWORD } = process.env;

const REDIS_URI = `redis://:${REDIS_PASSWORD}@${REDIS_HOST}:6379/0`;

const createStore = () => {
    return {
        redis: asyncRedis.createClient(REDIS_URI, { 'return_buffers': true })
    }
}

export {
    createStore
};