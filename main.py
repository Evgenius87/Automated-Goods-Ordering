import uvicorn
import os
import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status, Header
from fastapi.responses import HTMLResponse
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from httpx import AsyncClient
from pyngrok import ngrok

from src.conf.config import settings
from src.routes import (bot_actions,  
                        dishes, 
                        categories, 
                        users, 
                        tags, 
                        ingredients,
                        premixes, 
                        comments,
                        providers, 
                        stop_list,
                        auth)



load_dotenv()
TG_API_KEY_FOR_USERS = os.getenv("BOT_TOKEN")
TG_API_KEY_FOR_PROVIDERS = os.getenv("BOT_TOKEN_PRO")

app = FastAPI()
# header = Header({"ngrok-skip-browser-warning": True})

origins = ["http://172.25.8.7:3000/React-cocktails",
            "http://localhost:3000/React-cocktails",
            "https://andrijdudar.github.io/React-cocktails/", 
            "http://localhost:3000", 
            "http://localhost:3000/React-cocktails", 
            "http://localhost:8000", 
            "https://fb64-46-119-118-70.ngrok.io/api/grids/",
            "https://andrijdudar.github.io/React-cocktails/",
            "https://andrijdudar.github.io",
            "https://194.44.160.206:0",
            "http://172.25.9.70:3000/lazy-barmen",
            "https://andrijdudar.github.io/lazy-barmen/#/login",
            "https://andrijdudar.github.io/lazy-barmen",
            "https://andrijdudar.github.io/lazy-barmen/#",
            "https://andrijdudar.github.io/lazy-barmen/#/login/",
            "https://andrijdudar.github.io/lazy-barmen/",
            "https://andrijdudar.github.io/lazy-barmen/#/",
           ] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.api_secret_key)



app.include_router(bot_actions.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(dishes.router, prefix='/api')
app.include_router(ingredients.router, prefix="/api")
app.include_router(premixes.router, prefix="/api")
app.include_router(categories.router, prefix='/api')
app.include_router(tags.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(providers.router, prefix="/api")
app.include_router(stop_list.router, prefix="/api")



TELEGRAM_SET_WEBHOOK_URL = f"https://api.telegram.org/bot{TG_API_KEY_FOR_USERS}/setWebhook" #?url=https://{whook}/api/bot_actions/webhook



@app.get('/')
async def root():
    return HTMLResponse('''<body><a href="/api/auth/google_login">Log In</a>
                        <a href="/api/auth/google_logout">Logout</a></body>''')
                        


@app.get('/hello/', status_code=status.HTTP_200_OK)
async def hello():
    message = {'message': 'hello!'}
    return message


@app.get('/token')
async def token(request: Request):
    return HTMLResponse('''
                <script>
                function send(){
                    var req = new XMLHttpRequest();
                    req.onreadystatechange = function() {
                        if (req.readyState === 4) {
                            console.log(req.response);
                            if (req.response["result"] === true) {
                                window.localStorage.setItem('jwt', req.response["access_token"]);
                                window.localStorage.setItem('refresh', req.response["refresh_token"]);
                            }
                        }
                    }
                    req.withCredentials = true;
                    req.responseType = 'json';
                    req.open("get", "/api/auth/token?"+window.location.search.substr(1), true);
                    req.send("");

                }
                </script>
                <button onClick="send()">Get FastAPI JWT Token</button>


                <button onClick='fetch("http://127.0.0.1:8000/api/auth/google_logout",{
                    headers:{
                        "Authorization": "Bearer " + window.localStorage.getItem("jwt")
                    },
                }).then((r)=>r.json()).then((msg)=>{
                    console.log(msg);
                    if (msg["result"] === true) {
                        window.localStorage.removeItem("jwt");
                    }
                    });'>
                Google_Logout
                </button>
                
                 <button onClick='fetch("http://127.0.0.1:8000/api/auth/logout",{
                    headers:{
                        "Authorization": "Bearer " + window.localStorage.getItem("jwt")
                    },
                }).then((r)=>r.json()).then((msg)=>{
                    console.log(msg);
                    if (msg["result"] === true) {
                        window.localStorage.removeItem("jwt");
                    }
                    });'>
                Logout
                </button>

                <button onClick='fetch("http://127.0.0.1:7000/auth/refresh",{
                    method: "POST",
                    headers:{
                        "Authorization": "Bearer " + window.localStorage.getItem("jwt")
                    },
                    body:JSON.stringify({
                        grant_type:\"refresh_token\",
                        refresh_token:window.localStorage.getItem(\"refresh\")
                        })
                }).then((r)=>r.json()).then((msg)=>{
                    console.log(msg);
                    if (msg["result"] === true) {
                        window.localStorage.setItem("jwt", msg["access_token"]);
                    }
                    });'>
                Refresh
                </button>
                # <script>
                # function send(){
                #     var req = new XMLHttpRequest();
                #     req.onreadystatechange = function() {
                #         if (req.readyState === 4) {
                #             console.log(req.response);
                #             if (req.response["result"] === true) {
                #                 window.localStorage.setItem('jwt', req.response["access_token"]);
                #                 window.localStorage.setItem('refresh', req.response["refresh_token"]);
                #             }
                #         }
                #     }
                #     req.withCredentials = true;
                #     req.responseType = 'json';
                #     req.open("get", "/api/users/me?"+window.location.search.substr(1), true);
                #     req.send("");

                # }
                # </script>
                # <button onClick="send()">Get Me</button>

            ''')





async def request(url: str):#, payload: dict, debug: bool = False):
    async with AsyncClient() as client:
        request = await client.post(url)#, json=payload)
        # if debug:
        #     print(request.json())
        return request

async def set_telegram_webhook_url() -> bool:
    payload = {"url": f"{HOST_URL}/webhook/?url=https://{TG_API_KEY_FOR_USERS}/api/bot_actions/webhook"}
    req_to_users = await request(f"https://api.telegram.org/bot{TG_API_KEY_FOR_USERS}/setWebhook?url={HOST_URL}/api/bot_actions/webhook/to_users")#TELEGRAM_SET_WEBHOOK_URL, payload)
    req_to_providefs = await request(f"https://api.telegram.org/bot{TG_API_KEY_FOR_PROVIDERS}/setWebhook?url={HOST_URL}/api/bot_actions/webhook/to_providers")
    return req_to_users.status_code == 200



if __name__ == "__main__":
    # uvicorn.run("main:app", port=8000, host="localhost", reload=True)
    PORT = 8000
    http_tunnel = ngrok.connect(PORT, bind_tls=True)#, proto="http", name="dynamo-blues")
    public_url = http_tunnel.public_url
    HOST_URL = public_url
    print(HOST_URL)
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(set_telegram_webhook_url())

    if success:
        uvicorn.run("main:app", host="127.0.0.1", port=PORT, log_level="info", reload=True)
    else:
        print("Fail, closing the app.")
    # uvicorn.run("main:app", host="127.0.0.1", port=PORT, log_level="info", reload=True)

#f"https://api.telegram.org/bot{TG_API}/setWebhook?url=https://{whook}/api/bot_actions/webhook")
