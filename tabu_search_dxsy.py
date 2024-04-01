# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 12:34:09 2021

@author: Administrator
"""
from tabu_search import TS
from copy import deepcopy
import pandas as pd
import operator
import os
import random
import numpy as np

'''
禁忌搜索算法：地下深渊
'''
class TS_dxsy(TS):
    
    def __init__(self,max_gen,length,builder,result_path,history_file,team,threshold):
        '''
        # cache: 缓存
        # count_dict: 副将组合计数
        # builder: dxsy_builder对象
        # result_path: 结果文件路径
        # record_team_list: 记录阵容列表阵容列表
        # record_fitness_list: 记录阵容适应度列表
        # record_old_list: 历史阵容列表
        # threshold：需要记录的适应度阈值
        '''
        self.cache = {}
        self.count_dict = {}
        self.builder = builder
        self.result_path = result_path
        self.record_team_list = []
        self.record_fitness_list = []
        self.record_old_list = []
        if os.path.exists(history_file):
            old_record = pd.read_csv(history_file)
            self.record_old_list = old_record['team'].tolist()
        self.threshold = threshold
        TS.__init__(self, max_gen, length, team)
    
    def set_builder(self, builder):
        self.builder = builder
        self.cache = {}
        self.count_dict = {}
        self.record_team_list = []
        self.record_fitness_list = []
        self.neighbor = []
        self.swap_list = []
        self.current_fitness = 0.0
        self.current_fitness_list = []
        self.team_list = []
        self.best_team = []
        self.best_fitness_list = []
        self.best_fitness = 0.0
        self.tabu_list = np.random.randint(0,1,size=(self.length, 3)).tolist()
    
    def initialize(self):
        '''
        # 随机初始化一个符合规则的team
        '''
        if len(self.team) == 0:
            self.team = self.builder.generate_team()
    
    def swap(self):
        '''
        # 2-opt邻域交换，得到邻居列表，并记录交换操作
        # 从上阵英雄中替换英雄列表中符合规则的英雄
        # 从已有技能中替换技能列表中符合规则的技能
        # 记录邻居列表和交换列表
        '''
        # 记录技能学习次数
        study_num = {}
        temp_spell_list = self.builder.get_spell_list()
        for i in range(3):
            spell1,spell2 = self.builder.get_spell_by_pos(self.team, i)
            hero = self.builder.get_hero_by_pos(self.team, i)
            init_spell = self.builder.get_init_spell(hero)
            study_num[spell1] = study_num[spell1] - 1 if spell1 in study_num.keys() else self.builder.get_spell_num(spell1) - 1
            study_num[spell2] = study_num[spell2] - 1 if spell2 in study_num.keys() else self.builder.get_spell_num(spell2) - 1
            if init_spell in temp_spell_list:
                study_num[init_spell] = study_num[init_spell] - 1 if init_spell in study_num.keys() else self.builder.get_spell_num(init_spell) - 1
        # 交换英雄
        temp_hero_list = self.builder.get_hero_list()
        for i in range(3):
            hero = self.builder.get_hero_by_pos(self.team, i)
            temp_hero_list.remove(hero) # 去掉当前队伍的英雄
        for pos in range(3):
            if self.builder.check_manual(pos):
                continue
            for temp_hero in temp_hero_list:
                init_spell = self.builder.get_init_spell(temp_hero)
                if init_spell in self.builder.get_spell_by_pos(self.team, pos):
                    continue
                if init_spell in study_num.keys() and study_num[init_spell] == 0:
                    continue
                temp_team = deepcopy(self.team)
                self.builder.set_hero_by_pos(temp_team, pos, temp_hero)
                hero_tup = self.builder.get_hero_tup(temp_team)
                flag,arm_hero_count,diff_sex,diff_race,nature_list = self.builder.check_hero(hero_tup)
                if flag:
                    #quality = self.hero_dict[temp_team[0][0]][8]
                    spell_tup = self.builder.get_spell_tup(temp_team)
                    if self.builder.check_spell(spell_tup, arm_hero_count, diff_sex, diff_race, nature_list) and self.builder.check_all(temp_team):
                        self.neighbor.append(temp_team)
                        heroes = [temp_hero, self.builder.get_hero_by_pos(self.team, pos)]
                        heroes.sort()
                        self.swap_list.append((pos,heroes[0],heroes[1]))
        # 交换技能
        for k,v in study_num.items():
            if v == 0:
                temp_spell_list.remove(k) # 去掉当前队伍中可学习次数用完的技能
        for pos in range(3):
            hero = self.builder.get_hero_by_pos(self.team, pos)
            init_spell = self.builder.get_init_spell(hero)
            for spell_pos in range(2):
                for temp_spell in temp_spell_list:
                    temp_team = deepcopy(self.team)
                    if temp_spell in self.builder.get_spell_by_pos(temp_team, pos) or temp_spell == init_spell:
                        continue
                    self.builder.set_spell_by_pos(temp_team, pos, spell_pos, temp_spell)
                    hero_tup = self.builder.get_hero_tup(temp_team)
                    flag,arm_hero_count,diff_sex,diff_race,nature_list = self.builder.check_hero(hero_tup)
                    if flag:
                        #quality = self.hero_dict[temp_team[0][0]][8]
                        spell_tup = self.builder.get_spell_tup(temp_team)
                        if self.builder.check_spell(spell_tup, arm_hero_count, diff_sex, diff_race, nature_list) and self.builder.check_all(temp_team):
                             self.neighbor.append(temp_team)
                             spells = [temp_spell, self.builder.get_spell_by_pos(self.team, pos)[spell_pos]]
                             spells.sort()
                             self.swap_list.append((pos*2+spell_pos,spells[0],spells[1]))
    
    def fitness(self, team):
        '''
        # 请求战斗接口，得到阵容适应度
        '''
        #return self.builder.web_request(team)
        return random.randint(0,100)
    
    def result(self, i=0):
        res_df = pd.DataFrame()
        res_df['team'] = self.record_team_list
        res_df['fitness'] = self.record_fitness_list
        res_df.to_csv(self.result_path+'result'+str(i)+'.csv', index=False)
    
    def count_monster(self, monster_list=[]):
        '''
        # 副将组合计数
        '''
        monster_list.sort()
        key = tuple(monster_list)
        if key not in self.count_dict.keys():
            self.count_dict[key] = 0
        self.count_dict[key] += 1
    
    def judge_monster(self, monster_list=[]):
        '''
        # 副将组合判断
        '''
        monster_list.sort()
        key = tuple(monster_list)
        if key not in self.count_dict.keys():
            return False
        elif self.count_dict[key] < 10:
            return False
        return True
    
    def duplicate_monster(self, team):
        '''
        # 副将组合重复
        '''
        temp_team = eval(team)
        temp_team = [temp_team[0],temp_team[2],temp_team[1]]
        temp_team = str(temp_team)
        return (temp_team in self.record_team_list or temp_team in self.record_old_list or team in self.record_old_list)
    
    def execute(self, i=0):
        '''
        # 执行算法：每次从邻居从选择交换操作不在禁忌表中(除非满足藐视原则)的最佳阵容，并将交换操作加入禁忌表，如此迭代直到最大迭代次数或者满足停止规则
        '''
        self.initialize() # 初始化当前最佳阵容
        if self.duplicate_monster(team=str(self.team)):
            self.current_fitness = -100
        else:
            self.current_fitness = self.fitness(team=self.team) #当前阵容的适应度值
            self.cache[str(self.team)] = self.current_fitness # 缓存
        self.best_team = self.team #复制self.team到最好的阵容self.best_team
        self.best_fitness = self.current_fitness #最好的适应度值
        self.best_fitness_list.append(self.best_fitness)
        self.count_monster(monster_list=[self.builder.get_hero_by_pos(self.team, 1), self.builder.get_hero_by_pos(self.team, 2)])
        self.team_list.append(str(self.team))  # 更新当前最佳编码体的列表
        self.current_fitness_list.append(self.current_fitness)  #更新当前的最佳适应度值列表
        if self.current_fitness > self.threshold: # 记录阈值以上的阵容
            self.record_team_list.append(str(self.team))
            self.record_fitness_list.append(self.current_fitness)
        self.builder.logger.info('thread: %d  init team: %s  fitness: %d' %(i, str(self.team), self.current_fitness))
        step = 0 # 当前迭代步数
        record_len = 0 # 当前大于阈值阵容个数
        while(step < self.max_gen):
            self.swap() #产生邻居二维列表self.neighbor和交换列表self.swap_list,记住后面需要置空
            #计算每个邻居的适应度函数值
            fitness_list = []
            for temp in self.neighbor:
                temp_ = str(temp)
                if self.judge_monster(monster_list=[self.builder.get_hero_by_pos(temp, 1), self.builder.get_hero_by_pos(temp, 2)]) \
                    or self.duplicate_monster(team=temp_):
                    score = -100
                elif temp_ not in self.cache.keys():
                    score = self.fitness(team = temp)
                    self.cache[temp_] = score
                else:
                    score = self.cache[temp_]
                fitness_list.append(score)
                if score > self.threshold and temp_ not in self.record_team_list:
                    self.record_team_list.append(temp_)
                    self.record_fitness_list.append(score)
            #按照适应度函数值从大到小排定候选次序
            sorted_neighbor = sorted(zip(fitness_list,self.neighbor,self.swap_list), key=operator.itemgetter(0), reverse=True)
            self.neighbor = []  #将邻居列表置空，以便下次使用
            self.swap_list = [] #将交换列表清空
            last_team = self.team #记录上一次最佳阵容
            # 找到最佳邻居
            for temp in sorted_neighbor:
                if str(temp[1]) in self.team_list:  #跳过重复个体，避免循环
                    continue
                GN = temp[2] #交换操作
                flag = self.judgment(GN=GN)    #判断该种互换是否在禁忌表中
                if flag: #表示这个互换在禁忌表中
                    #判断藐视准则是否满足
                    if temp[0] > self.best_fitness:   #满足藐视规则                        
                        self.current_fitness = temp[0]   #更新当前最佳适应度函数值
                        self.current_fitness_list.append(self.current_fitness)   #更新当前最佳适应度函数值列表                        
                        self.team = temp[1]     #更新当前最佳阵容
                        self.team_list.append(str(self.team))            #更新当前最佳阵容的列表
                        self.best_fitness = temp[0] #更新最好的适应度函数值
                        self.best_fitness_list.append(self.best_fitness)
                        self.best_team = self.team           #更新最好的阵容
                        self.change_tabu_list(GN=GN, ignore=True)    #更新禁忌表
                        break
                else: #表示这个互换不在禁忌表中
                    self.current_fitness = temp[0] #更新当前的最佳适应度值
                    self.team = temp[1]     #更新当前最佳阵容
                    self.team_list.append(str(self.team))  #更新当前最佳阵容的列表
                    self.current_fitness_list.append(self.current_fitness)  #更新当前的最佳适应度函数值列表
                    self.change_tabu_list(GN=GN, ignore=False)    #更新禁忌表
                    if temp[0] > self.best_fitness:
                        self.best_fitness = temp[0]      #更新最好的适应度函数值
                        self.best_fitness_list.append(self.best_fitness)
                        self.best_team = self.team    #更新最好的阵容
                    break
            step += 1
            if last_team == self.team:
                self.builder.logger.info('thread: %d no team found. terminate.' %i)
                break
            self.builder.logger.info('thread: %d  step: %d  team: %s  fitness: %d' %(i, step, str(self.team), self.current_fitness))
            self.count_monster(monster_list=[self.builder.get_hero_by_pos(self.team, 1), self.builder.get_hero_by_pos(self.team, 2)])
            if len(self.record_team_list) > record_len:
                record_len = len(self.record_team_list)
                self.result(i)
            
        
            
        
        
        
        
        
        
        
        
        