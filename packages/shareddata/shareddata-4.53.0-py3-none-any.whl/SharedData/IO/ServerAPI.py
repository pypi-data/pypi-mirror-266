from flask import Flask, Response
from flask import request
from flask import jsonify
from flask_httpauth import HTTPTokenAuth
from flasgger import Swagger, swag_from

import os
import datetime
import gzip
import json

import pandas as pd
import numpy as np

from SharedData.Logger import Logger
from SharedData.SharedData import SharedData

shdata = SharedData('SharedData.IO.ServerAPI', user='master')


Logger.log.info('Starting API Server...')

app = Flask(__name__)
app.config['APP_NAME'] = 'SharedData API'
app.config['FLASK_ENV'] = 'production'
app.config['FLASK_DEBUG'] = '0'
if not 'SHAREDDATA_SECRET_KEY' in os.environ:
    raise Exception('SHAREDDATA_SECRET_KEY environment variable not set')
app.config['SECRET_KEY'] = os.environ['SHAREDDATA_SECRET_KEY']
app.config['SWAGGER'] = {
    'title': 'SharedData API',
    'uiversion': 3
}
docspath = 'ServerAPIDocs.yml'
swagger = Swagger(app, template_file=docspath)

tokens = {
    os.environ['SHAREDDATA_API_TOKEN']: "master",
}
auth = HTTPTokenAuth(scheme='Bearer')
@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]
    
@app.route('/api/table/<database>/<period>/<source>/<tablename>', methods=['GET'])
@auth.login_required
@swag_from(docspath)
def table(database, period, source, tablename):
    try:
        tablesubfolder = request.args.get('tablesubfolder')  # Optional
        startdate = request.args.get('startdate')  # Optional
        enddate = request.args.get('enddate')  # Optional
        symbols = request.args.get('symbols')  # Optional
        portfolios = request.args.get('portfolios')  # Optional
        page = request.args.get('page', default=1, type=int)
        per_page = min(request.args.get(
            'per_page', default=1000000, type=int), 1000000)

        if period == 'M1':
            if startdate is not None:
                startdate = pd.Timestamp(startdate).normalize()
                tablename = tablename + '/' + startdate.strftime('%Y%m')
        elif period == 'M15':
            if startdate is not None:
                startdate = pd.Timestamp(startdate).normalize()
                tablename = tablename + '/' + startdate.strftime('%Y')

        if tablesubfolder is not None:
            tbl = shdata.table(database, period, source, tablename+'/'+tablesubfolder)
        else:
            tbl = shdata.table(database, period, source, tablename)
        
        if startdate is not None:
            startdate = pd.Timestamp(startdate).normalize()
            dti, _ = tbl.get_date_loc(startdate)
        else:
            dti = 0

        if enddate is not None:
            enddate = pd.Timestamp(enddate).normalize()
            _, dte = tbl.get_date_loc(enddate)
        else:
            dte = tbl.count

        # Calculate start and end for slicing the DataFrame
        startpage = (page - 1) * per_page
        endpage = startpage + per_page

        loc = np.arange(dti, dte)
        if symbols is not None:
            symbols = symbols.split(',')
            symbolloc = []
            for symbol in symbols:
                symbolloc.extend(tbl.get_symbol_loc(symbol))
            symbolloc = np.array(symbolloc)
            if len(symbolloc) > 0:
                loc = np.intersect1d(loc, symbolloc)

        if portfolios is not None:
            portfolios = portfolios.split(',')
            portloc = []
            for port in portfolios:
                portloc.extend(tbl.get_portfolio_loc(port))
            portloc = np.array(portloc)
            if len(portloc) > 0:
                loc = np.intersect1d(loc, portloc)

        # Apply pagination
        df = tbl.records2df(tbl[loc[startpage:endpage]])
        pkey = df.index.names
        df = df.reset_index()
        df = df.applymap(lambda x: x.isoformat() if isinstance(x, datetime.datetime) else x)
        
        response = {
            'page': page,
            'per_page': per_page,
            'total': len(loc),
            'pkey': pkey,
            'data': df.to_dict(orient='records')
        }

        if 'gzip' in request.headers.get('Accept-Encoding', ''):            
            response_json = json.dumps(response).encode('utf-8')            
            response_compressed = gzip.compress(response_json, compresslevel=1)            
            response = Response(response_compressed, mimetype='application/json')
            response.headers['Content-Encoding'] = 'gzip'
            return response
        else:
            return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run('0.0.0.0',8000,debug=True)
