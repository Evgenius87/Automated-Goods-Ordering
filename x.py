import typing
import uvicorn

from fastapi import FastAPI
from starlette.responses import RedirectResponse, JSONResponse, Response

from src.conf.config import settings

app = FastAPI()

url = "https://andrijdudar.github.io/lazy-barmen"

@app.get('/')
async def root():
    return JSONResponse({"message": "hallo"})

@app.get('/ukr')
async def urk():
    response = Response()
    response.set_cookie("token", "xxxx")
    tokens = {"access_token": "XXXXXXXXXXXXXXXXXXXXXX",
              "refresh-token": "YYYYYYYYYYYYYYYYYYYYY",
              "token_type": "bearer"}
    return RedirectResponse(url=settings.home_page, headers=tokens)


if __name__ == "__main__":
    uvicorn.run("x:app", host="127.0.0.1", port=8080)