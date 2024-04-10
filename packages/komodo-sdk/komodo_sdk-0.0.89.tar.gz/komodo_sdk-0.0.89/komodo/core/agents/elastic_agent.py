from komodo.core.tools.elastic.elastic_connect import get_elastic_client
from komodo.core.tools.elastic.elastic_count import ElasticCount
from komodo.core.tools.elastic.elastic_get import ElasticGet
from komodo.core.tools.elastic.elastic_search import ElasticQuery
from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_context import KomodoContext


class ElasticAgent(KomodoAgent):
    instructions = "You are an Elastic Agent. You will be given query and you will use " \
                   "supplied context and elastic search to get relevant data. " \
                   "Do not use any external sources. Use only the information provided to answer the question. " \
                   "Do not suggest user to teach them or to fetch data themselves." \
                   "Use the tools to fetch data only if it is not available to you in the context."

    def __init__(self, connection_string, authorized_indexes):
        super().__init__(shortcode="elastic_agent",
                         name="Elastic Agent",
                         purpose="Answer questions based on data in elasticsearch database.",
                         instructions=self.instructions,
                         tools=[ElasticQuery(connection_string, authorized_indexes),
                                ElasticCount(connection_string, authorized_indexes),
                                ElasticGet(connection_string, authorized_indexes)])
        self.connection_string = connection_string
        self.authorized_indexes = authorized_indexes

    def generate_context(self, prompt=None, runtime=None):
        context = KomodoContext()
        context.add("Data", "You have the list of indexes below. Do not query to get this information.")
        context.add("List of Indexes", str(self.list_indexes("*")))
        context.add("Limitation", "You can only query the indexes: " + str(self.authorized_indexes))
        return context

    def list_indexes(self, index="*"):
        es = get_elastic_client(self.connection_string)
        indices = list(es.indices.get_alias(index=index).keys())
        es.close()
        return indices
