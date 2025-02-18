import sqlite3
import pandas as pd

class DBConnector():
    def __init__(self, db_path="/Users/lincong/Desktop/python_course/assignment/Dataset/functions.db"):
        """_summary_

        Args:
            db_path (str, optional): _description_. Defaults to "/Users/lincong/Desktop/python_course/assignment/Dataset/functions.db".
        """
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

class Dataloader():
    """Parent class for data loders
    """
    def __init__(self, db_connector, table_name):
        """_summary_

        Args:
            db_connector (_type_): _description_
            table_name (_type_): _description_
        """
        self.db = db_connector
        self.table_name = table_name
        self.df = pd.read_sql("SELECT * FROM " + self.table_name, self.db.conn)


class FunctionDataloader(Dataloader):
    def __init__(self, db_connector, table_name="ideal_functions"):
        super().__init__(db_connector, table_name)

class TrainDataloader(Dataloader):
    def __init__(self, db_connector, table_name="train_data"):
        super().__init__(db_connector, table_name)

class TestDataloader(Dataloader):
    def __init__(self, db_connector, table_name="test_data"):
        super().__init__(db_connector, table_name)