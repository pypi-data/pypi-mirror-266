import requests
import os
import pandas as pd

host = 'localhost'
port = 8000
apiurl = f"http://{host}:{port}"

def get_table(database, period, source, tablename, 
    tablesubfolder=None, startdate=None, enddate=None, 
    symbols=None, portfolios=None, page=None, per_page=None):    

    url = apiurl+"/api/table/{database}/{period}/{source}/{tablename}"

    headers = {
        "Authorization": "Bearer "+os.environ['SHAREDDATA_API_TOKEN'],
        "Accept-Encoding": "gzip",
    }

    params = {
        'tablesubfolder': tablesubfolder,
        'startdate': startdate,
        'enddate': enddate,  
        'symbols': symbols,
        'portfolios': portfolios,  
        'page': page,
        'per_page': per_page
    }

    urlformat = url.format(database=database, period=period, source=source, tablename=tablename)
    response = requests.get(urlformat, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    js = response.json()
    df = pd.DataFrame(js['data']).set_index(js['pkey'])    
    return df.sort_index()

database = "MarketData"
period = "D1"
source = "VOTER"
tablename = "QUOTES"
tablesubfolder = "202401"
startdate = "2024-01-10"
enddate = "2024-01-10"
df = get_table(database, period, source, tablename, 
    tablesubfolder=tablesubfolder, 
    startdate=startdate,
    enddate=enddate
)

idx = ['ES_' == x[:3] for x in df.index.get_level_values('symbol')]
df[idx]

