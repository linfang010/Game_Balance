#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 09:33:50 2019

@author: lilnfang
"""

import xml.etree.ElementTree as ET
# import pandas as pd
import sys
# from sqlalchemy import create_engine


class util_balance(object):
    
    def __init__(self, logger, path):
        self.engine = None
        self.logger = logger
        self.config = {}
        self._read_config(path)
        if len(self.config) == 0:
            self.logger.error("read config error!")
            sys.exit()
        # self._create_db()
    '''
    def __del__(self):
        self.engine.dispose()
    '''
    def _read_config(self, path):
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            self.config['hero_file'] = root.find('hero_file').text
            self.config['equip_file'] = root.find('equip_file').text
            self.config['horse_file'] = root.find('horse_file').text
            self.config['army_file'] = root.find('army_file').text
            self.config['book_file'] = root.find('book_file').text
            self.config['treasure_file'] = root.find('treasure_file').text
            self.config['junxie_file'] = root.find('junxie_file').text
            self.config['jinue_file'] = root.find('jinue_file').text
            self.config['qishu_file'] = root.find('qishu_file').text
            self.config['keji_file'] = root.find('keji_file').text
            self.config['castle_file'] = root.find('castle_file').text
            self.config['dot_file'] = root.find('dot_file').text
            self.config['hero_army_file'] = root.find('hero_army_file').text
            self.config['tabu_url'] = root.find('tabu_url').text
            self.config['ga_url'] = root.find('ga_url').text
            self.config['result'] = root.find('result').text
            self.config['http_port'] = root.find('HTTP').text
            self.config['process'] = root.find('process').text
        except Exception as e:
            self.logger.error(e)
            self.config = {}
    '''
    def _create_db(self):
        self.engine = create_engine(
        "mysql+pymysql://%s:%s@%s:%s/%s"
        % (self.config["user"], self.config["passwd"], self.config["host"], self.config["port"], self.config["name"]),
        pool_recycle=3600
        )
    
    def _handle_sql(self, sql):
        try:
            res = pd.read_sql(sql, self.engine)
        except Exception as e:
            self.logger.error(e)
            res = pd.DataFrame()
        return res

    def _write_sql(self, df, name):
        try:
            df.to_sql(name, self.engine, if_exists='append', index=False)
        except Exception as e:
            self.logger.error(e)
            df.to_csv('temp/'+name+'.csv', index=False)
    
    def _execute_sql(self, sql):
        try:
            db_con = self.engine.connect()
            db_con.execute(sql)
            db_con.close()
        except Exception as e:
            self.logger.error(e)
    '''  
        
        
