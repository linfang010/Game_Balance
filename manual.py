#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 09:33:50 2019

@author: lilnfang
"""
import logging
from Util import util_balance
#from dxsy_builder import dxsy_builder
#from tabu_search_dxsy import TS_dxsy
#from genetic_dxsy import GA_dxsy
from sgz_builder import sgz_builder
from genetic_sgz import GA_sgz
from tabu_search_sgz import TS_sgz
from deap import creator,base
from KeyValueDB import KeyValueDB
from pathlib import Path


logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger()
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

'''
def dxsy_search_tabu():
    ub = util_balance(logger, 'config.xml')
    max_gen = 5
    length = 5
    manual=(0,0,0)
    team = []
    threshold = 0
    builder = dxsy_builder(ub.config['hero_file'],ub.config['spell_file'],ub.config['url'],logger,manual)
    strategy = TS_dxsy(max_gen,length,builder,ub.config['result'],ub.config['history_file'],team,threshold)
    hero_list = builder.get_hero_list()
    for i in range(len(hero_list)):
        builder.set_manual((hero_list[i],0,0))
        strategy.set_builder(builder)
        strategy.execute(i)


def dxsy_search_ga():
    ub = util_balance(logger, 'config.xml')
    manual = (0,0,0)
    indpb = 0.05
    tournsize = 3
    threshold = 0
    max_gen = 1000
    n_pop = 300
    CXPB = 0.5
    MUTPB =0.2
    builder = dxsy_builder(ub.config['hero_file'],ub.config['spell_file'],ub.config['url'],logger,manual)
    strategy = GA_dxsy(max_gen,n_pop,CXPB,MUTPB,builder,ub.config['result'],ub.config['history_file'],indpb,tournsize,threshold)
    hero_list = builder.get_hero_list()
    for i in range(len(hero_list)):
        builder.set_manual((hero_list[i],0,0))
        strategy.set_builder(builder)
        strategy.execute(i)
'''

def sgz_search_ga():
    ub = util_balance(logger, 'config.xml')
    manual = ((0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0))
    indpb = 0.05
    tournsize = 3
    threshold = 0
    max_gen = 50
    n_pop = 1000
    CXPB = 0.5
    MUTPB = 0.2
    user_type = 0
    mode = 0
    result_path = Path(ub.config['result'])
    file_path = result_path / ('result_ga_'+str(user_type)+'.dat')
    db = KeyValueDB(file_path)
    builder = sgz_builder(ub.config['hero_file'],ub.config['equip_file'],ub.config['horse_file'],ub.config['army_file'],
                          ub.config['book_file'],ub.config['treasure_file'],ub.config['junxie_file'],ub.config['jinue_file'],
                          ub.config['qishu_file'],ub.config['keji_file'], ub.config['castle_file'], ub.config['dot_file'], ub.config['hero_army_file'],
                          ub.config['ga_url'],logger,manual,user_type)
    strategy = GA_sgz(max_gen,n_pop,CXPB,MUTPB,builder,indpb,tournsize,threshold,mode,db)
    strategy.execute(int(ub.config['process']))
    

def sgz_search_tabu():
    ub = util_balance(logger, 'config.xml')
    manual = ((0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0))
    max_gen = 50
    length = 10
    #team = [[10436, [20016, 20221, 20418, 20620], 22321, 103012, [105511, 105311, 105518, 105517, 105601, 0], [12241, 0, 0], 1], [10234, [20016, 20212, 20407, 20609], 22303, 103005, [105328, 105408, 105406, 105309, 105601, 0], [12372, 0, 0], 2], [10007, [20016, 20219, 20407, 20606], 22321, 102006, [105410, 105405, 105511, 105601, 105407, 0], [12355, 12352, 0], 1], [10044, [20006, 20220, 20406, 20607], 22310, 103009, [105326, 105327, 105320, 105511, 105302, 0], [12415, 0, 0], 2], [10409, [20007, 20213, 20416, 20610], 22315, 103008, [105511, 105318, 105411, 105414, 105520, 0], [12314, 12362, 0], 0], [10653, [20017, 20209, 20410, 20621], 22303, 103008, [105509, 105301, 105405, 105511, 105305, 0], [12369, 12414, 0], 1], 23501, [26701, 26901], 10090211]
    team = [[10436, [20016, 20221, 20418, 20620], 22321, 103012, [105511, 105311, 105518, 105517, 105601, 0], [12241, 0, 0], 1], [10234, [20016, 20212, 20407, 20609], 22303, 103005, [105328, 105408, 105406, 105309, 105601, 0], [12372, 0, 0], 2], [10007, [20016, 20219, 20407, 20606], 22321, 102006, [105410, 105405, 105511, 105601, 105407, 0], [12355, 12352, 0], 1], [10044, [20006, 20220, 20406, 20607], 22321, 103009, [105326, 105327, 105320, 105511, 105302, 0], [12415, 0, 0], 2], [10409, [20007, 20213, 20416, 20610], 22315, 103008, [105511, 105318, 105411, 105414, 105520, 0], [12314, 12362, 0], 0], [10653, [20017, 20209, 20410, 20621], 22303, 103008, [105509, 105301, 105405, 105511, 105305, 0], [12369, 12414, 0], 1], 23501, [26701, 26901], 10090211]
    threshold = 0
    user_type = 0
    mode = 0
    result_path = Path(ub.config['result'])
    file_path = result_path / ('result_tabu_'+str(user_type)+'.dat')
    db = KeyValueDB(file_path)
    builder = sgz_builder(ub.config['hero_file'],ub.config['equip_file'],ub.config['horse_file'],ub.config['army_file'],
                          ub.config['book_file'],ub.config['treasure_file'],ub.config['junxie_file'],ub.config['jinue_file'],
                          ub.config['qishu_file'],ub.config['keji_file'], ub.config['castle_file'], ub.config['dot_file'], ub.config['hero_army_file'],
                          ub.config['tabu_url'],logger,manual,user_type)
    strategy = TS_sgz(max_gen,length,builder,team,threshold,mode,db)
    strategy.execute(int(ub.config['process']))



if __name__ == "__main__":
    #sgz_search_ga()
    sgz_search_tabu() 
    
    
