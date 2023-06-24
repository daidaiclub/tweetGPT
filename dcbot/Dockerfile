# 使用 Python 3.8 做為基礎映像
FROM python:3.8-slim-buster

# 安裝所需的套件
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt