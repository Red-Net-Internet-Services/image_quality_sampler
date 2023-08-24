import sqlite3

from image_quality_sampler import config


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(config.DB_FILENAME)
        self.cursor = self.conn.cursor()

        # Check if tables exist, if not, create them
        if not self.check_table_exists("configuration"):
            self.create_configuration_table()

        if not self.check_table_exists("batches"):
            self.create_batches_table()

    def check_table_exists(self, table_name):
        self.cursor.execute(
            """
            SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?
            """,
            (table_name,),
        )
        return self.cursor.fetchone()[0] == 1

    def create_configuration_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXIST configuration (
                id INTEGER PRIMARY KEY,
                project_name TEXT NOT NULL,
                location TEXT NOT NULL,
                batch_folder TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def create_batches_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXIST batches (
                id INTEGER PRIMARY KEY,
                batch_name TEXT NOT NULL,
                folder_count INTEGER NOT NULL,
                image_count INTEGER NOT NULL,
                sampling_attempts INTEGER,
                status TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def insert_configuration(self, project_name, location, batch_folder):
        self.cursor.execute(
            """
            INSERT INTO configuration (project_name, location, batch_folder)
            VALUES (?, ?, ?)
            """,
            (project_name, location, batch_folder),
        )
        self.conn.commit()

    def update_configuration(self, project_name, location, batch_folder):
        self.cursor.execute(
            """
            UPDATE configuration
            SET project_name = ?, location = ?, batch_folder = ?
            WHERE id = 1
            """,
            (project_name, location, batch_folder),
        )
        self.conn.commit()

    def get_configuration(self):
        self.cursor.execute(
            """
            SELECT project_name,
            location,
            batch_folder FROM configuration LIMIT 1
            """
        )
        return self.cursor.fetchone()

    def insert_batch(
        self, batch_name, folder_count, image_count, sampling_attempts, status
    ):
        self.cursor.execute(
            """
            INSERT INTO batches (batch_name, folder_count,
            image_count, sampling_attempts, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (batch_name, folder_count, image_count, sampling_attempts, status),
        )
        self.conn.commit()

    def update_batch(
        self,
        batch_name,
        subfolder_count,
        image_count,
        sampling_attempts,
        status,
    ):
        self.cursor.execute(
            """
            UPDATE batches
            SET folder_count = ?, image_count = ?,
            sampling_attempts = ?, status = ?
            WHERE batch_name = ?
            """,
            (
                subfolder_count,
                image_count,
                sampling_attempts,
                status,
                batch_name,
            ),
        )
        self.conn.commit()

    def get_batch(self, batch_name):
        self.cursor.execute(
            "SELECT * FROM batches WHERE batch_name = ?",
            (batch_name,),
        )
        return self.cursor.fetchone()

    def get_all_batches(self):
        self.cursor.execute("SELECT * FROM batches")
        return self.cursor.fetchall()

    def delete_batch(self, batch_name):
        self.cursor.execute(
            "DELETE FROM batches WHERE batch_name = ?", (batch_name,)
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
