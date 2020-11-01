import { DataSource } from 'apollo-datasource';
import fs from 'fs';
import zstd from 'node-zstandard';

const fsPromise = fs.promises;

const dctx = {
    decompress: function (key) {
        return new Promise(function (resolve, reject) {
            zstd.decompress(`./zstd/${key}.zst`, `./zstd/${key}`, (err, result) => {
                resolve(result);
            });
        });
    }
};

class Ticker extends DataSource {
    constructor({ store }) {
        super();
        this.store = store;
    }

    initialize(config) {
        this.context = config.context;
    }

    async getTickersList(filter) {
        const key = 'SIMPLI_US_TICKERS_DICT';
        const exists = fs.existsSync(`./zstd/${key}`);
        if (!exists) {
            const data = await this.store.redis.get(key);
            await fsPromise.writeFile(`./zstd/${key}.zst`, data);
            await dctx.decompress(key);
        }
        let res = await fsPromise.readFile(`./zstd/${key}`);
        res = JSON.parse(res.toString('utf8'));
        return Object.values(res);
    }
}

export default Ticker;