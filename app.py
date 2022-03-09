from flask import *
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import jwt
import hashlib
import requests
import xmltodict, json

SECRET_KEY = 'SPARTA'
client = MongoClient('mongodb+srv://test01:test01@cluster0.sk1w9.mongodb.net/Cluster0?retryWrites=true&w=majority',tlsCAFile=certifi.where())
db = client.dbpjt

SECRET_KEY = 'SPARTA'

# 홈
@app.route("/")
def home():
    candidates = list(db.candidate.find({}, {'_id': False}))
    # 로그인 상태인 경우 회원 정보와 함께 response
    if request.cookies.get('token') is not None:
        try:
            token = request.cookies.get('token')
            member = jwt.decode(token, SECRET_KEY, algorithms='HS256')
            return render_template('index.html', candidates=candidates, member=member)
        except jwt.ExpiredSignatureError:
            resp = make_response(redirect(url_for('home')))
            resp.delete_cookie('token')
            return resp
        except jwt.exceptions.DecodeError:
            resp = make_response(redirect(url_for('home')))
            resp.delete_cookie('token')
            return resp
    return render_template('index.html', candidates=candidates)

# 후보 상세정보 보기
@app.route("/detail", methods=["GET"])
def detail():
    target = request.args.get('name')
    id = request.args.get('id')
    comment_list = list(db.comment.find({'target': target}))

    url = 'http://apis.data.go.kr/9760000/ElecPrmsInfoInqireService/getCnddtElecPrmsInfoInqire'
    params = {'serviceKey': 'TikFg2eahcB/ceBXx88hqH3IRDFb6GEd/uli4geQ0NssuNajoYP4qOkj0kFB6fpBBK/uYammLUwzg9STKIRqbw==',
              'pageNo': '1', 'numOfRows': '100', 'sgId': '20220309', 'sgTypecode': '1', 'cnddtId': id}
    response = requests.get(url, params=params)

    # api response가 xml이기 때문에 dict 형태로 바꿔줌
    obj = xmltodict.parse(response.content)
    # 한글이 ascii code 처리되어 False
    api = json.dumps(obj, ensure_ascii=False)
    # json으로 load
    promise = json.loads(api)['response']['body']['items']['item']
    prmscnt = []
    for i in range(1, int(promise['prmsCnt'])+1):
        prmscnt.append(str(i))
    if request.cookies.get('token') is not None:
        try:
            token = request.cookies.get('token')
            member = jwt.decode(token, SECRET_KEY, algorithms='HS256')
            return render_template('detail.html', comment_list=comment_list, promise=promise, prmscnt=prmscnt, member=member)
        except jwt.ExpiredSignatureError:
            resp = make_response(redirect(url_for('home')))
            resp.delete_cookie('token')
            return resp
        except jwt.exceptions.DecodeError:
            resp = make_response(redirect(url_for('home')))
            resp.delete_cookie('token')

    return render_template('detail.html', comment_list=comment_list, promise=promise, prmscnt=prmscnt)


# 댓글 생성
@app.route("/comment/insert", methods=["POST"])
def comment_insert():
    now = datetime.now()
    id = request.form['id']
    comment = request.form['comment']
    target = request.form['target']
    doc = {
        'id': id,
        'comment': comment,
        'target': target,
        'reg_date': now.strftime('%Y-%m-%d'),
        'reg_time': now.strftime('%H:%M:%S'),
    }

    db.comment.insert_one(doc)
    return jsonify({'msg': '댓글이 등록되었습니다!'})

# 댓글 수정
@app.route("/comment/update", methods=["PUT"])
def comment_update():
    objid = request.form['objid']
    comment = request.form['comment']
    db.comment.update_one({'_id': ObjectId(objid)}, {'$set': {'comment': comment}})
    return jsonify({'msg': '댓글이 수정되었습니다!'})

# 댓글 삭제
@app.route("/comment/delete", methods=["DELETE"])
def comment_delete():
    objid = request.form['objid']
    db.comment.delete_one({"_id": ObjectId(objid)})
    return jsonify({'msg': '댓글이 삭제되었습니다!'})

# 답글 생성
@app.route("/recomment/insert", methods=["POST"])
def recomment():
    now = datetime.now()
    id = request.form['id']
    objid = request.form['objid']
    recomment = request.form['recomment']
    re_id = ObjectId()
    db.comment.update_one({'_id': ObjectId(objid)},
                          {'$push':
                              {'recomments':
                                  {
                                      '_id': re_id,
                                      'target': objid,
                                      'id': id,
                                      'recomment': recomment,
                                      'reg_date': now.strftime('%Y-%m-%d'),
                                      'reg_time': now.strftime('%H:%M:%S')
                                  }
                              }
                          })
    return jsonify({'msg': '답글이 등록되었습니다!'})

# 답글 삭제
@app.route("/recomment/delete", methods=["DELETE"])
def recomment_delete():
    objid = request.form['objid']
    target = request.form['target']
    db.comment.update_one({'_id': ObjectId(target)},
                          {'$pull':
                              {'recomments':
                                   {
                                        "_id":ObjectId(objid)
                                   }
                              }
                          })
    return jsonify({'msg': '답글이 삭제되었습니다!'})

# 답글 수정
@app.route("/recomment/update", methods=["PUT"])
def recomment_update():
    objid = request.form['objid']
    recomment = request.form['comment']
    target = request.form['target']
    db.comment.update_one({'recomments._id': ObjectId(objid)},
                          {'$set':
                               {'recomments.$.recomment':recomment}
                          })
    return jsonify({'msg': '댓글이 수정되었습니다!'})

# 로그인
@app.route("/signin", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']

        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

        result = db.member.find_one({'id': id, 'password': pw_hash})

        if result is not None:
            payload = {
                'id': result['id'],
                'name': result['name'],
                'exp': datetime.utcnow() + timedelta(hours=1)
            }

            token = jwt.encode(payload, SECRET_KEY, algorithm = 'HS256')

            resp = make_response(redirect(url_for('home')) )
            resp.set_cookie('token', token)
            return resp
        else:
            return render_template('login_resist_form.html', msg='아이디 또는 비밀번호가 일치하지 않습니다.')
    else:
        return render_template('login_resist_form.html')

#로그아웃
@app.route("/logout", methods=["GET"])
def logout():
    #쿠키 삭제
    resp = make_response(redirect(url_for('home')))
    resp.delete_cookie('token')
    return resp

# 회원가입
@app.route('/signup', methods=["POST"])
def sign_up():
    id = request.form['id']
    password = request.form['pw']
    pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    name = request.form['name']
    doc={
        'id':id,
        'password':pw_hash,
        'name':name
    }
    db.member.insert_one(doc)
    return render_template('login_resist_form.html')

# 중복 확인
@app.route('/duplicheck', methods=["POST"])
def duplication_check():
    id = request.form['id']
    if db.member.find_one({'ID':id}) is None:
        return jsonify({'msg' : "사용 가능한 아이디입니다.", 'result' : 1})
    else:
        return jsonify({'msg' : "중복된 아이디가 존재합니다.", 'result' : 0})

# 관리자페이지
@app.route('/adminpage', methods=["GET"])
def adminpage():
    report_list = list(db.reports.find({}))
    try:
        token = request.cookies.get('token')
        member = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        return render_template('adminpage.html', report_list=report_list, member=member)
    except jwt.ExpiredSignatureError:
        resp = make_response(redirect(url_for('home')))
        resp.delete_cookie('token')
        return resp
    except jwt.exceptions.DecodeError:
        resp = make_response(redirect(url_for('home')))
        resp.delete_cookie('token')

    return render_template('adminpage.html', report_list=report_list, member=member)

# 댓글 신고 등록
@app.route('/report/comment', methods=["POST"])
def reportcomment():
    msg = ''
    ojtid = request.form['ojtid']

    if db.reports.find_one({'comment_id': ObjectId(ojtid)}) != None:
        msg = '이미 신고되어 처리 대기 중인 댓글입니다.'
    else:
        comment = db.comment.find_one({'_id': ObjectId(ojtid)}, {'recomments': False})
        doc={
            'comment_id': comment['_id'],
            'id': comment['id'],
            'comment': comment['comment'],
            'reg_date': comment['reg_date'],
            'reg_time': comment['reg_time'],
            'distinct': 0
        }
        db.reports.insert_one(doc)
        msg = '댓글 신고가 완료되었습니다.'

    return jsonify({'msg': msg})

#답글 신고 등록
@app.route('/report/recomment', methods=["POST"])
def reportrecomment():
    msg = ''
    ojtid = request.form['ojtid']
    target = request.form['target']
    if db.reports.find_one({'recomment_id': ObjectId(ojtid)}) != None:
        msg = '이미 신고되어 처리 대기 중인 답글입니다.'
    else:
        recomment = db.comment.find_one({}, {'recomments': { "$elemMatch": {"_id": ObjectId(ojtid)}}, 'name':1})
        doc={
            'recomment_id': recomment['recomments'][0]['_id'],
            'id': recomment['recomments'][0]['id'],
            'recomment': recomment['recomments'][0]['recomment'],
            'reg_date': recomment['recomments'][0]['reg_date'],
            'reg_time': recomment['recomments'][0]['reg_time'],
            'target': recomment['recomments'][0]['target'],
            'distinct': 1
        }
        db.reports.insert_one(doc)
        msg = '답글 신고가 완료되었습니다.'

    return jsonify({'msg': msg})

#댓글 신고내용 삭제
@app.route('/report/comment', methods=["DELETE"])
def delete_report_comment():
    msg = ''
    ojtid = request.form['ojtid']
    comment_id = request.form['comment_id']

    if db.comment.find_one({'_id': ObjectId(comment_id)}) == None:
        db.reports.delete_one({'_id': ObjectId(ojtid)})
        msg = '이미 삭제된 댓글입니다.'
    else:
        db.comment.delete_one({"_id": ObjectId(comment_id)})
        db.reports.delete_one({'_id': ObjectId(ojtid)})
        msg = '댓글 삭제가 완료되었습니다.'
    return jsonify({'msg': msg})

#답글 신고내용 삭제
@app.route('/report/recomment', methods=["DELETE"])
def delete_report_recomment():
    msg = ''
    ojtid = request.form['ojtid']
    recomment_id = request.form['recomment_id']
    target = request.form['target']

    if db.comment.find_one({'recomments._id': ObjectId(recomment_id)}) == None:
        db.reports.delete_one({'_id': ObjectId(ojtid)})
        msg = '이미 삭제된 답글입니다.'
    else:
        db.reports.delete_one({'_id': ObjectId(ojtid)})

        db.comment.update_one({'_id': ObjectId(target)},
                              {'$pull':
                                  {'recomments':
                                      {
                                          "_id": ObjectId(recomment_id)
                                      }
                                  }
                              })
        msg = '답글 삭제가 완료되었습니다.'
    return jsonify({'msg': msg})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)