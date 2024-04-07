from fastapi import FastAPI, Request, Response
from fastapi.exceptions import HTTPException

def http_error(code:int, detail:str=''):
    raise HTTPException(code, detail)

def configure_cors(api:FastAPI) -> FastAPI:
    async def inner(request:Request, call_next):
        response:Response = Response() if request.method == "OPTIONS" else await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = '*'
        response.headers["Access-Control-Allow-Methods"] = 'GET, POST, OPTIONS, PUT, DELETE, PATCH'
        response.headers["Access-Control-Allow-Headers"] = '*'
        return response
    api.middleware("http")(inner)
    return api