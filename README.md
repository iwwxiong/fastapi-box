# fastapi-box
FastAPI 开箱即用，包含模块管理，数据库（PostgreSQL，SQLAlchemy），Session 管理（Redis）。

## docker-compose 运行

```bash
git clone git@github.com:iwwxiong/fastapi-box.git
cd fastapi-box
sudo docker-compose up
```

启动后可以访问 http://127.0.0.1:8000/docs 查看 API 文档。

## 直接 Python 运行

依赖 Python 3.6 + 版本

```
git clone git@github.com:iwwxiong/fastapi-box.git
cd fastapi-box/src/web

# vim settings.py
# 修改 postgresql、redis 链接信息
# 然后

python wsgi.py
```

之后也可以访问 http://127.0.0.1:8000/docs 查看 API 文档。
