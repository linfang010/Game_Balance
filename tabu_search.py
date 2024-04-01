# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 12:34:09 2021

@author: Administrator
"""
from Strategy import Strategy
import numpy as np


class TS(Strategy):
    
    def __init__(self, max_gen, length, team=[]):
        '''
        # max_gen: 最大迭代次数
        # length: 禁忌表长度
        # team: 当前阵容
        # neighbor: 邻居列表
        # swap_list: 交换操作列表
        # current_fitness: 当前最佳阵容适应度
        # current_fitness_list: 历史当前最佳阵容适应度列表
        # team_list: 历史当前最佳阵容列表
        # best_team: 历史最佳阵容
        # best_fitness_list: 历史最佳阵容适应度列表
        # best_fitness: 历史最佳阵容适应度
        # tabu_list: 禁忌表
        '''
        self.max_gen = max_gen
        self.team = team
        self.neighbor = []
        self.swap_list = []
        self.current_fitness = 0.0
        self.current_fitness_list = []
        self.team_list = []
        self.best_team = []
        self.best_fitness_list = []
        self.best_fitness = 0.0
        self.tabu_list = np.random.randint(0, 1, size=(length, 3)).tolist()  # 初始化禁忌表 (位置，英雄1，英雄2) or (位置，技能1，技能2)
        
    def initialize(self):
        '''
        # 随机初始化一个team
        '''
        raise NotImplementedError
    
    def swap(self):
        '''
        # 2-opt邻域交换,得到邻居列表,并记录交换操作
        '''
        raise NotImplementedError
    
    def judgment(self, GN=()):
        '''
        # 判断交换操作GN是否在禁忌表中
        '''
        return GN in self.tabu_list
    
    def change_tabu_list(self, GN=(), ignore=False):
        '''
        #GN: 要插入禁忌表的新交换操作
        #ignore: 用于判断是否满足藐视原则, True表示满足藐视原则
        '''
        if not ignore:
            self.tabu_list.pop()        # 弹出最后一个编码
            self.tabu_list.insert(0, GN)  # 开始位置插入新的编码
        else:
            for i, temp in enumerate(self.tabu_list):
                if GN == temp:
                    self.tabu_list.pop(i)
                    self.tabu_list.insert(0, GN)
    
    def fitness(self, team):
        '''
        # 计算阵容的适应度
        '''
        raise NotImplementedError
    
    def execute(self):
        '''
        # 执行算法：每次从邻居从选择交换操作不在禁忌表中(除非满足藐视原则)的最佳阵容，并将交换操作加入禁忌表，如此迭代直到最大迭代次数或者满足停止规则
        '''
        raise NotImplementedError