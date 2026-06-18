from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from modules.sorter import sort_file
import time
import os

class DownloadHandler(FileSystemEventHandler):
    def __init__(self, log_callback, stat_callback):
        super().__init__()
        self.log_callback = log_callback
        self.stat_callback = stat_callback

    def on_created(self, event):
        if event.is_directory:
            return
        
        self.log_callback(f"Detection : {os.path.basename(event.src_path)}")
        time.sleep(1)
        result, category = sort_file(event.src_path)
        self.log_callback(result)
        if category:
            self.stat_callback(category)

class FolderWatcher:
    def __init__(self, folder, log_callback, stat_callback):
        self.folder = folder
        self.log_callback = log_callback
        self.stat_callback = stat_callback
        self.observer = Observer()

    def start(self):
        handler = DownloadHandler(self.log_callback, self.stat_callback)
        self.observer.schedule(handler, self.folder, recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()