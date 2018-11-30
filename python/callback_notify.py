# -*- coding: utf-8 -*-  
  
from flask import Flask,jsonify 
from flask import request  
from flask import make_response,Response  
from multiprocessing import Value
  
import json  
 
counter = Value('i', 0)
 
app = Flask(__name__)  
 
def Response_headers(content):  
    resp = Response(content)  
    resp.headers['Access-Control-Allow-Origin'] = '*'  
    resp.headers['Content-Type'] = 'application/json'  

    return resp  

@app.route('/notify')
def notify():
    
    with counter.get_lock():
        counter.value += 1

    fobj = open('count.txt', 'w')
    fobj.write("%s" % counter.value)
    fobj.close()

    print('count:', counter.value)
    return jsonify(count=counter.value)

if __name__ == '__main__':  
    app.run(debug=True,port=18081,host="0.0.0.0") 
    #app.run(processes=8,debug=True,port=18081,host="0.0.0.0") 
