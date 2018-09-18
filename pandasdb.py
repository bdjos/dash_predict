# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 08:41:03 2018

@author: BJoseph
"""

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, DateTime
import pandas as pd

class pandasdb():
    def __init__(self, database, password, host):
        self.database = database
        self.password = password
        self.host = host
        
        self.engine = create_engine(f'postgresql://{self.database}:{self.password}@{self.host}:5432/{self.database}')
        
    def pd_to_db(self, dtypes, df, if_exists, table):
        if len(dtypes) != len(df.columns):
            print('len of dtypes must equal number of columns')
        else:
            dtypes_dict = dict(zip(list(df.columns), dtypes))
            print(dtypes_dict)
        
            df.to_sql(name = table, con = self.engine, if_exists = if_exists, index = False, dtype = dtypes_dict)

    def pd_from_db(self, table):
        df = pd.read_sql(table, con = self.engine)
        
        return df