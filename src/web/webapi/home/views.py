
from fastapi import Request, Depends

from webapi.core.base import BaseRouter
from webapi.core.depends import permission_required

# dependencies 执行顺序是从左至右
router = BaseRouter(tags=['Home'], prefix='/home', dependencies=[Depends(permission_required(["admin"]))])


@router.get('')
def home(request: Request):
    return "hello world"
