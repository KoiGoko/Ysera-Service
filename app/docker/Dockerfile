# 使用基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 复制应用程序文件到容器中
COPY . /app

# 安装应用程序的依赖项
RUN pip install -r requirements.txt

# 暴露应用程序的端口
EXPOSE 8000

# 启动应用程序
CMD ["python", "app.py"]