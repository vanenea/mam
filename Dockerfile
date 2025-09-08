# 使用轻量级 Python 镜像
FROM python:3.11-slim

# copy directory
RUN mkdir /app
# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt ./

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

RUN chmod 777 /app/finance.db

RUN chown -R user:user /app

# Flask 默认监听 5000 端口
EXPOSE 5000

# 启动服务
CMD ["python", "main.py"]