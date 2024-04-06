import time
from datetime import datetime

from komodo.core.utils.rag_context import RagContext
from komodo.shared.utils.filestats import file_details
from komodo.shared.utils.globber import Globber


class Indexer:
    def __init__(self, rag_context: RagContext):
        self.rag_context = rag_context
        self.globber = Globber(rag_context.path, self.__on_created, self.__on_deleted)

    def __on_created(self, filepath):
        print("Reviewing status of file: " + filepath)
        file = self.rag_context.find_file(filepath)
        if file and file.indexed_at:
            print(f"Already indexed: {filepath} in collection: {self.rag_context.shortcode} at {file.indexed_at}")
            return

        # index the file
        self.rag_context.index(filepath)

        # update the file details
        file = file_details(filepath)
        file.indexed_at = datetime.utcnow().isoformat() + 'Z'
        self.rag_context.update_file(filepath, file)

    def __on_deleted(self, filepath):
        print("Removing deleted file: " + filepath)
        self.rag_context.remove(filepath)

    def add_intelligence(self, filepath):
        print("Adding intelligence to: " + filepath)

    def run(self, max_updates=1, update_interval=5, reindex=False):
        if reindex:
            print("Reindexing...")
            self.rag_context.reset_all()

        self.globber.start()
        update_count = 1  # start runs the initial update
        while update_count < max_updates or max_updates == 0:
            time.sleep(update_interval)
            self.globber.updates()
            update_count += 1

        print("Indexed. Looped " + str(update_count) + " times. Stopping...")


if __name__ == "__main__":
    from komodo.config import PlatformConfig

    data_path = PlatformConfig().komodo_hello_path
    cache_path = PlatformConfig().cache()
    rag_context = RagContext(path=data_path, cache_path=cache_path)
    indexer = Indexer(rag_context)
    indexer.run(update_interval=5)
