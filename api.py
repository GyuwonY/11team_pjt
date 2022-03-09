import requests
import xml.etree.ElementTree as elemTree
import xmltodict, json

url = 'http://apis.data.go.kr/9760000/PofelcddInfoInqireService/getPofelcddRegistSttusInfoInqire'
params ={'serviceKey' : 'TikFg2eahcB/ceBXx88hqH3IRDFb6GEd/uli4geQ0NssuNajoYP4qOkj0kFB6fpBBK/uYammLUwzg9STKIRqbw==', 'pageNo' : '1', 'numOfRows' : '100', 'sgId' : '20220309', 'sgTypecode' : '1', 'sggName' : '', 'sdName' : ''}

response = requests.get(url, params=params)
tree = elemTree.fromstring(str(response.content, "utf-8"))
items = tree.findall('body/items/item')


api_list = []
for item in items:
    huboid = item.findtext('huboid')
    url = 'http://apis.data.go.kr/9760000/ElecPrmsInfoInqireService/getCnddtElecPrmsInfoInqire'
    params ={'serviceKey' : 'TikFg2eahcB/ceBXx88hqH3IRDFb6GEd/uli4geQ0NssuNajoYP4qOkj0kFB6fpBBK/uYammLUwzg9STKIRqbw==', 'pageNo' : '1', 'numOfRows' : '100', 'sgId' : '20220309', 'sgTypecode' : '1', 'cnddtId' : huboid}
    response = requests.get(url, params=params)

    # api response가 xml이기 때문에 dict 형태로 바꿔줌
    obj = xmltodict.parse(response.content)
    # 한글이 ascii code 처리되어 False
    api = json.dumps(obj, ensure_ascii = False)
    # json으로 load
    api_list.append(json.loads(api)['response']['body']['items'])
    # tree = elemTree.fromstring(str(response.content, "utf-8"))
    # prms = tree.find('body/items/item')
    # prms.findtext('prmsCnt')
    # prms.findtext('partyName')
    # prms.findtext('krName')

    # prms.findtext('prmsRealmName'+ str(i))
    # prms.findtext('prmsTitle'+ str(i))
    # prms.findtext('prmmCont' + str(i))


