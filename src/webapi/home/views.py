
from fastapi import Request, Depends

from webapi.core.base import BaseRouter
from webapi.core.depends import login_required

router = BaseRouter(tags=['Home'], prefix='/home', dependencies=[Depends(login_required)])


@router.get('')
def home(request: Request):
    return "hello world"
