import { gql } from 'apollo-server-koa';

export const typeDefs = gql`
    type Ticker {
        Code: String
        Name: String
        Country: String
        Exchange: String
        Currency: String
        Type: String
    }

    type Query {
        Tickers(filter: String): [Ticker]
    }
`;