# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 12:34:09 2021

@author: Administrator
"""
from Builder import Builder
import pandas as pd
import random
from itertools import combinations
import requests
import json

'''
地下深渊阵容类，阵容规则参考 技能对撞基本规则.xlsx
'''
class dxsy_builder(Builder):
    
    def __init__(self, hero_filepath, spell_filepath, url, logger, manual, is_race=False):
        '''
        # hero_filepath: 英雄文件路径
        # spell_filepath: 技能文件路径
        # url: 战斗接口地址
        # manual：固定主将
        # is_race: 主将人类 副将非人类
        # hero_dict：人类英雄字典
        # spell_dict：技能字典
        # valid_heroes：符合规则的英雄组合列表，包含组合的特性
        # spells：技能列表的dataframe，包含必要列，扩展Skill_Effective_Parameter
        # logger: logging日志对象
        '''
        self.logger = logger
        self.hero_filepath = hero_filepath
        self.spell_filepath = spell_filepath
        self.url = url
        self.manual = manual
        self.is_race = is_race
        self.hero_dict = {}
        self.spell_dict = {}
        self.spells = None
        self.valid_heroes = []
        self.__parse()
        self.__generate_spells()
        self.__generate_heroes()

    def __parse(self):
        '''
        # 从英雄文件中解析英雄字典，人类为hero_dict，非人类为monster_dict
        # 从技能文件中解析技能字典spell_dict
        '''
        def parse_tag(tag):
            # 女性
            female = tag >> 1 & 1
            # 武力型
            berserk = tag >> 2 & 1
            # 谋略型
            mage = tag >> 3 & 1
            # 辅助型
            hunter = tag >> 4 & 1
            # 治疗型
            priest = tag >> 5 & 1
            # 均衡型
            balance = tag >> 6 & 1
            # 防御型
            warrior = tag >> 7 & 1
            # 控制型
            postposition = tag >> 8 & 1
            # 全能型
            knight = tag >> 9 & 1
            # 内政型
            craftsman = tag >> 10 & 1
            # 魅力型
            lucky = tag >> 11 & 1
            # 仙人
            clergyman = tag >> 12 & 1
            # 蛮族
            barbarian = tag >> 13 & 1
            # 黄巾军
            vampire = tag >> 14 & 1
            # 兵种型
            arms = tag >> 15 & 1
            
            return (female,berserk,mage,hunter,priest,balance,warrior,postposition,knight,craftsman,lucky,clergyman,barbarian,vampire,arms)
        
        def parse_type_study(type_study):
            # 水（骑兵）
            water = type_study >> 1 & 1
            # 火（盾兵）
            fire = type_study >> 2 & 1
            # 木（弓兵）
            wood = type_study >> 3 & 1
            # 光（枪兵）
            light = type_study >> 4 & 1
            # 暗（器械）
            dark = type_study >> 5 & 1
            
            return (water,fire,wood,light,dark)
        
        # 英雄
        hero_df = pd.read_csv(self.hero_filepath)
        for index,row in hero_df.iterrows():
            # id : ((tag),race,nature,(start_att,lvup_att),(start_def,lvup_def),(start_magic,lvup_magic),(start_speed,lvup_speed),skill)
            race = int(row['race'])
            nature = int(row['nature'])
            tag = parse_tag(int(row['tag']))
            start_att = int(row['start_att'])
            lvup_att = int(row['lvup_att'])
            start_def = int(row['start_def'])
            lvup_def = int(row['lvup_def'])
            start_magic = int(row['start_magic'])
            lvup_magic = int(row['lvup_magic'])
            start_speed = int(row['start_speed'])
            lvup_speed = int(row['lvup_speed'])
            skill = int(row['skill'])
            quality = int(row['quality'])
            self.hero_dict[int(row['id'])] = (tag,race,nature,(start_att,lvup_att),(start_def,lvup_def),(start_magic,lvup_magic),(start_speed,lvup_speed),skill,quality)
        # 技能    
        spell_df = pd.read_csv(self.spell_filepath)
        spell_df['Skill_Effective_Parameter'].fillna('', inplace=True)
        for index,row in spell_df.iterrows():
            # id: ((tag),type,studyNumb,Skill_Effective_Conditions,(Skill_Effective_Parameter))
            type_ = int(row['type'])
            studyNumb = int(row['studyNumb'])
            condition = int(row['Skill_Effective_Conditions'])
            parameter = row['Skill_Effective_Parameter']
            parameter = parameter.split('|') if parameter != '' else []
            for i in range(len(parameter)):
                parameter[i] = int(parameter[i])
            parameter = tuple(parameter)
            tag = parse_tag(int(row['tag']))
            quality = int(row['quality'])
            self.spell_dict[int(row['id'])] = (tag,type_,studyNumb,condition,parameter,quality)
    
    def __generate_spells(self):
        '''
        # id: 技能id
        # type： 技能类型
        # condition：技能出发条件
        # num: 技能学习次数
        # quality: 技能品质
        # tag: 1-纯武力 2-纯谋略 0-其它
        # 1/2/3/4/5: 扩展Skill_Effective_Parameter
        '''
        spell_list = []
        for k,v in self.spell_dict.items():
            res = {'id':k,'type':v[1],'condition':v[3],'num':v[2],'quality':v[5]}
            res['tag'] = 0
            if sum(v[0]) == 1:
                if v[0][1]:
                    # 纯武力
                    res['tag'] = 1
                elif v[0][2]:
                    # 纯谋略
                    res['tag'] = 2
            res['1'] = v[4][0] if len(v[4]) > 0 else 0
            res['2'] = v[4][1] if len(v[4]) > 0 else 0
            res['3'] = v[4][2] if len(v[4]) > 0 else 0
            res['4'] = v[4][3] if len(v[4]) > 0 else 0
            res['5'] = v[4][4] if len(v[4]) > 0 else 0
            spell_list.append(res)
        self.spells = pd.DataFrame(spell_list, columns=['id','type','condition','tag','num','quality','1','2','3','4','5'])
    
    def __generate_heroes(self):
        '''
        # 符合英雄组合规则的加入self.valid_heroes
        # arm_hero_count：兵种型英雄数量
        # diff_sex：异性标识
        # diff_race：异种族标识
        # nature_list：队伍nature组成列表
        '''
        if self.manual.count(0) == 0:
            flag,arm_hero_count,diff_sex,diff_race,nature_list = self.check_hero(self.manual)
            if not flag:
                return
            self.valid_heroes.append((self.manual,arm_hero_count,diff_sex,diff_race,nature_list))
            return
        monster_list = []
        if self.is_race:
            for k,v in self.hero_dict.items():
                if v[1] != 1:
                    monster_list.append(k)
        for hero in list(self.hero_dict.keys()):
            if (self.manual[0] > 0 and hero != self.manual[0]) or (self.is_race and self.hero_dict[hero][1] != 1):
                continue
            temp_hero_list = list(self.hero_dict.keys())
            temp_hero_list.remove(hero)
            if len(monster_list) > 0:
                temp_hero_list = monster_list
            if self.manual[1] > 0 and self.manual[2] > 0:
                hero_tup = (hero,self.manual[1],self.manual[2])
                flag,arm_hero_count,diff_sex,diff_race,nature_list = self.check_hero(hero_tup)
                if not flag:
                    continue
                self.valid_heroes.append((hero_tup,arm_hero_count,diff_sex,diff_race,nature_list))
            elif self.manual[1] > 0 or self.manual[2] > 0:
                manual_hero = self.manual[1] if self.manual[1] > 0 else self.manual[2]
                temp_hero_list.remove(manual_hero)
                for last_hero in temp_hero_list:
                    hero_tup = (hero,manual_hero,last_hero)
                    flag,arm_hero_count,diff_sex,diff_race,nature_list = self.check_hero(hero_tup)
                    if not flag:
                        continue
                    self.valid_heroes.append((hero_tup,arm_hero_count,diff_sex,diff_race,nature_list))
            else:
                hero_comb = combinations(temp_hero_list, 2)
                for temp_tup in hero_comb:
                    hero_tup = (hero,temp_tup[0],temp_tup[1])
                    flag,arm_hero_count,diff_sex,diff_race,nature_list = self.check_hero(hero_tup)
                    if not flag:
                        continue
                    self.valid_heroes.append((hero_tup,arm_hero_count,diff_sex,diff_race,nature_list))
    
    def check_hero(self, hero_tup):
        count = 0
        diff_sex = 0
        diff_race = 0
        nature_list = [0,0,0,0,0]
        hero1 = hero_tup[0]
        hero2 = hero_tup[1]
        hero3 = hero_tup[2]
        # 异性：队伍同时拥有女性和非女性 异族：队伍种三个英雄不同种族 异兵种强度：队伍种三个英雄兵种强度均不一样
        female_count = 0
        race_list = []
        #quality = hero_dict[hero1][8]
        '''
        # 2 3号位英雄的品质参照1号位英雄品质，上下浮动1
        if monster_dict[hero2][8] > quality + 1 or monster_dict[hero2][8] < quality - 1 or monster_dict[hero3][8] > quality + 1 or monster_dict[hero3][8] < quality - 1:
            return False,count,diff_sex,diff_race,nature_list
        '''
        # 英雄不能重复
        if len(set(hero_tup)) < 3:
            return False,count,diff_sex,diff_race,nature_list
        # 主将只能是人类，副将只能是非人类
        if self.is_race and (self.hero_dict[hero1][1] != 1 or self.hero_dict[hero2][1] == 1 or self.hero_dict[hero3][1] == 1):
            return False,count,diff_sex,diff_race,nature_list
        for hero in [hero1,hero2,hero3]:
            nature_list[self.hero_dict[hero][2] - 1] += 1
            if self.hero_dict[hero][0][0]:
                female_count += 1
            if self.hero_dict[hero][1] not in race_list:
                race_list.append(self.hero_dict[hero][1])
        if female_count > 0 and female_count < 3:
            diff_sex = 1
        if len(race_list) == 3:
            diff_race = 1
        # 兵种类英雄每个队伍只能出现一个
        for hero in [hero1,hero2,hero3]:
            if self.hero_dict[hero][0][14]:
                count += 1
                if count > 1:
                    return False,count,diff_sex,diff_race,nature_list
        '''
        # 队伍中三个英雄的nature必须相同
        if 3 not in nature_list:
            return False,count,diff_sex,diff_race,nature_list
        '''
        return True,count,diff_sex,diff_race,nature_list
    
    def check_spell(self, spell_tup, arm_hero_count, diff_sex, diff_race, nature_list):
        '''
        # 光环和兵种技能，每个队伍只能有一个
        # “异性”：需要队伍中拥有“女性”和非“女性”英雄同时出现时才能选择
        # “异族”：需要队伍中3个英雄需要是不同种族时才能选择
        # “属性要求”：需要队伍中3个英雄nature标签与Skill_Effective_Parameter技能要求一致
        # 技能的品质参照1号位英雄品质，上下浮动1
        '''
        light_count = 0
        for spell in spell_tup:
            '''
            if spell_dict[spell][5] > quality + 1 or spell_dict[spell][5] < quality - 1:
                return False
            '''
            if self.spell_dict[spell][1] == 5:
                light_count += 1
                if light_count > 1:
                    return False
            elif self.spell_dict[spell][1] == 6:
                arm_hero_count += 1
                if arm_hero_count > 1:
                    return False    
            if self.spell_dict[spell][3] == 1 and not diff_sex:
                return False
            elif self.spell_dict[spell][3] == 2 and not diff_race:
                return False
            elif self.spell_dict[spell][3] == 4:
                parameter = self.spell_dict[spell][4]
                for i in range(len(parameter)):
                    if nature_list[i] > parameter[i]:
                        return False 
        return True
    
    def check_all(self, team):
        for i,member in enumerate(team):
            if isinstance(member, int):
                break
            hero = member[0]
            spell_tup = member[1]
            for spell in spell_tup:
                if sum(self.spell_dict[spell][0]) == 1:
                    # 纯武力型技能不能给辅助、防御、治疗和谋略类型英雄学习
                    if self.spell_dict[spell][0][1]:
                        if self.hero_dict[hero][0][3] or self.hero_dict[hero][0][6] or self.hero_dict[hero][0][4] or self.hero_dict[hero][0][2]:
                            return False
                    # 纯谋略型技能不能防御、治疗和武力类型英雄学习
                    elif self.spell_dict[spell][0][2]:
                        if self.hero_dict[hero][0][6] or self.hero_dict[hero][0][4] or self.hero_dict[hero][0][1]:
                            return False
        return True 
    
    def get_init_spell(self, hero):
        return self.hero_dict[hero][7]
    
    def get_hero_list(self):
        return list(self.hero_dict.keys())
    
    def get_spell_by_pos(self, team, pos):
        return team[pos][1]
    
    def get_hero_by_pos(self, team, pos):
        return team[pos][0]
    
    def get_spell_num(self, spell):
        return self.spell_dict[spell][2]
    
    def get_spell_list(self):
        return list(self.spell_dict.keys())
    
    def set_hero_by_pos(self, team, pos, hero):
        team[pos][0] = hero
    
    def get_hero_tup(self, team):
        return (team[0][0],team[1][0],team[2][0])
    
    def get_spell_tup(self, team):
        return (team[0][1][0],team[0][1][1],team[1][1][0],team[1][1][1],team[2][1][0],team[2][1][1])
    
    def set_spell_by_pos(self, team, pos, spell_pos, spell):
        team[pos][1][spell_pos] = spell
    
    def check_manual(self, pos):
        return self.manual[pos] > 0
    
    def get_manual(self, pos):
        return self.manual[pos]
    
    def set_manual(self, manual):
        self.manual = manual
        self.valid_heroes = []
        self.__generate_heroes()
        
    def generate_team(self):
        hero = random.choice(self.valid_heroes)
        hero_tup = hero[0]
        arm_hero_count = hero[1]
        diff_sex = hero[2]
        diff_race = hero[3]
        nature_list = hero[4]
        hero1 = hero_tup[0]
        hero2 = hero_tup[1]
        hero3 = hero_tup[2]
        study_num = {}
        light_flag = False
        arm_flag = False
        skill1 = self.hero_dict[hero1][7]
        skill2 = self.hero_dict[hero2][7]
        skill3 = self.hero_dict[hero3][7]
        #quality = hero_dict[hero1][8]
        spells = self.spells.copy()
        if not diff_sex:
            spells = spells[spells['condition'] != 1]
        if not diff_race:
            spells = spells[spells['condition'] != 2]
        if arm_hero_count > 0:
            spells = spells[spells['type'] != 6]
        special_spell = spells[spells['condition'] == 4]
        for i in range(len(nature_list)):
            key = str(i+1)
            temp_spell = special_spell[special_spell[key] < nature_list[i]]
            spells = spells[~spells['id'].isin(temp_spell['id'])]
        
        init_spells = spells[spells['id'].isin([skill1,skill2,skill3])]
        for index,row in init_spells.iterrows():
            study_num[row['id']] = row['num'] - 1
        
        #spells = spells[(spells['quality'] >= quality - 1) & (spells['quality'] <= quality + 1)]
        
        first_spells = spells.copy()
        first_spells = first_spells[first_spells['id'] != skill1]
        if self.hero_dict[hero1][0][3] or self.hero_dict[hero1][0][6] or self.hero_dict[hero1][0][4] or self.hero_dict[hero1][0][2]:
            first_spells  = first_spells[first_spells['tag'] != 1]
        if self.hero_dict[hero1][0][6] or self.hero_dict[hero1][0][4] or self.hero_dict[hero1][0][1]:
            first_spells = first_spells[first_spells['tag'] != 2]
        del_list = []
        for k,v in study_num.items():
            if v == 0:
                del_list.append(k)
        first_spells = first_spells[~first_spells['id'].isin(del_list)]
        index_list = first_spells.index.tolist()
        spell1_index = random.choice(index_list)
        spell1 = first_spells.loc[spell1_index]
        if spell1['type'] in [5,6]:
            first_spells = first_spells[(first_spells['id'] != spell1['id']) & (first_spells['type'] != spell1['type'])]
            index_list = first_spells.index.tolist()
            light_flag = (spell1['type'] == 5)
            arm_flag = (spell1['type'] == 6)
        else:
            index_list.remove(spell1_index)
        spell2_index = random.choice(index_list)
        spell2 = first_spells.loc[spell2_index]
        light_flag = (spell2['type'] == 5) | light_flag
        arm_flag = (spell2['type'] == 6) | arm_flag
        study_num[spell1['id']] = study_num[spell1['id']] - 1 if spell1['id'] in study_num.keys() else spell1['num'] - 1
        study_num[spell2['id']] = study_num[spell2['id']] - 1 if spell2['id'] in study_num.keys() else spell2['num'] - 1
        first_combo = [hero1,[int(spell1['id']),int(spell2['id'])]]
        
        second_spells = spells.copy()
        second_spells = second_spells[second_spells['id'] != skill2]
        if self.hero_dict[hero2][0][3] or self.hero_dict[hero2][0][6] or self.hero_dict[hero2][0][4] or self.hero_dict[hero2][0][2]:
            second_spells  = second_spells[second_spells['tag'] != 1]
        if self.hero_dict[hero2][0][6] or self.hero_dict[hero2][0][4] or self.hero_dict[hero2][0][1]:
            second_spells = second_spells[second_spells['tag'] != 2]
        if light_flag:
            second_spells = second_spells[second_spells['type'] != 5]
        if arm_flag:
            second_spells = second_spells[second_spells['type'] != 6]
        del_list = []
        for k,v in study_num.items():
            if v == 0:
                del_list.append(k)
        second_spells = second_spells[~second_spells['id'].isin(del_list)]
        index_list = second_spells.index.tolist()
        spell1_index = random.choice(index_list)
        spell1 = second_spells.loc[spell1_index]
        if spell1['type'] in [5,6]:
            second_spells = second_spells[(second_spells['id'] != spell1['id']) & (second_spells['type'] != spell1['type'])]
            index_list = second_spells.index.tolist()
            light_flag = (spell1['type'] == 5)
            arm_flag = (spell1['type'] == 6)
        else:
            index_list.remove(spell1_index)
        spell2_index = random.choice(index_list)
        spell2 = second_spells.loc[spell2_index]
        light_flag = (spell2['type'] == 5) | light_flag
        arm_flag = (spell2['type'] == 6) | arm_flag
        study_num[spell1['id']] = study_num[spell1['id']] - 1 if spell1['id'] in study_num.keys() else spell1['num'] - 1
        study_num[spell2['id']] = study_num[spell2['id']] - 1 if spell2['id'] in study_num.keys() else spell2['num'] - 1
        second_combo = [hero2,[int(spell1['id']),int(spell2['id'])]]
        
        third_spells = spells.copy()
        third_spells = third_spells[third_spells['id'] != skill3]
        if self.hero_dict[hero3][0][3] or self.hero_dict[hero3][0][6] or self.hero_dict[hero3][0][4] or self.hero_dict[hero3][0][2]:
            third_spells  = third_spells[third_spells['tag'] != 1]
        if self.hero_dict[hero3][0][6] or self.hero_dict[hero3][0][4] or self.hero_dict[hero3][0][1]:
            third_spells = third_spells[third_spells['tag'] != 2]
        if light_flag:
            third_spells = third_spells[third_spells['type'] != 5]
        if arm_flag:
            third_spells = third_spells[third_spells['type'] != 6]
        del_list = []
        for k,v in study_num.items():
            if v == 0:
                del_list.append(k)
        third_spells = third_spells[~third_spells['id'].isin(del_list)]
        index_list = third_spells.index.tolist()
        spell1_index = random.choice(index_list)
        spell1 = third_spells.loc[spell1_index]
        if spell1['type'] in [5,6]:
            third_spells = third_spells[(third_spells['id'] != spell1['id']) & (third_spells['type'] != spell1['type'])]
            index_list = third_spells.index.tolist()
        else:
            index_list.remove(spell1_index)
        spell2_index = random.choice(index_list)
        spell2 = third_spells.loc[spell2_index]
        third_combo = [hero3,[int(spell1['id']),int(spell2['id'])]]
        
        team = [first_combo, second_combo, third_combo]
        return team
    
    
    def web_request(self, team):
        '''
        # 格式参考 WEB战斗测试参数.xlsx
        '''
        def fill(team, hero_dict, act_type):
            final_team = []
            for i in range(3):
                hero = team[i][0]
                spell1 = team[i][1][0]
                spell2 = team[i][1][1]
                init_spell = hero_dict[hero][7]
                attack = hero_dict[hero][3][0] + 50*hero_dict[hero][3][1]
                defence = hero_dict[hero][4][0] + 50*hero_dict[hero][4][1]
                mage = hero_dict[hero][5][0] + 50*hero_dict[hero][5][1]
                speed = hero_dict[hero][6][0] + 50*hero_dict[hero][6][1]
                arm = team[3] if len(team) > 3 else 0
                if hero_dict[hero][0][1] or hero_dict[hero][0][5]:
                    attack += 50*100
                elif hero_dict[hero][0][2] or hero_dict[hero][0][8] or hero_dict[hero][0][3] or hero_dict[hero][0][4] or hero_dict[hero][0][7]:
                    mage += 50*100
                elif hero_dict[hero][0][6]:
                    defence += 50*100
                actor = [hero,10000,[[init_spell,10],[spell1,10],[spell2,10]],[attack,defence,mage,speed],act_type,i,arm]
                final_team.append(actor)
            return final_team
        
        Testeam = fill(team, self.hero_dict, 1)
        '''
        opponents = []
        for opponent in opponent_teams:
            opponents.append(fill(opponent, hero_dict, 2))
        '''
        #print (Testeam)
        data_dict = {
                    'Testeam': (None,json.dumps(Testeam))
                    #'opponents': (None,json.dumps(opponents))
                    }
        score = -100
        try:
            res = requests.post(self.url, files=data_dict, verify=False, timeout=60)
            if res.status_code == 200:
                text = json.loads(res.text)
                score = text['result']
            else:
                self.logger.error('http code: %d, http content: %s' %(res.status_code, res.text))
        except Exception as e:
            self.logger.error(e)
            self.logger.info('error team: %s' %str(team))
        
        return score