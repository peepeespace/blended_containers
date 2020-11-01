import Koa from 'koa';
import bodyParser from 'koa-bodyparser';
import { ApolloServer } from 'apollo-server-koa';

import { createStore } from './src/store';
import { resolvers } from './src/resolvers'
import { typeDefs } from './src/schemas';
import { Fundamental, Ticker, Price } from './src/datasources';

const store = createStore();

const server = new ApolloServer({
    typeDefs,
    resolvers,
    dataSources: () => ({
        Fundamental: new Fundamental({ store }),
        Ticker: new Ticker({ store }),
        Price: new Price({ store })
    }),
    context: ({ req }) => ({}),
    introspection: true,
    playground: true
});

const app = new Koa();
app.use(bodyParser());
server.applyMiddleware({ app });

const port = 3000;
app.listen(port, () => {
    console.log(`Server connect at port: ${port}${server.graphqlPath}`);
});