import mimetypes
import os
import time
from concurrent.futures import ThreadPoolExecutor

import magic
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from image_quality_sampler.db.database_manager import DatabaseManager

MAX_THREADS = 10


class Watcher:
    def __init__(self):
        self.event_handler = FileSystemEventHandler()
        self.event_handler.on_modified = self.on_modified
        self.observer = None
        print("Watcher Initialized")

    def get_db(self):
        return DatabaseManager()

    def on_modified(self, event):
        # Only react to changes in directories (not individual files)
        if event.is_directory:
            self.update_db()

    def update_db(self):
        db = self.get_db()
        batch_folder = self.get_folder_path_from_db()
        if batch_folder:
            batch_data = self.analyze_batch_folder(batch_folder)
            for data in batch_data:
                # Check if the batch already exists in the database
                existing_batch = db.get_batch(data["batch_name"])
                if existing_batch:
                    # Update only the relevant fields
                    db.update_batch(
                        data["batch_name"],
                        data["subfolder_count"],
                        data["image_count"],
                        existing_batch[4],  # Keep the existing attempts
                        existing_batch[5],  # Keep the existing status
                    )
                else:
                    # Insert the new batch into the database
                    db.insert_batch(
                        data["batch_name"],
                        data["subfolder_count"],
                        data["image_count"],
                        "0",
                        "PENDING",
                    )
        # Step 1: Fetch all batch names from the database
        all_batches = db.get_all_batches()
        all_batch_names = [batch[1] for batch in all_batches]

        # Step 2: Check each batch name against the folder
        folder_path = self.get_folder_path_from_db()
        existing_folders = [
            name
            for name in os.listdir(folder_path)
            if os.path.isdir(os.path.join(folder_path, name))
        ]

        for batch_name in all_batch_names:
            if batch_name not in existing_folders:
                # Step 3: Delete the entry from the database
                db.delete_batch(batch_name)
        db.close()

    def get_folder_path_from_db(self):
        db = self.get_db()
        config = db.get_configuration()
        db.close()
        return config[2] if config else None

    def run(self):
        self.db = DatabaseManager()
        folder_path = self.get_folder_path_from_db()

        # Wait until a valid folder is provided
        while not folder_path or not os.path.exists(folder_path):
            time.sleep(10)  # Wait for 10 seconds before checking again
            folder_path = self.get_folder_path_from_db()

        # Once a valid folder is found, initialize the observer and schedule it
        self.observer = Observer()
        self.observer.schedule(self.event_handler, folder_path, recursive=True)
        # Analyze the folder and update the database
        self.update_db()

        try:
            self.observer.start()
            print("Observer started with folder: " + folder_path)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.observer.stop()
            self.observer.join()
        except Exception as e:
            # Handle the exception
            print(f"Error in watcher: {e}")

    def analyze_batch_folder(self, batch_folder_path):
        batch_data = []
        for item in os.listdir(batch_folder_path):
            item_path = os.path.join(batch_folder_path, item)
            if os.path.isdir(item_path) and item.startswith("BATCH"):
                subfolder_count = 0
                image_count = self.recursive_image_count(item_path)
                for subitem in os.listdir(item_path):
                    subitem_path = os.path.join(item_path, subitem)
                    if os.path.isdir(subitem_path):
                        subfolder_count += 1
                batch_data.append(
                    {
                        "batch_name": item,
                        "subfolder_count": subfolder_count,
                        "image_count": image_count,
                    }
                )
        return batch_data

    def check_image(self, file):
        mime_type, _ = mimetypes.guess_type(file)

        # If mimetypes fails, fall back to python-magic.
        if not mime_type or not mime_type.startswith("image"):
            mime_type = magic.from_file(file, mime=True)

        return 1 if mime_type and mime_type.startswith("image") else 0

    def recursive_image_count(self, path):
        all_files = [
            os.path.join(dp, f)
            for dp, _, filenames in os.walk(path)
            for f in filenames
        ]

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            results = list(executor.map(self.check_image, all_files))

        return sum(results)
