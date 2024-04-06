from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


class Watcher:

    def __init__(self, on_modified, on_created=None, on_deleted=None, on_moved=None):
        patterns = ["*"]
        ignore_patterns = None
        ignore_directories = True
        case_sensitive = True
        handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
        handler.on_modified = on_modified
        if on_created:
            handler.on_created = on_created

        if on_deleted:
            handler.on_deleted = on_deleted

        if on_moved:
            handler.on_moved = on_moved

        self.event_handler = handler
        self.observer = Observer()

    def start(self, path: str, recursive: bool = True):
        self.observer.schedule(self.event_handler, path, recursive=recursive)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()


if __name__ == "__main__":
    from time import sleep
    import os

    watcher = Watcher(on_modified=lambda e: print(f"Modified: {e.src_path}"))
    watcher.start(os.path.dirname(__file__))
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        watcher.stop()
        print("Exiting...")
