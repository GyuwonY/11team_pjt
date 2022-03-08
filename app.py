from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://testjh:mini9150@cluster0.sk1w9.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbpjt

import requests

url = 'http://apis.data.go.kr/9760000/ElecPrmsInfoInqireService/getCnddtElecPrmsInfoInqire'
params ={'serviceKey': 'TikFg2eahcB%2FceBXx88hqH3IRDFb6GEd%2Fuli4geQ0NssuNajoYP4qOkj0kFB6fpBBK%2FuYammLUwzg9STKIRqbw%3D%3D', 'pageNo' : '1', 'numOfRows' : '10', 'sgId' : '20220309', 'sgTypecode' : '1', 'cnddtId' : '100138381' }

response = requests.get(url, params=params)
print(response.content)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/detail/<keyword>')
def detail(keyword):
    r = requests.get(f"/{keyword}", headers={"Authorization": "TikFg2eahcB%2FceBXx88hqH3IRDFb6GEd%2Fuli4geQ0NssuNajoYP4qOkj0kFB6fpBBK%2FuYammLUwzg9STKIRqbw%3D%3D"})
    result = r.json()
    print(result)
    return render_template('detail.html', word=keyword)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)