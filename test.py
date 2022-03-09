from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
import xml.etree.ElementTree as elemTree
import xmltodict, json

client = MongoClient('mongodb+srv://test:ksd3480@cluster0.sk1w9.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.dbpjt

# url = 'http://apis.data.go.kr/9760000/PofelcddInfoInqireService/getPofelcddRegistSttusInfoInqire'
# params ={'serviceKey' : 'TikFg2eahcB/ceBXx88hqH3IRDFb6GEd/uli4geQ0NssuNajoYP4qOkj0kFB6fpBBK/uYammLUwzg9STKIRqbw==', 'pageNo' : '1', 'numOfRows' : '100', 'sgId' : '20220309', 'sgTypecode' : '1', 'sggName' : '', 'sdName' : ''}
# response = requests.get(url, params=params)
#
# obj = xmltodict.parse(response.content)
# api = json.loads(json.dumps(obj, ensure_ascii = False))['response']['body']['items']
#
# for i in range(len(api['item'])):
#     db.candidate.insert_one(api['item'][i])

candidates = list(db.candidate.find({}))

for candidate in candidates:

    huboid = candidate['huboid']

    url = 'http://apis.data.go.kr/9760000/ElecPrmsInfoInqireService/getCnddtElecPrmsInfoInqire'
    params = {'serviceKey': 'TikFg2eahcB/ceBXx88hqH3IRDFb6GEd/uli4geQ0NssuNajoYP4qOkj0kFB6fpBBK/uYammLUwzg9STKIRqbw==',
              'pageNo': '1', 'numOfRows': '100', 'sgId': '20220309', 'sgTypecode': '1', 'cnddtId': huboid}
    response = requests.get(url, params=params)

    obj = xmltodict.parse(response.content)
    api = json.loads(json.dumps(obj, ensure_ascii = False))['response']['body']['items']
    prms_cnt = api['item']['prmsCnt']

    for i in range(1, prms_cnt+1):
        prmsRealmName = 'prmsRealmName'+str(i)
