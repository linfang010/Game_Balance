#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 09:33:50 2019

@author: lilnfang
"""
import requests
import json
import pandas as pd
import random


def complete():
    url = 'http://192.168.10.72:10001/sanguo/ai/combination/complete'
    status_code = - 100
    try:
        res = requests.get(url, timeout=10)
        status_code = res.status_code
    except Exception as e:
        print(e)
    return status_code
    

def web_request(team, army_dict={}, science=[], hero_dict={}, mount_skill={}, castle=[], dot_dict={}, hero_army_dict={}):
    
    team_dict = {}
    # 阶段 0超R 1大R+ 2大R 3中R+ 4中R 5小R 6平民
    team_dict['stage'] = 0
    # 计略
    skill36 = []
    for jinue in team[7]:
        temp = {}
        temp['sid'] = jinue
        skill36.append(temp)
    team_dict['skill36'] = skill36
    # 科技
    team_dict['science'] = science
    # 皮肤联动
    team_dict['castleLinkage'] = castle
    # 军械
    team_dict['ordnance'] = {'sid': team[6]}
    # 阵法
    team_dict['dotMatrix'] = {'sid':team[8],'level': dot_dict[team[8]][0]}
    # 武将
    cards = []
    for pos in range(6):
        temp = {}
        temp['sid'] = team[pos][0] # 武将
        temp['name'] = hero_dict[team[pos][0]][3]
        temp['pos'] = pos
        temp['breakAwaken'] = hero_dict[team[pos][0]][0] # 突破
        temp['intimacy'] = hero_dict[team[pos][0]][1] # 亲密度
        temp['position'] = hero_dict[team[pos][0]][2] # 拜官
        temp['soldiersType'] = army_dict[team[pos][3]][0]
        temp['soldiersSid'] = team[pos][3] # 兵种
        temp['soldiersLv'] = hero_army_dict[team[pos][0]][team[pos][3]]
        temp['appointment'] = team[pos][6] # 任命
        temp['mountSkill'] = mount_skill[pos] # 骑术
        temp['equipments'] = {'weaponSid':team[pos][1][3],'helmetSid':team[pos][1][0],'armourSid':team[pos][1][1],'shoeSid':team[pos][1][2]}
        temp['treasure'] = {'sid':team[pos][5]}
        temp['book'] = {'sid':team[pos][4]}
        temp['mount'] = {'sid':team[pos][2]}
        cards.append(temp)
    team_dict['cards'] = cards
    json_res = json.dumps(team_dict)
    print (json_res)
    score = -100
    headers = {'Content-Type': 'application/json'}
    url = 'http://192.168.10.72:10001/sanguo/ai/combination/fight'
    try:
        res = requests.post(url, headers=headers, data=json_res, timeout=60)
        if res.status_code == 200:
            text = json.loads(res.text)
            if text['status'] == 200:
                score = text['data']['intensityScore']
            else:
                print ('fight request error! status: %d' %text['status'])
        else:
            print('http code: %d, http content: %s' %(res.status_code, res.text))
    except Exception as e:
        print(e)
    
    return score
    





if __name__ == "__main__":

    with open('result/result0.json','r') as f:
        data = json.load(f)
    team = random.choice(list(data.keys()))
    team = eval(team)
    
    army_df = pd.read_csv('data/army.csv')
    army_dict = {}
    for index,row in army_df.iterrows():
        type_ = int(row['type'])
        army_dict[int(row['id'])] = (type_,)
    
    hero_df = pd.read_csv('data/hero.csv')
    hero_df = hero_df[hero_df['user_type'] == 0]
    hero_dict = {}
    hero_army_dict = {}
    for index,row in hero_df.iterrows():
        # id : (upgrade,intimacy,baiguan,name,tag,progress,quality)
        position = int(row['position'])
        upgrade = int(row['break'])
        intimacy = int(row['intimacy'])
        baiguan = int(row['baiguan'])
        tag = int(row['tag'])
        quality = int(row['quality'])
        name = row['name']
        hero_dict[int(row['id'])] = (upgrade,intimacy,baiguan,name,tag,quality)
        hero_army_dict[int(row['id'])] = {}
    
    science_df = pd.read_csv('data/science.csv')
    science_df = science_df[science_df['user_type'] == 0]
    science = []
    for index,row in science_df.iterrows():
        science.append({'sid':int(row['id']), 'level':int(row['level'])})
    
    mount_skill_df = pd.read_csv('data/qishu.csv')
    mount_skill_df = mount_skill_df[mount_skill_df['user_type'] == 0]
    mount_skill = {0:[],1:[],2:[],3:[],4:[],5:[]}
    for index,row in mount_skill_df.iterrows():
        # position : [{sid,level}]
        mount_skill[row['position']].append({'sid':int(row['id']), 'level':int(row['level'])})
    
    castle_df = pd.read_csv('data/castle.csv')
    castle_df = castle_df[castle_df['user_type'] == 0]
    castle = []
    for index,row in castle_df.iterrows():
        castle.append({'sid':int(row['id']), 'level':int(row['level'])})
    
    dot_df = pd.read_csv('data/dot.csv')
    dot_df = dot_df[dot_df['user_type'] == 0]
    dot_dict = {}
    for index,row in dot_df.iterrows():
        # id: (level,)
        level = int(row['level'])
        dot_dict[int(row['id'])] = (level,)
    
    hero_army_df = pd.read_csv('data/hero_army.csv')
    hero_army_df = hero_army_df[hero_army_df['user_type'] == 0]
    for index,row in hero_army_df.iterrows():
        hero_army_dict[int(row['hero'])][int(row['army'])] = int(row['level'])
    
    score = web_request(team, army_dict, science, hero_dict, mount_skill, castle, dot_dict, hero_army_dict)
    print (f'score: {score}')
    #status = complete()
        
    
    
