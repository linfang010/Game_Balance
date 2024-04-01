# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 12:34:09 2021

@author: Administrator
"""


class Strategy(object):
    
    def initialize(self):
        '''
        # 初始化种群、个体
        '''
        raise NotImplementedError
    
    def fitness(self):
        '''
        # 计算个体适应度
        '''
        raise NotImplementedError
    
    def execute(self):
        '''
        # 执行算法
        '''
        raise NotImplementedError