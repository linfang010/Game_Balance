#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 09:33:50 2019

@author: lilnfang
"""
from flask import Flask, request
import logging
from Util import util_balance
from sgz_builder import sgz_builder
from genetic_sgz import GA_sgz
from tabu_search_sgz import TS_sgz
from multiprocessing import Process
import json
from deap import creator, base
from KeyValueDB import KeyValueDB
from pathlib import Path
#import gc


app = Flask("game balance")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger()
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)
    

@app.after_request
def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,session_id"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS,HEAD"
    )
    # 这里不能使用add方法，否则会出现 The 'Access-Control-Allow-Origin' header contains multiple values 的问题
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.route("/sgz_search_ga", methods=["POST"])
def sgz_search_ga():
    res = {'result': 'ok'}
    form = request.form
    logger.info(f'parameter: {form}')
    manual = ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0))
    indpb = 0.05
    tournsize = 3
    threshold = 0
    CXPB = 0.5
    MUTPB = 0.2
    max_gen = 10
    n_pop = 100
    user_type = 0
    mode = 0
    if "mode" in form.keys():
        mode = int(form['mode'])
    if "user_type" in form.keys():
        user_type = int(form['user_type'])
    if "manual" in form.keys():
        manual = eval(form['manual'])
    if "max_gen" in form.keys():
        max_gen = int(form['max_gen'])
    if "n_pop" in form.keys():
        n_pop = int(form['n_pop'])
    process_dict = app.extensions['process_dict']
    process = process_dict.get('ga'+str(user_type), None)
    if process is not None and process.is_alive():
        res['result'] = 'busy'
        return json.dumps(res)
    ub = app.extensions["ub"]
    result_path = Path(ub.config['result'])
    file_path = result_path / ('result_ga_'+str(user_type)+'.dat')
    db = KeyValueDB(file_path)
    gen = db.get_value('gen') 
    if (gen is None or gen == 0) and mode == 1:
        res['result'] = 'read state error'
        return json.dumps(res)
    
    builder = sgz_builder(ub.config['hero_file'], ub.config['equip_file'], ub.config['horse_file'], ub.config['army_file'],
                          ub.config['book_file'], ub.config['treasure_file'], ub.config['junxie_file'], ub.config['jinue_file'],
                          ub.config['qishu_file'], ub.config['keji_file'], ub.config['castle_file'], ub.config['dot_file'], ub.config['hero_army_file'],
                          ub.config['ga_url'], logger, manual, user_type)
    strategy = GA_sgz(max_gen, n_pop, CXPB, MUTPB, builder, indpb, tournsize, threshold, mode, db)
    process = Process(target=strategy.execute, args=(int(ub.config['process']),))
    process.start()
    process_dict['ga'+str(user_type)] = process
    
    return json.dumps(res)


@app.route("/sgz_search_tabu", methods=["POST"])
def sgz_search_tabu():
    res = {'result': 'ok'}
    form = request.form
    logger.info(f'parameter: {form}')
    manual = ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0))
    threshold = 0
    max_gen = 5
    length = 5
    team = []
    user_type = 0
    mode = 0
    if "mode" in form.keys():
        mode = int(form['mode'])
    if "user_type" in form.keys():
        user_type = int(form['user_type'])
    if "manual" in form.keys():
        manual = eval(form['manual'])
    if "max_gen" in form.keys():
        max_gen = int(form['max_gen'])
    if "length" in form.keys():
        length = int(form['length'])
    if "team" in form.keys():
        team = eval(form['team'])
    process_dict = app.extensions['process_dict']
    process = process_dict.get('tabu'+str(user_type), None)
    if process is not None and process.is_alive():
        res['result'] = 'busy'
        return json.dumps(res)
    ub = app.extensions["ub"]
    result_path = Path(ub.config['result'])
    file_path = result_path / ('result_tabu_'+str(user_type)+'.dat')
    db = KeyValueDB(file_path)
    gen = db.get_value('gen') 
    if (gen is None or gen == 0) and mode == 1:
        res['result'] = 'read state error'
        return json.dumps(res)

    builder = sgz_builder(ub.config['hero_file'], ub.config['equip_file'], ub.config['horse_file'], ub.config['army_file'],
                          ub.config['book_file'], ub.config['treasure_file'], ub.config['junxie_file'], ub.config['jinue_file'],
                          ub.config['qishu_file'], ub.config['keji_file'], ub.config['castle_file'], ub.config['dot_file'], ub.config['hero_army_file'],
                          ub.config['tabu_url'], logger, manual, user_type)
    strategy = TS_sgz(max_gen, length, builder, team, threshold, mode, db)
    process = Process(target=strategy.execute, args=(int(ub.config['process']),))
    process.start()
    process_dict['tabu'+str(user_type)] = process

    return json.dumps(res)


@app.route("/terminate", methods=["POST"])
def task_terminate():
    res = {'result': 'ok'}
    form = request.form
    logger.info(f'parameter: {form}')
    algorithm = 'ga'
    user_type = 0
    if 'algorithm' in form.keys():
        algorithm = form['algorithm']
    if 'user_type' in form.keys():
        user_type = int(form['user_type'])
    process_dict = app.extensions['process_dict']
    process = process_dict.get(algorithm+str(user_type), None)
    if process is not None and process.is_alive():
        logger.info(f'terminate pid {process.pid}')
        process.terminate()
        del process_dict[algorithm+str(user_type)]
    else:
        res['result'] = 'empty'
    #gc.collect()
    return json.dumps(res)


@app.route("/progress", methods=["POST"])
def progress_query():
    res = {'result': 'ok'}
    form = request.form
    logger.info(f'parameter: {form}')
    algorithm = 'ga'
    user_type = 0
    if 'algorithm' in form.keys():
        algorithm = form['algorithm']
    if 'user_type' in form.keys():
        user_type = int(form['user_type'])
    ub = app.extensions["ub"]
    result_path = Path(ub.config['result'])
    file_path = result_path / ('result_'+algorithm+'_'+str(user_type)+'.dat')
    db = KeyValueDB(file_path)
    total = db.get_value('max_gen')
    now = db.get_value('gen')
    if total is None or now is None:
        res['result'] = 'read state error'
        return json.dumps(res)
    res['total'] = total
    res['now'] = now
    return json.dumps(res)

    
if __name__ == "__main__":

    ub = util_balance(logger, 'config.xml')
    if not hasattr(app, "extensions"):
        app.extensions = {}
    app.extensions["ub"] = ub
    app.extensions['process_dict'] = {}
    app.run(host="0.0.0.0", port=int(ub.config["http_port"]))
