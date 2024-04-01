# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 12:34:09 2021

@author: Administrator
"""


class Builder(object):

    def __parse(self):
        '''
        # 解析游戏数据文件，例如英雄、技能、装备
        # 私有方法, 仅在具体builder构造时调用
        '''
        raise NotImplementedError
    
    def generate_team(self):
        '''
        # 随机生成符合游戏规则的阵容
        '''
        raise NotImplementedError
    
    def web_request(self):
        '''
        # 请求战斗接口
        '''
        raise NotImplementedError