import certifi as certifi
from flask import *
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime, timedelta
import jwt
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
client = MongoClient('mongodb+srv://test:ksd3480@cluster0.sk1w9.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.dbpjt

# 홈
@app.route("/")
def home():
    return render_template('index.html')

# 후보 상세정보 보기
@app.route("/detail", methods=["GET"])
def detail():
    # request.form['target']
    target = '이재명'
    comment_list = list(db.comment.find({'target': target}))
    return render_template('detail.html', comment_list=comment_list)


# 댓글 생성
@app.route("/comment/insert", methods=["POST"])
def comment_insert():
    now = datetime.datetime.now()
    id = request.form['id']
    comment = request.form['comment']
    doc = {
        'id': id,
        'comment': comment,
        'target': '이재명',
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
    now = datetime.datetime.now()
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

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.userss.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.userss.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})



@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    email_receive = request.form['email_give']
    name_receive = request.form['name_give']
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "email": email_receive,
        "name" : name_receive,
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디

    }
    db.userss.insert_one(doc)
    return jsonify({'result': 'success'})



@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.userss.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)