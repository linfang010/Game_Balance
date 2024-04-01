# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 12:34:09 2021

@author: Administrator
"""
from os import cpu_count
from Strategy import Strategy
# import numpy as np
from deap import base, tools
import random


class GA(Strategy):
    
    def __init__(self, max_gen, n_pop, CXPB, MUTPB, indpb, tournsize):
        '''
        # max_gen: 最大迭代次数
        # n_pop: 种群数量
        # CXPB: 交叉概率
        # MUTPB: 变异概率
        
        '''
        self.max_gen = max_gen
        self.n_pop = n_pop
        self.CXPB = CXPB
        self.MUTPB = MUTPB
        self.pop = []
        self.indpb = indpb
        self.tournsize = tournsize
        '''
        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_bool", random.randint, 0, 1)
        self.toolbox.register("evaluate", self.fitness)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutFlipBit, indpb=indpb)
        self.toolbox.register("select", tools.selTournament, tournsize=tournsize)
        '''
    def initialize(self):
        '''
        # 随机初始化一个种群
        '''
        raise NotImplementedError
    
    def decode(self, individual):
        '''
        # 解码
        '''
        raise NotImplementedError
    
    def fitness(self, individual):
        '''
        # 计算个体的适应度
        '''
        raise NotImplementedError
    
    def execute(self):
        '''
        # 执行算法
        '''
        raise NotImplementedError