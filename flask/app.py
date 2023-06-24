from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from rq import Queue
from rq.job import Job
from worker import conn

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/lib/sqlite/test.db'  # 將這個路徑改為你的 sqlite3 資料庫的路徑
db = SQLAlchemy(app)

q = Queue(connection=conn)
jobs = []

# 創建一個數據模型，用來儲存 GPT 分析完的數據
class Result(db.Model):
  channel_id = db.Column(db.Integer(), primary_key=True)
  result = db.Column(db.String(1200), nullable=False)

def get_tweets(brand, channel_id):
  # TODO: 使用品牌名稱調用 Twitter API 獲取 tweet 數據
  # 儲存或處理數據的邏輯實現，在這裡寫好 prompt
  return {'prompt': '這是一個 prompt', 'channel_id': channel_id}

@app.route('/brand', methods=['POST'])
def brand():
  # 保存channel_id 和 品牌名稱到資料庫
  data = request.get_json()

  # 使用品牌名稱調用 Twitter API 獲取 tweet 數據，並將它加入工作佇列
  job = q.enqueue(get_tweets, data['brand'], data['channel_id'])
  jobs.append(job.get_id())
  
  return {'job_id': job.get_id()}, 202

@app.route('/queue', methods=['GET'])
def queue():
  # 獲取工作佇列的內容
  results = []
  for job_id in jobs:
    job = Job.fetch(job_id, connection=conn)
    if job.is_finished:
      jobs.remove(job_id)
      results.append(job.result)

  return jsonify(results)

@app.route('/gpt', methods=['POST'])
def gpt():
  # 紀錄 GPT 分析完的數據
  data = request.get_json()
  result = Result(channel_id=data['channel_id'], result=data['result'])
  
  # 如果資料庫中已經有這個 channel_id 的數據，就更新它
  existing_result = Result.query.filter_by(channel_id=data['channel_id']).first()
  if existing_result:
    existing_result.result = data['result']
  # 否則就新增一筆數據
  else:
    db.session.add(result)
  db.session.commit()

  return {'message': 'Data saved successfully'}, 200

@app.route('/results', methods=['GET'])
def results():
  # 獲取 GPT 分析完的數據
  results = Result.query.all()
  data = [{'channel_id': result.channel_id, 'result': result.result} for result in results]

  # TODO: 清空資料庫
  for result in results:
    db.session.delete(result)

  db.session.commit()

  return jsonify(data)

# 創建資料庫
with app.app_context():
  db.create_all()

if __name__ == '__main__':
  db.create_all()
  app.run(debug=True)

