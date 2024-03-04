from __future__ import annotations as _annotations


from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastui import prebuilt_html

from tables import router as table_router
from main import router as main_router



app = FastAPI()


app.include_router(table_router, prefix='/api/table')
app.include_router(main_router, prefix='/api')



@app.get('/favicon.ico', status_code=404, response_class=PlainTextResponse)
async def favicon_ico() -> str:
    return 'page not found'


@app.get('/{path:path}')
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title='Admin'))