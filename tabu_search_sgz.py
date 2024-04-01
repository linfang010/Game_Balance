# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 12:34:09 2021

@author: Administrator
"""
from tabu_search import TS
from copy import deepcopy
# import pandas as pd
import operator
# import os
import random
# import numpy as np
# import json
import multiprocessing


class TS_sgz(TS):
    
    def __init__(self, max_gen, length, builder, team=[], threshold=0, mode=0, db=None):
        '''
        # builder: sgz_builder对象
        # record_team_dict: 记录阵容字典
        # threshold: 需要记录的适应度阈值
        # mode: 0-开始 1-继续
        '''
        TS.__init__(self, max_gen, length, team)
        self.mode = mode
        self.db = db
        self.builder = builder
        self.record_team_dict = {}
        self.threshold = threshold
        if mode == 0:
            self.db.clear()
            self.db.set_value('max_gen', max_gen)
            self.db.set_value('tabu_list', self.tabu_list)
            self.db.set_value('current_fitness_list', self.current_fitness_list)
            self.db.set_value('team_list', self.team_list)
            self.db.set_value('best_fitness_list', self.best_fitness_list)
            self.db.set_value('manual', builder.manual)
            self.db.set_value('record_team', self.record_team_dict)
            self.update_db(step=0)
            self.db.save_data()
        else:
            self.max_gen = self.db.get_value('max_gen')
            self.tabu_list = self.db.get_value('tabu_list')
            self.current_fitness = self.db.get_value('current_fitness_list')
            self.team_list = self.db.get_value('team_list')
            self.best_fitness_list = self.db.get_value('best_fitness_list')
            self.builder.manual = self.db.get_value('manual')
            self.record_team_dict = self.db.get_value('record_team')

    def initialize(self):
        '''
        # 随机初始化一个符合规则的team
        '''
        if len(self.team) == 0:
            self.team = self.builder.generate_team()
            
    def swap(self):
        '''
        # 2-opt邻域交换, 得到邻居列表, 并记录交换操作
        # 记录邻居列表和交换列表
        '''
        # 交换英雄
        pre_hero_list = self.builder.pre_hero_list.copy()
        post_hero_list = self.builder.post_hero_list.copy()
        for hero in self.builder.get_hero_list_by_pos(self.team):
            pre_hero_list.remove(hero)
        for hero in self.builder.get_hero_list_by_pos(self.team, False):
            post_hero_list.remove(hero)
        for pos in range(6):
            if self.builder.check_manual(pos, 0):
                continue
            hero_list = pre_hero_list if pos < 3 else post_hero_list
            for hero in hero_list:
                temp_team = deepcopy(self.team)
                self.builder.set_hero_by_pos(temp_team, pos, hero)
                self.builder.fix_team(temp_team)
                if self.builder.check_all(temp_team):
                    self.neighbor.append(temp_team)
                    heroes = [hero, self.builder.get_hero_by_pos(self.team, pos)]
                    heroes.sort()
                    self.swap_list.append((pos, heroes[0], heroes[1]))
        # 交换装备 (0:头盔 1:衣服 2:靴子 3:武器)
        head_list = self.builder.head_list.copy()
        cloth_list = self.builder.cloth_list.copy()
        boot_list = self.builder.boot_list.copy()
        weapon_list = self.builder.weapon_list.copy()
        equip_list = [head_list, cloth_list, boot_list, weapon_list]
        i = 0
        for equips in equip_list:
            for pos in range(6):
                for equip in equips:
                    if equip == self.builder.get_equip_by_pos(self.team, pos, i):
                        continue
                    temp_team = deepcopy(self.team)
                    self.builder.set_equip_by_pos(temp_team, pos, i, equip)
                    if self.builder.check_all(temp_team):
                        self.neighbor.append(temp_team)
                        temp_equips = [equip, self.builder.get_equip_by_pos(self.team, pos, i)]
                        temp_equips.sort()
                        self.swap_list.append((pos, temp_equips[0], temp_equips[1]))
            i += 1
        # 交换坐骑
        horse_list = self.builder.horse_list.copy()
        for pos in range(6):
            for horse in horse_list:
                if horse == self.builder.get_horse_by_pos(self.team, pos):
                    continue
                temp_team = deepcopy(self.team)
                self.builder.set_horse_by_pos(temp_team, pos, horse)
                if self.builder.check_all(temp_team):
                    self.neighbor.append(temp_team)
                    horses = [horse, self.builder.get_horse_by_pos(self.team, pos)]
                    horses.sort()
                    self.swap_list.append((pos, horses[0], horses[1]))
        # 交换兵种
        pre_army_list = self.builder.pre_army_list.copy()
        post_army_list = self.builder.post_army_list.copy()
        for pos in range(6):
            army_list = pre_army_list if pos < 3 else post_army_list
            for army in army_list:
                if army == self.builder.get_army_by_pos(self.team, pos):
                    continue
                temp_team = deepcopy(self.team)
                self.builder.set_army_by_pos(temp_team, pos, army)
                if self.builder.check_all(temp_team):
                    self.neighbor.append(temp_team)
                    armys = [army, self.builder.get_army_by_pos(self.team, pos)]
                    armys.sort()
                    self.swap_list.append((pos, armys[0], armys[1]))
        # 交换兵书
        for pos in range(6):
            book_list = list(self.builder.book_dict.keys())
            books = self.builder.get_book_list_by_pos(self.team, pos)
            for book in books:
                if book > 0:
                    book_list.remove(book)
            for i in range(6):
                for book in book_list:
                    temp_team = deepcopy(self.team)
                    self.builder.set_book_by_pos(temp_team, pos, i, book)
                    self.builder.fix_team(temp_team)
                    if self.builder.check_all(temp_team) and temp_team != self.team:
                        self.neighbor.append(temp_team)
                        if self.builder.get_book_by_pos(self.team, pos, i) > 0:
                            temp_books = [book, self.builder.get_book_by_pos(self.team, pos, i)]
                            temp_books.sort()
                            self.swap_list.append((pos, temp_books[0], temp_books[1]))
        # 交换宝物
        treasure_list = list(self.builder.treasure_dict.keys())
        treasures = self.builder.get_treasure_list(self.team)
        for treasure in treasures:
            if treasure > 0:
                treasure_list.remove(treasure)
        for pos in range(6):
            for i in range(3):
                for treasure in treasure_list:
                    temp_team = deepcopy(self.team)
                    self.builder.set_treasure_by_pos(temp_team, pos, i, treasure)
                    self.builder.fix_team(temp_team)
                    if self.builder.check_all(temp_team) and temp_team != self.team:
                        self.neighbor.append(temp_team)
                        if self.builder.get_treasure_by_pos(self.team, pos, i) > 0:
                            temp_treasures = [treasure, self.builder.get_treasure_by_pos(self.team, pos, i)]
                            temp_treasures.sort()
                            self.swap_list.append((pos, temp_treasures[0], temp_treasures[1]))
        # 交换任命
        for pos in range(6):
            assign_list = [0, 1, 2]
            for assign in assign_list:
                if assign == self.builder.get_assign_by_pos(self.team, pos):
                    continue
                temp_team = deepcopy(self.team)
                self.builder.set_assign_by_pos(temp_team, pos, assign)
                self.neighbor.append(temp_team)
                assigns = [assign, self.builder.get_assign_by_pos(self.team, pos)]
                assigns.sort()
                self.swap_list.append((pos, assigns[0], assigns[1]))
        # 交换军械
        junxie_list = self.builder.junxie_list.copy()
        junxie_list.remove(self.builder.get_junxie(self.team))
        for junxie in junxie_list:
            temp_team = deepcopy(self.team)
            self.builder.set_junxie(temp_team, junxie)
            self.neighbor.append(temp_team)
            junxies = [junxie, self.builder.get_junxie(self.team)]
            junxies.sort()
            self.swap_list.append((6, junxies[0], junxies[1]))
        # 交换计略
        jinue_list = self.builder.jinue_list.copy()
        for i in range(2):
            jinue_list.remove(self.builder.get_jinue(self.team, i))
        for i in range(2):
            for jinue in jinue_list:
                temp_team = deepcopy(self.team)
                self.builder.set_jinue(temp_team, i, jinue)
                self.neighbor.append(temp_team)
                jinues = [jinue, self.builder.get_jinue(self.team, i)]
                jinues.sort()
                self.swap_list.append((7, jinues[0], jinues[1]))
        # 交换阵法
        dot_list = list(self.builder.dot_dict.keys())
        dot_list.remove(self.builder.get_dot(self.team))
        for dot in dot_list:
            temp_team = deepcopy(self.team)
            self.builder.set_dot(temp_team, dot)
            self.neighbor.append(temp_team)
            dots = [dot, self.builder.get_dot(self.team)]
            dots.sort()
            self.swap_list.append((8, dots[0], dots[1]))
                
    def fitness(self, team):
        '''
        # 请求战斗接口，得到阵容适应度
        '''
        return self.builder.web_request(team)
        # return random.randint(0, 100)

    def update_db(self, step):
        self.db.set_value('current_fitness', self.current_fitness)
        self.db.set_value('best_team', self.best_team)
        self.db.set_value('best_fitness', self.best_fitness)
        self.db.set_value('team', self.team)
        self.db.set_value('gen', step)
        
    def execute(self, n_process):
        pool = multiprocessing.Pool(processes=n_process)
        '''
        # 执行算法：每次从邻居从选择交换操作不在禁忌表中(除非满足藐视原则)的最佳阵容，并将交换操作加入禁忌表，如此迭代直到最大迭代次数或者满足停止规则
        '''
        if self.mode == 0:
            self.initialize()  # 初始化当前最佳阵容
            self.current_fitness = self.fitness(team=self.team)  # 当前阵容的适应度值
            self.best_team = self.team  # 复制self.team到最好的阵容self.best_team
            self.best_fitness = self.current_fitness  # 最好的适应度值
            self.best_fitness_list.append(self.best_fitness)
            self.team_list.append(str(self.team))  # 更新当前最佳编码体的列表
            self.current_fitness_list.append(self.current_fitness)  # 更新当前的最佳适应度值列表
            if self.current_fitness > self.threshold:  # 记录阈值以上的阵容
                self.record_team_dict[str(self.team)] = self.current_fitness
            self.builder.logger.info('user_type: %d  init team: %s  fitness: %d' % (self.builder.user_type, str(self.team), self.current_fitness))
            step = 0  # 当前迭代步数
        else:
            step = self.db.get_value('gen')
            self.current_fitness = self.db.get_value('current_fitness')
            self.best_team = self.db.get_value('best_team')
            self.best_fitness = self.db.get_value('best_fitness')
            self.team = self.db.get_value('team')

        while(step < self.max_gen):
            self.swap()  # 产生邻居二维列表self.neighbor和交换列表self.swap_list,记住后面需要置空
            # 计算每个邻居的适应度函数值
            fitness_list = pool.map(self.fitness, self.neighbor)
            for score, temp in zip(fitness_list, self.neighbor):
                if score > self.threshold:
                    self.record_team_dict[str(temp)] = score
            # 按照适应度函数值从大到小排定候选次序
            sorted_neighbor = sorted(zip(fitness_list, self.neighbor, self.swap_list), key=operator.itemgetter(0), reverse=True)
            self.neighbor = []  # 将邻居列表置空，以便下次使用
            self.swap_list = []  # 将交换列表清空
            last_team = self.team  # 记录上一次最佳阵容
            # 找到最佳邻居
            for temp in sorted_neighbor:
                if str(temp[1]) in self.team_list:  # 跳过重复个体，避免循环
                    continue
                GN = temp[2]  # 交换操作
                flag = self.judgment(GN=GN)  # 判断该种互换是否在禁忌表中
                if flag:  # 表示这个互换在禁忌表中
                    # 判断藐视准则是否满足
                    if temp[0] > self.best_fitness:  # 满足藐视规则                        
                        self.current_fitness = temp[0]   # 更新当前最佳适应度函数值
                        self.current_fitness_list.append(self.current_fitness)   # 更新当前最佳适应度函数值列表                        
                        self.team = temp[1]     # 更新当前最佳阵容
                        self.team_list.append(str(self.team))            # 更新当前最佳阵容的列表
                        self.best_fitness = temp[0]  # 更新最好的适应度函数值
                        self.best_fitness_list.append(self.best_fitness)
                        self.best_team = self.team           # 更新最好的阵容
                        self.change_tabu_list(GN=GN, ignore=True)    # 更新禁忌表
                        break
                else:  # 表示这个互换不在禁忌表中
                    self.current_fitness = temp[0]  # 更新当前的最佳适应度值
                    self.team = temp[1]     # 更新当前最佳阵容
                    self.team_list.append(str(self.team))  # 更新当前最佳阵容的列表
                    self.current_fitness_list.append(self.current_fitness)  # 更新当前的最佳适应度函数值列表
                    self.change_tabu_list(GN=GN, ignore=False)    # 更新禁忌表
                    if temp[0] > self.best_fitness:
                        self.best_fitness = temp[0]      # 更新最好的适应度函数值
                        self.best_fitness_list.append(self.best_fitness)
                        self.best_team = self.team    # 更新最好的阵容
                    break
            step += 1
            if last_team == self.team:
                self.builder.logger.info('user_type: %d no team found. terminate.' % self.builder.user_type)
                break
            self.builder.logger.info('user_type: %d  step: %d  team: %s  fitness: %d' % (self.builder.user_type, step, str(self.team), self.current_fitness))
            self.update_db(step)
            self.db.save_data()
        # 执行完成
        self.builder.notify('tabu')
        pool.terminate()