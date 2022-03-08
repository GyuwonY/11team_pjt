from flask import *
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)
client = MongoClient('mongodb+srv://test:ksd3480@cluster0.sk1w9.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.dbpjt

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
                               {'recomments.recomment':recomment}
                          })
    return jsonify({'msg': '댓글이 수정되었습니다!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)