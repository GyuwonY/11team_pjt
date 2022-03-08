import requests
import xml.etree.ElementTree as elemTree

url = 'http://apis.data.go.kr/9760000/PofelcddInfoInqireService/getPofelcddRegistSttusInfoInqire'
params ={'serviceKey' : 'TikFg2eahcB/ceBXx88hqH3IRDFb6GEd/uli4geQ0NssuNajoYP4qOkj0kFB6fpBBK/uYammLUwzg9STKIRqbw==', 'pageNo' : '1', 'numOfRows' : '100', 'sgId' : '20220309', 'sgTypecode' : '1', 'sggName' : '', 'sdName' : ''}

response = requests.get(url, params=params)
tree = elemTree.fromstring(str(response.content, "utf-8"))
items = tree.findall('body/items/item')

for item in items:
    huboid = item.findtext('huboid')
    url = 'http://apis.data.go.kr/9760000/ElecPrmsInfoInqireService/getCnddtElecPrmsInfoInqire'
    params ={'serviceKey' : 'TikFg2eahcB/ceBXx88hqH3IRDFb6GEd/uli4geQ0NssuNajoYP4qOkj0kFB6fpBBK/uYammLUwzg9STKIRqbw==', 'pageNo' : '1', 'numOfRows' : '100', 'sgId' : '20220309', 'sgTypecode' : '1', 'cnddtId' : huboid}
    response = requests.get(url, params=params)

    tree = elemTree.fromstring(str(response.content, "utf-8"))
    prms = tree.find('body/items/item')
    prmsCnt = int(prms.findtext('prmsCnt'))+1
    print(prms.findtext('num'))
    print(prms.findtext('partyName'))
    print(prms.findtext('krName'))
    for i in range(1,prmsCnt):
        print(prms.findtext('prmsRealmName'+ str(i)))
        print(prms.findtext('prmsTitle'+ str(i)))
        print(prms.findtext('prmmCont' + str(i)))