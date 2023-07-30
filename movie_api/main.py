from fastapi import Depends,FastAPI, Body, Path, Query,HTTPException, Request
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel,Field
from typing import Optional,List
import datetime
from jwt_manager import create_token,validate_token


app = FastAPI(title= 'Mi aplicacion con FastAPI')
#Para cambiar el nombre de la aplicacion
app.title = "Mi FastAPI"
# cambiar la version 
app.version = "0.0.2"

class User(BaseModel):
    email:str
    password:str

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != "admin@gmail.com":
            raise HTTPException(status_code=403, detail="Credenciales son invalidas")

class Movie(BaseModel):
    id: Optional[int] = None
    title:      str =   Field(min_length = 5,max_length = 20)
    overview:   str =   Field(min_length = 10,max_length = 100 )
    year:       int =   Field(le = datetime.date.today().year)
    rating:     float = Field(ge=1, le = 10.0)
    category:   str =   Field(max_length = 20, min_length = 3)


    model_config = {
            "json_schema_extra" : {
                "example": [{
                    "id": 1,
                    "title": "Mi Pelicula",
                    "overview": "Descripcion de la mia pelicula",
                    "year": 2022,
                    "rating": 9.0,
                    "category": "Anime"
                }]
            }
        }

movies = [
    {
    'id': 1,
    'title': 'Avatar',
    'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
    'year': 2009,
    'rating': 7.8,
    'category': 'Acción'    
    },
    {
    'id': 2,
    'title': 'Avatar',
    'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
    'year': 2010,
    'rating': 7.8,
    'category': 'Acción'    
    } 
]


# @app.get('/')
# esta linea para agregar listas de rutas
@app.get('/',tags=['home'])
def message():
    return HTMLResponse('<h1>Hello world</h1>')

@app.post('/login',tags=['auth'])
def login(user:User):
    if user.email == 'admin@gmail.com' and user.password == 'admin':
        token:str =create_token(user.dict())
        return JSONResponse(status_code=200,content=token)
    return user

@app.get('/movies',tags=['movies'],response_model=List[Movie],status_code=200,dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    return JSONResponse(status_code=200,content=movies)

# parametro ruta
@app.get('/movies/{id}',tags=['movies'],response_model=Movie)
def get_movie(id: int = Path(ge=1,le=2000)) -> Movie:
    for item in movies:
        if item["id"]== id:
            return JSONResponse(status_code=200,content=item)
    return JSONResponse(status_code=404,content=[])

# cuando asignamos un parametro a la funcion pero  no se
# especifica en la URL se toma como un parametro Query
@app.get('/movies/',tags=['movies'],response_model=List[Movie])
def get_movies_by_category(category: str = Query(min_length = 5,max_length=15)) -> List[Movie]: 
    data = [item for item in movies if  item["category"]== category]
    return JSONResponse(status_code=200,content=data)

# Metodo post
# importamos Body en la seccion de imports
# ahora agregamos = Body() despues de cada parametro para indicar que estos se pasaran como parte del body
@app.post('/movies',tags=['movies'],response_model=dict,status_code=201)
def create_movie(movie:Movie) -> dict:
    movies.append(movie.dict())
    return JSONResponse(status_code=201,content={'message':"Se ha registrado la pelicula"})

# metodo put
@app.put('/movies/{id}',tags=['movies'],response_model=dict)
def update_movie(id:int, movie:Movie) -> dict:
    for item in movies:
        if item["id"] == id:
            item["title"]    =  movie.title
            item["overview"] =  movie.overview
            item["year"]     =  movie.year
            item["rating"]   =  movie.rating
            item["category"] =  movie.category
            return JSONResponse(content={'message':"Se ha modificado la pelicula"})
    return JSONResponse(status_code=404,content={'message':"No se encontro la peli a cambiar"})

# metodo delete
@app.delete('/movies/{id}',tags=['movies'],response_model=dict)
def delete_movie(id:int) -> dict:
    for item in movies:
        if item['id'] == id:
            movies.remove(item)
            return JSONResponse(content={'message':"Se ha borrado la pelicula"})
    return ['Aqui no se encontro la pelicula a borrar']