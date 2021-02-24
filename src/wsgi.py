import uvicorn

from webapi.app import create_app

app = create_app()


if __name__ == '__main__':
    uvicorn.run('wsgi:app', host='0.0.0.0', port=8000, reload=True, debug=True)
