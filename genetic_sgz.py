# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 12:34:09 2021

@author: Administrator
"""
from genetic import GA
# import numpy as np
from deap import creator, tools, base
import random
# import os
# import pandas as pd
# import json
import multiprocessing


class GA_sgz(GA):
    
    def __init__(self, max_gen, n_pop, CXPB, MUTPB, builder, indpb=0.05, tournsize=3, threshold=0, mode=0, db=None):
        '''
        # builder: sgz_builder对象
        # record_team_dict: 记录阵容字典
        # threshold: 需要记录的适应度阈值
        # mode: 0-开始 1-继续
        # db: KeyValueDB存储算法状态
        '''
        GA.__init__(self, max_gen, n_pop, CXPB, MUTPB, indpb, tournsize)
        self.db = db
        self.mode = mode
        self.builder = builder
        self.threshold = threshold
        self.record_team_dict = {}
        if mode == 0:
            self.db.clear()
            self.db.set_value('max_gen', max_gen)
            self.db.set_value('n_pop', n_pop)
            self.db.set_value('manual', builder.manual)
            self.db.set_value('record_team', self.record_team_dict)
            self.db.set_value('gen', 0)
            self.db.save_data()
        else:
            self.max_gen = self.db.get_value('max_gen')
            self.n_pop = self.db.get_value('n_pop')
            self.builder.manual = self.db.get_value('manual')
            self.record_team_dict = self.db.get_value('record_team')
        # [[hero(6),head(4),cloth(4),boot(4),weapon(4),horse(5),army(4),book(6)*6,treasure(7)*3,assign(2)]*6,junxie(3),jinue(4)*2,dot(4)] 共555 bit
        length = 555
        for pos in range(6):
            if self.builder.check_manual(pos, 0):
                length -= 6
            if self.builder.check_manual(pos, 1):
                length -= 5
            if self.builder.check_manual(pos, 2):
                length -= 6
            if self.builder.check_manual(pos, 3):
                length -= 7
        self.length = length
        #self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_bool, length)
        #self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        #pool = multiprocessing.Pool(processes=4)
        #self.toolbox.register("map", pool.map)
    '''
    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['toolbox']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)
    '''
    def initialize(self, toolbox):
        '''
        # 随机初始化一个种群
        '''
        self.pop = toolbox.population(n=self.n_pop)
        self.db.set_value('pop', self.pop)
    
    def decode(self, individual):
        '''
        # 解码
        '''
        i = 0
        pos = 0
        team = []
        book_list = list(self.builder.book_dict.keys())
        treasure_list = list(self.builder.treasure_dict.keys())
        while i < len(individual) - 15:
            # hero(6)
            hero_list = self.builder.pre_hero_list if pos < 3 else self.builder.post_hero_list
            if not self.builder.check_manual(pos, 0):
                hero_gene = int(''.join(map(str, individual[i:i+6])), 2)
                hero = hero_list[hero_gene % len(hero_list)]
                i += 6
            else:
                hero = self.builder.get_manual(pos, 0)
            # head(4)
            head_gene = int(''.join(map(str, individual[i:i+4])), 2)
            head = self.builder.head_list[head_gene % len(self.builder.head_list)]
            i += 4
            # cloth(4)
            cloth_gene = int(''.join(map(str, individual[i:i+4])), 2)
            cloth = self.builder.cloth_list[cloth_gene % len(self.builder.cloth_list)]
            i += 4
            # boot(4)
            boot_gene = int(''.join(map(str, individual[i:i+4])), 2)
            boot = self.builder.boot_list[boot_gene % len(self.builder.boot_list)]
            i += 4
            # weapon(4)
            weapon_gene = int(''.join(map(str, individual[i:i+4])), 2)
            weapon = self.builder.weapon_list[weapon_gene % len(self.builder.weapon_list)]
            i += 4
            # horse(5)
            if not self.builder.check_manual(pos, 1):
                horse_gene = int(''.join(map(str, individual[i:i+5])), 2)
                horse = self.builder.horse_list[horse_gene % len(self.builder.horse_list)]
                i += 5
            else:
                horse = self.builder.get_manual(pos, 1)
            # army(4)
            army_list = self.builder.pre_army_list if pos < 3 else self.builder.post_army_list
            army_gene = int(''.join(map(str, individual[i:i+4])), 2)
            army = army_list[army_gene % len(army_list)]
            i += 4
            # book(6) * 6
            books = []
            if not self.builder.check_manual(pos, 2):
                book_gene = int(''.join(map(str, individual[i:i+6])), 2)
                books.append(book_list[book_gene % len(book_list)])
                i += 6
            else:
                books.append(self.builder.get_manual(pos, 2))
            for j in range(5):
                book_gene = int(''.join(map(str, individual[i:i+6])), 2)
                books.append(book_list[book_gene % len(book_list)])
                i += 6
            # treasure(7)*3
            treasures = []
            if not self.builder.check_manual(pos, 3):
                treasure_gene = int(''.join(map(str, individual[i:i+7])), 2)
                treasures.append(treasure_list[treasure_gene % len(treasure_list)])
                i += 7
            else:
                treasures.append(self.builder.get_manual(pos, 3))
            for j in range(2):
                treasure_gene = int(''.join(map(str, individual[i:i+7])), 2)
                treasures.append(treasure_list[treasure_gene % len(treasure_list)])
                i += 7
            # assign(2)
            assign_gene = int(''.join(map(str, individual[i:i+2])), 2)
            assign = assign_gene % 3
            i += 2
            team.append([hero, [head, cloth, boot, weapon], horse, army, books, treasures, assign])
            pos += 1
        # junxie(3)
        junxie_gene = int(''.join(map(str, individual[i:i+3])), 2)
        team.append(self.builder.junxie_list[junxie_gene % len(self.builder.junxie_list)])
        i += 3
        # jinue(4)*2
        jinue_list = []
        for j in range(2):
            jinue_gene = int(''.join(map(str, individual[i:i+4])), 2)
            jinue_list.append(self.builder.jinue_list[jinue_gene % len(self.builder.jinue_list)])
            i += 4
        team.append(jinue_list)
        # dot(4)
        dot_list = list(self.builder.dot_dict.keys())
        dot_gene = int(''.join(map(str, individual[i:i+4])), 2)
        team.append(dot_list[dot_gene % len(dot_list)])
        i += 4
        return team
    
    def fitness(self, individual):
        '''
        # 计算个体的适应度
        '''
        team = self.decode(individual)
        self.builder.fix_team(team)
        if not self.builder.check_all(team):
            return -100,
        score = self.builder.web_request(team)
        # score = random.randint(0, 100)
        return score,

    def execute(self, n_process):
        toolbox = base.Toolbox()
        toolbox.register("attr_bool", random.randint, 0, 1)
        toolbox.register("evaluate", self.fitness)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutFlipBit, indpb=self.indpb)
        toolbox.register("select", tools.selTournament, tournsize=self.tournsize)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, self.length)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        pool = multiprocessing.Pool(processes=n_process)
        toolbox.register("map", pool.map)
        '''
        # 执行算法
        '''
        if self.mode == 0:
            self.initialize(toolbox)
            fitnesses = toolbox.map(toolbox.evaluate, self.pop)
            for ind, fit in zip(self.pop, fitnesses):
                ind.fitness.values = fit
                if fit[0] > self.threshold:
                    team = self.decode(ind)
                    self.builder.fix_team(team)
                    self.record_team_dict[str(team)] = fit[0]
            g = 0
        else:
            g = self.db.get_value('gen')
            self.pop = self.db.get_value('pop')
        while g < self.max_gen:
            g += 1
            self.builder.logger.info("--User %d Generation %i --" % (self.builder.user_type, g))
            offspring = toolbox.select(self.pop, len(self.pop))
            offspring = list(map(toolbox.clone, offspring))
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.CXPB:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
            for mutant in offspring:
                if random.random() < self.MUTPB:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
                if fit[0] > self.threshold:
                    team = self.decode(ind)
                    self.builder.fix_team(team)
                    self.record_team_dict[str(team)] = fit[0]
            self.pop[:] = offspring
            fits = [ind.fitness.values[0] for ind in self.pop]
            length = len(self.pop)
            mean = sum(fits) / length
            sum2 = sum(x*x for x in fits)
            std = abs(sum2 / length - mean**2)**0.5
            self.builder.logger.info("Min %s Max %s Avg %s Std %s" % (min(fits), max(fits), mean, std))
            self.db.set_value('gen', g)
            self.db.save_data()
        # 执行完成
        self.builder.notify('ga')
        pool.terminate()
