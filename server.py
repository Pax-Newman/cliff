from typing import Dict
from search import Model
from aiohttp import web

# define routes for the server

routes = web.RouteTableDef()

@routes.put('/testput')
async def testput(request: web.Request):
    print(request.json())

# expects a json with a field 
@routes.put('/addtoindex')
async def add_to_index(request: web.Request):
    body: Dict = request.json()
    body['']
    



# initialize the server, add the routes, and run it

app = web.Application()
app.add_routes(routes)

web.run_app(app)

