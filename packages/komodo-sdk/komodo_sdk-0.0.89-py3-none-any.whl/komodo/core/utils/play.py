import json

from werkzeug.utils import secure_filename

from komodo.core.agents.default import embedhelper_agent
from komodo.framework.komodo_app import KomodoApp
from komodo.shared.documents.text_extract import extract_json


def get_conexio_data(app: KomodoApp, data_source: str, item: str):
    return app.data_sources[data_source].get_item(item)


def transform_documents(app: KomodoApp, source: str):
    ds = app.get_data_source(source)
    agent = embedhelper_agent()

    for item in ds.list_items():
        documents = ds.get_item(item)
        for d in documents:
            embeddable = agent.run(d.page_content)
            d.page_content = embeddable.text
            fname = secure_filename(item) + ".json"
            with open(fname, "w") as f:
                f.write(d.page_content)


def index_documents(app: KomodoApp, data_source: str, vector_store: str = "qdrant-test"):
    ds = app.get_data_source(data_source)
    vs = app.get_vector_store(vector_store)

    for item in ds.list_items():
        fname = secure_filename(item) + ".json"
        print(f"Indexing: {fname}")
        with open("../../docs/transformed/" + fname, "r") as f:
            text = f.read()
            d = json.loads(extract_json(text))
            print("Items: ", len(d))
            vs.upsert_list(list=d, source=item)
