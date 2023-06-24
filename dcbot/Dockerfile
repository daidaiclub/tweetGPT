# 使用 Python 3.9 做為基礎映像
FROM python:3.9-slim-buster

# 設定工作目錄
WORKDIR /app

# 將當前目錄的內容複製到工作目錄
COPY . /app

# 安裝所需的套件
RUN pip install --no-cache-dir -r requirements.txt

# 啟動 Discord bot
CMD ["python", "app.py"]
