from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from rq import Queue
from rq.job import Job
from worker import conn
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'  # 將這個路徑改為你的 sqlite3 資料庫的路徑
db = SQLAlchemy(app)

q = Queue(connection=conn)

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
  job = q.enqueue_call(
    func=get_tweets, args=(data['brand'], data['channel_id']), result_ttl=5000
  )
  
  return {'job_id': job.get_id()}, 202

@app.route('/queue', methods=['GET'])
def queue():
  # 獲取工作佇列的內容
  jobs = q.get_jobs()
  results = [Job.fetch(job.get_id(), connection=conn).result for job in jobs]
  
  # 清空佇列
  for job in jobs:
    job.delete()
  
  return jsonify(results)

@app.route('/gpt', methods=['POST'])
def gpt():
  # 紀錄 GPT 分析完的數據
  data = request.get_json()
  result = Result(channel_id=data['channel_id'], result=data['result'])
  db.session.add(result)
  db.session.commit()

  return {'message': 'Data saved successfully'}, 200

@app.route('/results', methods=['GET'])
def results():
  # 獲取 GPT 分析完的數據
  results = Result.query.all()
  data = [{'channel_id': result.channel_id, 'result': result.result} for result in results]

  # 清空資料庫
  for result in results:
    db.session.delete(result)
  return jsonify(data)

if __name__ == '__main__':
  db.create_all()
  app.run(debug=True)
