import json
import logging
from labelsmith.shyft.constants import DATA_FILE_PATH, LOGS_DIR

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        self.data = {"data": {}}
        self.load_data()

    def load_data(self):
        try:
            if DATA_FILE_PATH.exists():
                with open(DATA_FILE_PATH, "r") as f:
                    self.data = json.load(f)
            logger.info(f"Loaded data: {self.data}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except Exception as e:
            logger.error(f"Failed to load data file: {e}")

    def save_data(self):
        try:
            with open(DATA_FILE_PATH, "w") as f:
                json.dump(self.data, f, indent=4)
            logger.debug("Data saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            raise

    def get_shifts(self):
        return self.data["data"]

    def add_shift(self, shift_id, shift_data):
        self.data["data"][shift_id] = shift_data
        self.save_data()

    def update_shift(self, shift_id, shift_data):
        if shift_id in self.data["data"]:
            self.data["data"][shift_id] = shift_data
            self.save_data()
        else:
            raise KeyError(f"Shift with ID {shift_id} not found.")

    def delete_shift(self, shift_id):
        if shift_id in self.data["data"]:
            del self.data["data"][shift_id]
            self.save_data()
        else:
            raise KeyError(f"Shift with ID {shift_id} not found.")

    def get_max_shift_id(self):
        return max([int(x) for x in self.data["data"].keys()], default=0)

# Initialize the DataManager
data_manager = DataManager()