import { DataSource } from 'apollo-datasource';

class Price extends DataSource {
    constructor({ store }) {
        super();
        this.store = store;
    }

    initialize(config) {
        this.context = config.context;
    }
}

export default Price;