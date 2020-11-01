import { DataSource } from 'apollo-datasource';

class Fundamental extends DataSource {
    constructor({ store }) {
        super();
        this.store = store;
    }

    initialize(config) {
        this.context = config.context;
    }
}

export default Fundamental;