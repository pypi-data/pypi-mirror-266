from komodo.core.tools.mongo.mongo_databases import MongoDBLister
from komodo.core.tools.mongo.mongo_query import MongoDBQuery
from komodo.core.tools.mongo.mongo_schema import MongoDBSchema
from komodo.core.tools.mongo.mongo_unique import MongoDBUnique
from komodo.framework.komodo_agent import KomodoAgent


class MongoAgent(KomodoAgent):
    instructions = "You are a Mongo Agent. You will be given query and you will use mongo tools to get relevant data. " \
                   "Do not use any external sources. Use only the information provided by the tools to answer the question. " \
                   "Do not suggest user to fetch data himself. Use the tools to fetch data."

    def __init__(self, connection_string):
        super().__init__(shortcode="mongo_agent",
                         name="Mongo DB Agent",
                         purpose="Answer questions based on data in mongo db.",
                         instructions=self.instructions,
                         tools=[MongoDBLister(connection_string), MongoDBQuery(connection_string),
                                MongoDBSchema(connection_string), MongoDBUnique(connection_string)])
