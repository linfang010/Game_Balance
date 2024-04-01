# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 12:34:09 2021

@author: Administrator
"""
from genetic import GA
#import numpy as np
from deap import creator,tools
import random
import os
import pandas as pd

'''
遗传算法
'''
class GA_dxsy(GA):
    
    def __init__(self,max_gen,n_pop,CXPB,MUTPB,builder,result_path,history_file,indpb=0.05,tournsize=3,threshold=0):
        '''
        # builder: dxsy_builder对象
        # result_path: 结果文件路径
        # record_team_list: 记录阵容列表阵容列表
        # record_fitness_list: 记录阵容适应度列表
        # record_old_list: 历史阵容列表
        # threshold：需要记录的适应度阈值
        '''
        GA.__init__(self,max_gen,n_pop,CXPB,MUTPB,indpb,tournsize)
        self.builder = builder
        self.result_path = result_path
        self.threshold = threshold
        self.record_team_list = []
        self.record_fitness_list = []
        self.record_old_list = []
        if os.path.exists(history_file):
            old_record = pd.read_csv(history_file)
            self.record_old_list = old_record['team'].tolist()
        length = 54
        for pos in range(3):
            if self.builder.check_manual(pos):
                length -= 6
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_bool, length)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
    def set_builder(self, builder):    
        self.builder = builder
        self.record_team_list = []
        self.record_fitness_list = []
        self.pop = []
    
    def initialize(self):
        '''
        # 随机初始化一个种群
        '''
        self.pop = self.toolbox.population(n=self.n_pop)
    
    def decode(self, individual):
        '''
        # 解码
        '''
        i = 0
        pos = 0
        hero_key = self.builder.get_hero_list()
        spell_key = self.builder.get_spell_list()
        team = []
        while i < len(individual):
            if not self.builder.check_manual(pos):
                hero_gene = int(''.join(map(str, individual[i:i+6])), 2)
                hero = hero_key[hero_gene % len(hero_key)]
                i += 6
            else:
                hero = self.builder.get_manual(pos)
            
            spell1_gene = int(''.join(map(str, individual[i:i+6])), 2)
            spell1 = spell_key[spell1_gene % len(spell_key)]
            i += 6
           
            spell2_gene = int(''.join(map(str, individual[i:i+6])), 2)
            spell2 = spell_key[spell2_gene % len(spell_key)]
            i += 6
            
            team.append([hero,[spell1,spell2]])
            pos += 1
        return team
    
    def fitness(self, individual):
        '''
        # 计算个体的适应度
        '''
        team = self.decode(individual)
        if len(team) < 3:
            return -100,
        study_num = {}
        for i in range(3):
            spell1,spell2 = self.builder.get_spell_by_pos(team, i)
            hero = self.builder.get_hero_by_pos(team, i)
            init_spell = self.builder.get_init_spell(hero)
            if init_spell in [spell1,spell2]:
                return -100,
            if spell1 == spell2:
                return -100,
            study_num[spell1] = study_num[spell1] - 1 if spell1 in study_num.keys() else self.builder.get_spell_num(spell1) - 1
            study_num[spell2] = study_num[spell2] - 1 if spell2 in study_num.keys() else self.builder.get_spell_num(spell2) - 1
            if init_spell in self.builder.get_spell_list():
                study_num[init_spell] = study_num[init_spell] - 1 if init_spell in study_num.keys() else self.builder.get_spell_num(init_spell) - 1
        for k,v in study_num.items():
            if v < 0:
                return -100,
        hero_tup = self.builder.get_hero_tup(team)
        flag,arm_hero_count,diff_sex,diff_race,nature_list = self.builder.check_hero(hero_tup)
        if not flag:
            return -100,
        spell_tup = self.builder.get_spell_tup(team)
        if not self.builder.check_spell(spell_tup, arm_hero_count, diff_sex, diff_race, nature_list) or not self.builder.check_all(team):
            return -100,
        score = random.randint(0,100)
        if str(team) not in self.record_team_list and not self.duplicate_monster(team=str(team)) and score > self.threshold:
            self.record_team_list.append(str(team))
            self.record_fitness_list.append(score)
        return score,

    def duplicate_monster(self, team):
        '''
        # 副将组合重复
        '''
        temp_team = eval(team)
        temp_team = [temp_team[0],temp_team[2],temp_team[1]]
        temp_team = str(temp_team)
        return (temp_team in self.record_team_list or temp_team in self.record_old_list or team in self.record_old_list)
    
    def result(self, i=0):
        res_df = pd.DataFrame()
        res_df['team'] = self.record_team_list
        res_df['fitness'] = self.record_fitness_list
        res_df.to_csv(self.result_path+'result'+str(i)+'.csv', index=False)
    
    def execute(self, i=0):
        '''
        # 执行算法
        '''
        self.initialize()
        fitnesses = list(map(self.toolbox.evaluate, self.pop))
        for ind, fit in zip(self.pop, fitnesses):
            ind.fitness.values = fit
        #fits = [ind.fitness.values[0] for ind in pop]
        g = 0
        record_len = 0
        while g < self.max_gen:
            g += 1
            self.builder.logger.info("-- Generation %i --" %g)
            offspring = self.toolbox.select(self.pop, len(self.pop))
            offspring = list(map(self.toolbox.clone, offspring))
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.CXPB:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
            for mutant in offspring:
                if random.random() < self.MUTPB:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            self.pop[:] = offspring
            fits = [ind.fitness.values[0] for ind in self.pop]
            length = len(self.pop)
            mean = sum(fits) / length
            sum2 = sum(x*x for x in fits)
            std = abs(sum2 / length - mean**2)**0.5
            self.builder.logger.info("Min %s Max %s Avg %s Std %s" %(min(fits),max(fits),mean,std))
            if len(self.record_team_list) > record_len:
                record_len = len(self.record_team_list)
                self.result(i)