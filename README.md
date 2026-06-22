Plan
- [ ] FastAPI
  - [ ] Endpoints
    - [ ] User
      - [ ] Log in
      - [ ] Sign in
      - [ ] Edit profile
      - [ ] Safe session between request (middleware)
    - [ ] Analyzer
      - [x] Download img
      - [x] Processing on server (TOP)
      - [ ] Parallel processing
    - [ ] Researches
    - [ ] Researchers
    - [ ] Plants
    - [ ] Laboratories
    - [ ] Locations
  - [ ] Error handling
  - [ ] Middleware for response
  - [ ] Optimization 
    - [ ] Try to decrease size of module (cause: pytorch)
- [ ] DB
  - [ ] Fix the role model (admin, user?)
  - [ ] Create init sql file
  - [ ] Add neural_model entity
  - [ ] Add classification result entity
- [ ] Testing
  - [ ] Cold
  - [ ] Hot
  - [ ] Integration tests
  - [ ] Mocks
- [ ] Docker

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Монтируем папку со статикой React
app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

# Корневой маршрут отдаёт index.html
@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/dist/index.html")

# Остальные ваши API-эндпоинты
@app.get("/api/v1/studies")
async def get_studies():
    return [{"id": 1, "name": "Исследование 1"}]
