import uvicorn
import logging

from settings import settings
from webapi.app import create_app

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.getLevelName(settings.logger_level),
    format=settings.logger_formatter
)

app = create_app(init_tables=True)


if __name__ == '__main__':
    uvicorn.run('asgi:app', host='0.0.0.0', port=8000, reload=True, debug=True, lifespan="on")
