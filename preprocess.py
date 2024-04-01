#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 09:33:50 2019

@author: lilnfang
"""
import pandas as pd


def deal_hero(hero, baiguan, qinmidu, tupo):
    baiguan.rename(columns={'gen_sid':'id','official_level':'baiguan'},inplace=True)
    qinmidu.rename(columns={'gen_sid':'id','intimacy_level':'intimacy'},inplace=True)
    tupo.rename(columns={'gen_sid':'id','over_level':'break'}, inplace=True)
    temp = pd.merge(baiguan,qinmidu,how='inner',on=['id','user_type'])
    temp = temp.merge(tupo,how='inner',on=['id','user_type'])
    final = temp.merge(hero,how='inner',on='id')
    return final

def deal_treasure(treasure, temp_t):
    temp_t.rename(columns={'t_sid':'id'}, inplace=True)
    final = temp_t.merge(treasure,how='inner',on='id')
    return final

def deal_book(book, temp_b):
    temp_b.rename(columns={'book_sid':'id'}, inplace=True)
    final = temp_b.merge(book, how='inner', on='id')
    return final

def deal_hero_army(hero, army):
    result = []
    for index,row in hero.iterrows():
        hero_id = int(row['id'])
        hero_pos = int(row['position'])
        user_type = int(row['user_type'])
        for index,row in army.iterrows():
            res = {}
            res['hero'] = hero_id
            if hero_pos != 3 and hero_pos != int(row['position']):
                continue
            res['army'] = int(row['id'])
            res['user_type'] = user_type
            result.append(res)
    result = pd.DataFrame(result)
    result['level'] = 30
    return result

def deal_equip(equip, temp_e):
    temp_e.rename(columns={'eq_sid':'id'}, inplace=True)
    final = temp_e.merge(equip,how='inner',on='id')
    return final

def deal_horse(horse, temp_h):
    temp_h.rename(columns={'mou_sid':'id'}, inplace=True)
    final = temp_h.merge(horse,how='inner', on='id')
    return final
    
    
        



if __name__ == "__main__":
    # 武将
    hero = pd.read_csv('data/local/hero.csv')
    baiguan = pd.read_csv('data/Downloads/拜官.csv')
    qinmidu = pd.read_csv('data/Downloads/亲密度.csv')
    tupo = pd.read_csv('data/Downloads/突破等级.csv')
    final_hero = deal_hero(hero, baiguan, qinmidu, tupo)
    final_hero.to_csv('data/hero.csv', index=False)
    # 宝物
    treasure = pd.read_csv('data/local/treasure.csv')
    temp_t = pd.read_csv('data/Downloads/宝物.csv')
    final_treasure = deal_treasure(treasure, temp_t)
    final_treasure.to_csv('data/treasure.csv', index=False)
    # 兵书
    book = pd.read_csv('data/local/book.csv')
    temp_b = pd.read_csv('data/Downloads/兵书.csv')
    final_book = deal_book(book, temp_b)
    final_book.to_csv('data/book.csv', index=False)
    # 兵种
    army = pd.read_csv('data/army.csv')
    hero = pd.read_csv('data/hero.csv')
    final_hero_army = deal_hero_army(hero, army)
    final_hero_army.to_csv('data/hero_army.csv', index=False)
    # 皮肤
    castle = pd.read_csv('data/Downloads/皮肤联动.csv')
    castle.rename(columns={'skin_id':'id','skin_level':'level'}, inplace=True)
    castle.to_csv('data/castle.csv', index=False)
    # 骑术
    qishu = pd.read_csv('data/Downloads/骑术等级.csv')
    qishu.rename(columns={'ride_id':'id','ride_level':'level'}, inplace=True)
    qishu.to_csv('data/qishu.csv', index=False)
    # 科技
    science = pd.read_csv('data/Downloads/战斗科技.csv')
    science.rename(columns={'tec_id':'id','tec_level':'level'}, inplace=True)
    science.to_csv('data/science.csv', index=False)
    # 阵法
    dot = pd.read_csv('data/Downloads/阵法等级.csv')
    dot.rename(columns={'msid':'id','mlv':'level'}, inplace=True)
    dot = dot[dot['id'] > 0]
    dot.to_csv('data/dot.csv', index=False)
    # 装备
    equip = pd.read_csv('data/local/equip.csv')
    temp_e = pd.read_csv('data/Downloads/装备.csv')
    final_equip = deal_equip(equip, temp_e)
    final_equip.to_csv('data/equip.csv', index=False)
    # 坐骑
    horse = pd.read_csv('data/local/horse.csv')
    temp_h = pd.read_csv('data/Downloads/坐骑.csv')
    final_horse = deal_horse(horse, temp_h)
    final_horse.to_csv('data/horse.csv', index=False)
    
    
    
    
    
    
    