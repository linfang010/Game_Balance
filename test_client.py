# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 17:03:50 2022

@author: admin
"""

import requests


def sgz_ga_test():
    data = {'max_gen':(None, 100),
            'n_pop':(None, 10000),
            'mode':(None, 0)}
    
    url = 'http://192.168.5.135:8080/sgz_search_ga'
    res = requests.post(url, files=data, timeout=60)
    print (res.text)
    

def sgz_tabu_test():
    team = "[[10436, [20016, 20221, 20418, 20620], 22321, 103012, [105511, 105311, 105518, 105517, 105601, 0], [12241, 0, 0], 1], [10234, [20010, 20208, 20407, 20609], 22303, 103005, [105519, 105511, 105406, 105509, 105601, 0], [12367, 0, 0], 2], [10007, [20017, 20220, 20407, 20621], 22321, 103005, [105410, 105405, 105511, 105601, 105519, 105506], [12243, 12217, 12105], 2], [10044, [20015, 20213, 20406, 20620], 22321, 103009, [105517, 105518, 105320, 105511, 105302, 0], [12415, 0, 0], 2], [10403, [20017, 20213, 20419, 20610], 22317, 103008, [105511, 105318, 105411, 105601, 105520, 0], [12202, 12225, 0], 1], [10653, [20017, 20207, 20419, 20614], 22303, 103008, [105506, 105301, 105408, 105511, 105310, 0], [12369, 12414, 0], 1], 23501, [26701, 26901], 10090211]"
    data = {'max_gen':(None,100),
            'length':(None,50),
            'mode':(None,0),
            'team': (None, team)}
    
    url = 'http://192.168.5.135:8080/sgz_search_tabu'
    res = requests.post(url, files=data, timeout=60)
    print (res.text)


def terminate_test():
    data = {'algorithm':(None,'ga')}
    url = 'http://192.168.5.135:8080/terminate'
    res = requests.post(url, files=data, timeout=60)
    print (res.text)


def progress_test():
    data = {'algorithm':(None,'tabu')}
    url = 'http://192.168.5.135:8080/progress'
    res = requests.post(url, files=data, timeout=60)
    print (res.text)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

if __name__ == '__main__':
    #sgz_ga_test()
    #sgz_tabu_test()
    terminate_test()
    #progress_test()
    