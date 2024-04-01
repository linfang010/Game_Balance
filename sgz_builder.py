# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 12:34:09 2021

@author: Administrator
"""
from Builder import Builder
import pandas as pd
import random
# from itertools import combinations
import requests
import json


class sgz_builder(Builder):
    
    def __init__(self, hero_filepath, equip_filepath, horse_filepath, army_filepath, book_filepath, treasure_filepath, junxie_filepath, jinue_filepath, 
                 qishu_filepath, keji_filepath, castle_filepath, dot_filepath, hero_army_filepath, url, logger, manual, user_type):
        '''
        # hero_filepath: 英雄文件路径
        # equip_filepath: 装备文件路径
        # horse_filepath: 坐骑文件路径
        # army_filepath: 兵种文件路径
        # book_filepath: 兵书文件路径
        # treasure_filepath: 宝物文件路径
        # junxie_filepath: 军械文件路径
        # jinue_filepath: 计略文件路径
        # url: 战斗接口地址
        # manual: 固定主将
        # hero_dict: 英雄字典
        # equip_dict: 装备字典
        # horse_dict: 坐骑字典
        # army_dict: 兵种字典
        # book_dict: 兵书字典
        # treasure_dict: 宝物字典
        # junxie_list: 军械列表
        # jinue_list: 计略列表
        # head_list: 头盔列表
        # cloth_list: 衣服列表
        # boot_list: 鞋子列表
        # weapon_list: 武器列表
        # horse_list: 坐骑列表
        # pre_hero_list: 前排英雄列表
        # post_hero_list: 后排英雄列表
        # pre_army_list: 前排兵种列表
        # post_army_list: 后排兵种列表
        # logger: logging日志对象
        # user_type: 玩家类型
        '''
        self.logger = logger
        self.hero_filepath = hero_filepath
        self.equip_filepath = equip_filepath
        self.horse_filepath = horse_filepath
        self.army_filepath = army_filepath
        self.book_filepath = book_filepath
        self.treasure_filepath = treasure_filepath
        self.junxie_filepath = junxie_filepath
        self.jinue_filepath = jinue_filepath
        self.qishu_filepath = qishu_filepath
        self.keji_filepath = keji_filepath
        self.castle_filepath = castle_filepath
        self.dot_filepath = dot_filepath
        self.hero_army_filepath = hero_army_filepath
        self.url = url
        self.manual = manual
        self.user_type = user_type
        self.hero_dict = {}
        self.equip_dict = {}
        self.horse_dict = {}
        self.army_dict = {}
        self.book_dict = {}
        self.treasure_dict = {}
        self.junxie_list = []
        self.jinue_list = []
        self.head_list = []
        self.cloth_list = []
        self.boot_list = []
        self.weapon_list = []
        self.horse_list = []
        self.pre_hero_list = []
        self.post_hero_list = []
        self.pre_army_list = []
        self.post_army_list = []
        self.mount_skill = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}
        self.science = []
        self.castle = []
        self.dot_dict = {}
        self.hero_army_dict = {}
        self.__parse()
        
    def __parse(self):
        # 英雄
        hero_df = pd.read_csv(self.hero_filepath)
        hero_df = hero_df[hero_df['user_type'] == self.user_type]
        for index, row in hero_df.iterrows():
            # id : (upgrade,intimacy,baiguan,name,tag,quality)
            position = int(row['position'])
            upgrade = int(row['break'])
            intimacy = int(row['intimacy'])
            baiguan = int(row['baiguan'])
            tag = int(row['tag'])
            quality = int(row['quality'])
            name = row['name']
            self.hero_dict[int(row['id'])] = (upgrade, intimacy, baiguan, name, tag, quality)
            self.hero_army_dict[int(row['id'])] = {}
            if position == 1:
                self.pre_hero_list.append(int(row['id']))
            elif position == 2:
                self.post_hero_list.append(int(row['id']))
            elif position == 3:
                self.pre_hero_list.append(int(row['id']))
                self.post_hero_list.append(int(row['id']))
        # 装备    
        equip_df = pd.read_csv(self.equip_filepath)
        equip_df = equip_df[equip_df['user_type'] == self.user_type]
        for index, row in equip_df.iterrows():
            position = int(row['position'])
            num = int(row['num'])
            self.equip_dict[int(row['id'])] = (num,) 
            if position == 1:
                # 头盔
                self.head_list.append(int(row['id']))
            elif position == 2:
                # 衣服
                self.cloth_list.append(int(row['id']))
            elif position == 3:
                # 靴子
                self.boot_list.append(int(row['id']))
            elif position == 4:
                # 武器
                self.weapon_list.append(int(row['id']))
        # 坐骑
        horse_df = pd.read_csv(self.horse_filepath)
        horse_df = horse_df[horse_df['user_type'] == self.user_type]
        self.horse_list = horse_df['id'].tolist()
        for index, row in horse_df.iterrows():
            num = int(row['num'])
            self.horse_dict[int(row['id'])] = (num,)
        # 兵种
        army_df = pd.read_csv(self.army_filepath)
        for index, row in army_df.iterrows():
            # id: (type)
            position = int(row['position'])
            type_ = int(row['type'])
            self.army_dict[int(row['id'])] = (type_,)
            self.pre_army_list.append(int(row['id'])) if position == 1 else self.post_army_list.append(int(row['id']))
        # 兵书
        book_df = pd.read_csv(self.book_filepath)
        book_df = book_df[book_df['user_type'] == self.user_type]
        for index, row in book_df.iterrows():
            # id: (tag,num)
            tag = int(row['tag'])
            num = int(row['num'])
            self.book_dict[int(row['id'])] = (tag, num)
        # 宝物
        treasure_df = pd.read_csv(self.treasure_filepath)
        treasure_df = treasure_df[treasure_df['user_type'] == self.user_type]
        for index, row in treasure_df.iterrows():
            # id: (tag,special)
            tag = int(row['tag'])
            special = int(row['special'])
            self.treasure_dict[int(row['id'])] = (tag, special)
        # 军械
        junxie_df = pd.read_csv(self.junxie_filepath)
        self.junxie_list = junxie_df['id'].tolist()
        # 计略
        jinue_df = pd.read_csv(self.jinue_filepath)
        self.jinue_list = jinue_df['id'].tolist()
        # 骑术
        mount_skill_df = pd.read_csv(self.qishu_filepath)
        mount_skill_df = mount_skill_df[mount_skill_df['user_type'] == self.user_type]
        for index, row in mount_skill_df.iterrows():
            # position : [{sid,level}]
            self.mount_skill[row['position']].append({'sid': int(row['id']), 'level': int(row['level'])})
        # 科技
        science_df = pd.read_csv(self.keji_filepath)
        science_df = science_df[science_df['user_type'] == self.user_type]
        for index, row in science_df.iterrows():
            self.science.append({'sid': int(row['id']), 'level': int(row['level'])})
        # 皮肤
        castle_df = pd.read_csv(self.castle_filepath)
        castle_df = castle_df[castle_df['user_type'] == self.user_type]
        for index, row in castle_df.iterrows():
            self.castle.append({'sid': int(row['id']), 'level': int(row['level'])})
        # 阵法
        dot_df = pd.read_csv(self.dot_filepath)
        dot_df = dot_df[dot_df['user_type'] == self.user_type]
        for index, row in dot_df.iterrows():
            # id: (level,)
            level = int(row['level'])
            self.dot_dict[int(row['id'])] = (level,)
        # 英雄兵种等级
        hero_army_df = pd.read_csv(self.hero_army_filepath)
        hero_army_df = hero_army_df[hero_army_df['user_type'] == self.user_type]
        for index, row in hero_army_df.iterrows():
            self.hero_army_dict[int(row['hero'])][int(row['army'])] = int(row['level'])
        
    def book_num(self, quality, upgrade):
        '''
        初始橙色武将:
        1-7    橙色+1 - 橙色+7
        8      红色+0
        9-15   红色+1 - 红色+7
        16     金色+0
        17-23  金色+1 - 金色+7
        初始红色武将：
        1-7    红色+1 - 红色+7
        8      金色+0
        9-15   金色+1 - 金色+7
        '''
        return quality + ((upgrade - 1) // 8) if upgrade > 0 else quality - 1
    
    def treasure_num(self, quality, upgrade):
        if quality == 4:  # 橙将
            return 3 if upgrade >= 22 else (2 if upgrade >= 4 else 1)
        elif quality == 5:  # 红将
            return 3 if upgrade >= 14 else (2 if upgrade >= 4 else 1)
        elif quality == 6:  # 紫金
            return 3 if upgrade >= 6 else (2 if upgrade >= 4 else 1)
        else:
            self.logger.error('error hero quality: %d' % quality)
            return 1
            
    def fix_team(self, team):
        for i in range(6):
            # 武将佩戴兵书数量
            hero = team[i][0]
            quality = self.hero_dict[hero][5]
            upgrade = self.hero_dict[hero][0]
            books = team[i][4]
            index = self.book_num(quality, upgrade)
            for j in range(index, 6):
                books[j] = 0
            team[i][4] = books
            # 武将佩戴宝物数量
            treasures = team[i][5]
            index = self.treasure_num(quality, upgrade)
            for j in range(index, 3):
                treasures[j] = 0
            team[i][5] = treasures
        
    def check_all(self, team):
        hero_list = []
        treasure_list = []
        num_dict = {}
        for i in range(6):
            hero = team[i][0]
            hero_list.append(hero)
            horse = team[i][2]
            num_dict[horse] = num_dict[horse] - 1 if horse in num_dict.keys() else self.horse_dict[horse][0] - 1
            equips = team[i][1]
            for equip in equips:
                num_dict[equip] = num_dict[equip] - 1 if equip in num_dict.keys() else self.equip_dict[equip][0] - 1
            # 武将不能同时佩戴相同类型的兵书,同一武将兵书不能重复
            books = team[i][4]
            non_zero_books = []
            book_tags = []
            for book in books:
                if book > 0:
                    num_dict[book] = num_dict[book] - 1 if book in num_dict.keys() else self.book_dict[book][1] - 1
                    non_zero_books.append(book)
                    book_tag = self.book_dict[book][0]
                    if book_tag > 0:
                        book_tags.append(book_tag)
            if len(non_zero_books) > len(set(non_zero_books)):
                return False
            if len(book_tags) > len(set(book_tags)):
                return False
            # 宝物不能重复，宝物与武将的类型要配对
            treasures = team[i][5]
            hero_tag = self.hero_dict[hero][4]
            for treasure in treasures:
                if treasure > 0:
                    treasure_tag = self.treasure_dict[treasure][0]
                    if not treasure_tag & hero_tag:
                        return False
                    treasure_special = self.treasure_dict[treasure][1]
                    if treasure_special > 0 and treasure_special != hero:
                        return False
                    treasure_list.append(treasure)    
            
        # 6个武将不能重复
        if len(set(hero_list)) < 6:
            return False
        # 宝物不能重复
        if len(set(treasure_list)) < len(treasure_list):
            return False
        # 装备、坐骑、兵书数量不能超过限制
        for v in num_dict.values():
            if v < 0:
                return False
            
        return True
        
    def check_manual(self, pos, index):
        # 0:hero 1: horse 2: book 3: treasure
        return self.manual[pos][index] > 0
    
    def get_manual(self, pos, index):
        return self.manual[pos][index]
    
    def set_manual(self, manual):
        self.manual = manual
    
    def get_hero_list_by_pos(self, team, is_pre=True):
        if is_pre:
            return [team[0][0], team[1][0], team[2][0]]
        return [team[3][0], team[4][0], team[5][0]]
    
    def get_hero_by_pos(self, team, pos):
        return team[pos][0]
    
    def set_hero_by_pos(self, team, pos, hero):
        team[pos][0] = hero
    
    def get_equip_by_pos(self, team, pos, index):
        return team[pos][1][index]
    
    def set_equip_by_pos(self, team, pos, index, equip):
        team[pos][1][index] = equip
    
    def get_horse_by_pos(self, team, pos):
        return team[pos][2]
    
    def set_horse_by_pos(self, team, pos, horse):
        team[pos][2] = horse
    
    def get_army_by_pos(self, team, pos):
        return team[pos][3]
    
    def set_army_by_pos(self, team, pos, army):
        team[pos][3] = army
    
    def get_book_list_by_pos(self, team, pos):
        return team[pos][4]
    
    def get_book_by_pos(self, team, pos, index):
        return team[pos][4][index]
    
    def set_book_by_pos(self, team, pos, index, book):
        team[pos][4][index] = book
    
    def get_treasure_list(self, team):
        treasure_list = []
        for pos in range(6):
            treasures = team[pos][5]
            for treasure in treasures:
                if treasure > 0:
                    treasure_list.append(treasure)
        return treasure_list
    
    def get_treasure_by_pos(self, team, pos, index):
        return team[pos][5][index]
    
    def set_treasure_by_pos(self, team, pos, index, treasure):
        team[pos][5][index] = treasure
    
    def get_assign_by_pos(self, team, pos):
        return team[pos][6]
    
    def set_assign_by_pos(self, team, pos, assign):
        team[pos][6] = assign
    
    def get_junxie(self, team):
        return team[6]
    
    def set_junxie(self, team, junxie):
        team[6] = junxie
    
    def get_jinue(self, team, index):
        return team[7][index]
    
    def set_jinue(self, team, index, jinue):
        team[7][index] = jinue
    
    def get_dot(self, team):
        return team[8]
    
    def set_dot(self, team, dot):
        team[8] = dot
    
    def generate_team(self):
        # [[hero(6),head(4),cloth(4),boot(4),weapon(4),horse(5),army(4),book(6)*6,treasure(7)*3,assign(2)]*6,junxie(3),jinue(4)*2,dot(4)]
        team = []
        pre_hero_list = self.pre_hero_list.copy()
        post_hero_list = self.post_hero_list.copy()
        treasure_list = list(self.treasure_dict.keys())
        all_book_list = list(self.book_dict.keys())
        head_list = self.head_list.copy()
        cloth_list = self.cloth_list.copy()
        boot_list = self.boot_list.copy()
        weapon_list = self.weapon_list.copy()
        horse_list = self.horse_list.copy()
        num_dict = {}
        for pos in range(6):
            hero_list = pre_hero_list if pos < 3 else post_hero_list
            if self.check_manual(pos, 3):
                treasure = self.get_manual(pos, 3)
                treasure_tag = self.treasure_dict[treasure][0]
                treasure_special = self.treasure_dict[treasure][1]
                if treasure_special > 0:
                    hero = treasure_special
                else:
                    temp_hero_list = []
                    for hero in hero_list:
                        hero_tag = self.hero_dict[hero][4]
                        if treasure_tag & hero_tag:
                            temp_hero_list.append(hero)
                    hero = random.choice(temp_hero_list) if not self.check_manual(pos, 0) else self.get_manual(pos, 0)
            else:
                hero = random.choice(hero_list) if not self.check_manual(pos, 0) else self.get_manual(pos, 0)
            hero_list.remove(hero)
            head = random.choice(head_list)
            num_dict[head] = num_dict[head] - 1 if head in num_dict.keys() else self.equip_dict[head][0] - 1
            if num_dict[head] == 0:
                head_list.remove(head)
            cloth = random.choice(cloth_list)
            num_dict[cloth] = num_dict[cloth] - 1 if cloth in num_dict.keys() else self.equip_dict[cloth][0] - 1
            if num_dict[cloth] == 0:
                cloth_list.remove(cloth)
            boot = random.choice(boot_list)
            num_dict[boot] = num_dict[boot] - 1 if boot in num_dict.keys() else self.equip_dict[boot][0] - 1
            if num_dict[boot] == 0:
                boot_list.remove(boot)
            weapon = random.choice(weapon_list)
            num_dict[weapon] = num_dict[weapon] - 1 if weapon in num_dict.keys() else self.equip_dict[weapon][0] - 1
            if num_dict[weapon] == 0:
                weapon_list.remove(weapon)
            horse = random.choice(horse_list) if not self.check_manual(pos, 1) else self.get_manual(pos, 1)
            num_dict[horse] = num_dict[horse] - 1 if horse in num_dict.keys() else self.horse_dict[horse][0] - 1
            if num_dict[horse] == 0:
                horse_list.remove(horse)
            army_list = self.pre_army_list if pos < 3 else self.post_army_list
            army = random.choice(army_list)
            quality = self.hero_dict[hero][5]
            upgrade = self.hero_dict[hero][0]
            num_book = self.book_num(quality, upgrade)
            books = [0, 0, 0, 0, 0, 0]
            book_tags = []
            book_list = all_book_list.copy()
            book = random.choice(book_list) if not self.check_manual(pos, 2) else self.get_manual(pos, 2)
            book_tag = self.book_dict[book][0]
            if book_tag > 0:
                book_tags.append(book_tag)
            books[0] = book
            book_list.remove(book)
            num_dict[book] = num_dict[book] - 1 if book in num_dict.keys() else self.book_dict[book][1] - 1
            if num_dict[book] == 0:
                all_book_list.remove(book)
            for i in range(1, num_book):
                temp_book_list = []
                for book in book_list:
                    book_tag = self.book_dict[book][0]
                    if book_tag == 0 or book_tag not in book_tags:
                        temp_book_list.append(book)
                book = random.choice(temp_book_list)
                books[i] = book
                book_list.remove(book)
                num_dict[book] = num_dict[book] - 1 if book in num_dict.keys() else self.book_dict[book][1] - 1
                if num_dict[book] == 0:
                    all_book_list.remove(book)
                book_tag = self.book_dict[book][0]
                if book_tag > 0:
                    book_tags.append(book_tag)
            num_treasure = self.treasure_num(quality, upgrade)
            treasures = [0, 0, 0]
            hero_tag = self.hero_dict[hero][4]
            if self.check_manual(pos, 3): 
                treasure = self.get_manual(pos, 3)
                treasures[0] = treasure
                treasure_list.remove(treasure)
            else:
                temp_treasure_list = []
                for treasure in treasure_list:
                    treasure_tag = self.treasure_dict[treasure][0]
                    treasure_special = self.treasure_dict[treasure][1]
                    if (treasure_tag & hero_tag) and ((treasure_special > 0 and hero == treasure_special) or treasure_special == 0):
                        temp_treasure_list.append(treasure)
                treasure = random.choice(temp_treasure_list)
                treasures[0] = treasure
                treasure_list.remove(treasure)
            for i in range(1, num_treasure):
                temp_treasure_list = []
                for treasure in treasure_list:
                    treasure_tag = self.treasure_dict[treasure][0]
                    treasure_special = self.treasure_dict[treasure][1]
                    if (treasure_tag & hero_tag) and ((treasure_special > 0 and hero == treasure_special) or treasure_special == 0):
                        temp_treasure_list.append(treasure)
                treasure = random.choice(temp_treasure_list)
                treasures[i] = treasure
                treasure_list.remove(treasure)
            assign = random.randint(0, 2)  # 军师=0 上将=1  统帅=2
            team.append([hero, [head, cloth, boot, weapon], horse, army, books, treasures, assign])
        junxie = random.choice(self.junxie_list)
        team.append(junxie)
        jinue_list = random.sample(self.jinue_list, k=2)
        team.append(jinue_list)
        dot_list = list(self.dot_dict.keys())
        dot = random.choice(dot_list)
        team.append(dot)
        
        return team
            
    def web_request(self, team):
        team_dict = {}
        # 阶段 0超R 1大R+ 2大R 3中R+ 4中R 5小R 6平民
        team_dict['stage'] = self.user_type
        # 计略
        skill36 = []
        for jinue in team[7]:
            temp = {}
            temp['sid'] = jinue
            skill36.append(temp)
        team_dict['skill36'] = skill36
        # 科技
        team_dict['science'] = self.science
        # 皮肤联动
        team_dict['castleLinkage'] = self.castle
        # 军械
        team_dict['ordnance'] = {'sid': team[6]}
        # 阵法
        team_dict['dotMatrix'] = {'sid': team[8], 'level': self.dot_dict[team[8]][0], 'state': 3} # 0未激活|1阵位共鸣已激活|2阵法属性已激活|3完美激活（阵位共鸣和阵法属性都已激活）
        # 武将
        cards = []
        for pos in range(6):
            temp = {}
            temp['sid'] = team[pos][0]  # 武将
            temp['name'] = self.hero_dict[team[pos][0]][3]
            temp['pos'] = pos
            temp['breakAwaken'] = self.hero_dict[team[pos][0]][0]  # 突破
            temp['intimacy'] = self.hero_dict[team[pos][0]][1]  # 亲密度
            temp['position'] = self.hero_dict[team[pos][0]][2]  # 拜官
            temp['soldiersType'] = self.army_dict[team[pos][3]][0]
            temp['soldiersSid'] = team[pos][3]  # 兵种
            temp['soldiersLv'] = self.hero_army_dict[team[pos][0]][team[pos][3]]
            temp['appointment'] = team[pos][6]  # 任命
            temp['mountSkill'] = self.mount_skill[pos]  # 骑术
            temp['equipments'] = {'weaponSid': team[pos][1][3], 'helmetSid': team[pos][1][0], 'armourSid': team[pos][1][1], 'shoeSid': team[pos][1][2]}  # 装备
            temp['treasure'] = {'sid': team[pos][5]}  # 宝物
            temp['book'] = {'sid': team[pos][4]}  # 兵书
            temp['mount'] = {'sid': team[pos][2]}  # 坐骑
            cards.append(temp)
        team_dict['cards'] = cards
        
        score = -100
        headers = {'Content-Type': 'application/json'}
        url = self.url + '/fight'
        try:
            res = requests.post(url, headers=headers, data=json.dumps(team_dict), timeout=60)
            if res.status_code == 200:
                text = json.loads(res.text)
                if text['status'] == 200:
                    score = text['data']['intensityScore']
                else:
                    self.logger.error('fight request error! status: %d' % text['status'])
            else:
                self.logger.error('fight request error! http code: %d, http content: %s' % (res.status_code, res.text))
        except Exception as e:
            self.logger.error(e)
            self.logger.info('error team: %s' % str(team))
        
        return score
    
    def notify(self, algo):
        try:
            url = self.url + '/complete'
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                self.logger.info(f'user: {self.user_type} algorithm: {algo} search complete')
            else:
                self.logger.error(f'user: {self.user_type} algorithm: {algo} complete error! http code: {res.status_code}')
        except Exception as e:
            self.logger.error(e)