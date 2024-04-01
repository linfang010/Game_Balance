#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 09:33:50 2019

@author: lilnfang
"""
from flask import Flask
import logging
from Util import util_balance
import json
import requests


app = Flask("game balance notify")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger()


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


@app.route("/sgz_search_notify", methods=["GET"])
def sgz_search_notify():
    ub = app.extensions["ub"]
    app.extensions["count"] += 1
    result = {'result': 'ok'}
    if app.extensions["count"] == 1:
        url = ub.config['url'] + '/complete'
        try:
            res = requests.get(url, timeout=10)
            logger.info(f'sgz search compelete: http_code {res.status_code} http_content {res.text}')
        except Exception as e:
            logger.error(e)
            logger.info('sgz search complete error!')
        app.extensions["count"] = 0
    return json.dumps(result)
    

if __name__ == "__main__":
    
    ub = util_balance(logger, 'config.xml')
    if not hasattr(app, "extensions"):
        app.extensions = {}
    app.extensions["count"] = 0
    app.extensions["ub"] = ub
    app.run(host="127.0.0.1", port=int(ub.config["notify_port"]))
