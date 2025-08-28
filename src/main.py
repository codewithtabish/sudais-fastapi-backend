from dotenv import load_dotenv
from fastapi import FastAPI, Response, status

from routes import personal_routes

load_dotenv()
app:FastAPI = FastAPI()


@app.get("/")
def read_root():
    return Response(
        content="Hello, World!",
        status_code=status.HTTP_200_OK
    )
    
    

app.include_router(personal_routes,prefix='/api/v1/info',tags=['personal','info'])

    



