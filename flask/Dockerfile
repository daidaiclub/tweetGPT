 # 選擇一個基礎映像。我們選擇了 Python 3 的最新版
FROM python:3.9-slim-buster

# 設定工作目錄
WORKDIR /app

# 將當前目錄的內容複製到工作目錄
COPY . /app

# 安裝所需的套件
RUN pip install --no-cache-dir -r requirements.txt

# 開放 Flask 需要的端口
EXPOSE 5000

# 啟動 Flask 應用
CMD ["python", "app.py"]
