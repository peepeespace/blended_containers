export const resolvers = {
    Query: {
        Tickers: async (_, { filter }, { dataSources }) => {
            return await dataSources.Ticker.getTickersList(filter);
        }
    }
};