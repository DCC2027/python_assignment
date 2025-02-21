import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class DBConnector():
    """class for DB connection
    """
    def __init__(self, db_path="/Users/lincong/Desktop/python_course/assignment/Dataset/functions.db"):
        """_summary_
        Args:
            db_path (str, optional): location of db file. Defaults to "/Users/lincong/Desktop/python_course/assignment/Dataset/functions.db".
        """
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

class Dataloader():
    """Parent class for dataloders. visualization fuction embedded
    """
    def __init__(self, db_connector, table_name):
        """_summary_

        Args:
            db_connector (_type_): instance of  DBConnector() as argument
            table_name (_type_): train_data/test_data/ideal_functions
        """
        self.db = db_connector
        self.table_name = table_name
        self.df = pd.read_sql("SELECT * FROM " + self.table_name, self.db.conn)
    
    def viz_df(self):
        """ generate plt.scatter for train_data/test_data/ideal_functions
        """
        num_col = len(self.df.iloc[0])
        
        x = self.df["x"].values
        num_row = len(x)
        x = np.repeat(x, num_col-1)
        y = []

        for i in range(num_row):
            y = y + self.df.iloc[i, 1:].values.tolist()
        
        plt.figure(figsize=(8, 6))
        plt.scatter(x, y, c="gray", s=1, label=self.table_name, alpha=0.7)
        # plt.yticks(np.arange(-40, 40, 5))
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.legend()
        plt.title("Visualization of data: " + self.table_name)
        plt.show()



class FunctionDataloader(Dataloader):
    """child class of Dataloader. for loading ideal_functions

    Args:
        Dataloader (_type_): _description_
    """
    def __init__(self, db_connector, table_name="ideal_functions"):
        """calling parent class Dataloader's constructor to initialize attributes

        Args:
            db_connector (_type_): _description_
            table_name (str, optional): _description_. Defaults to "ideal_functions".
        """
        super().__init__(db_connector, table_name)

class TrainDataloader(Dataloader):
    """child class of Dataloader. for loading train_data

    Args:
        Dataloader (_type_): _description_
    """
    def __init__(self, db_connector, table_name="train_data"):
        """calling parent class Dataloader's constructor to initialize attributes

        Args:
            db_connector (_type_): _description_
            table_name (str, optional): _description_. Defaults to "train_data".
        """
        super().__init__(db_connector, table_name)

class TestDataloader(Dataloader):
    """child class of Dataloader. for loading test_data

    Args:
        Dataloader (_type_): _description_
    """
    def __init__(self, db_connector, table_name="test_data"):
        """calling parent class Dataloader's constructor to initialize attributes

        Args:
            db_connector (_type_): _description_
            table_name (str, optional): _description_. Defaults to "test_data".
        """
        super().__init__(db_connector, table_name)