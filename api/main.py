from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import games, gems, reviews, stats

app = FastAPI(title="Steam Stats API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(gems.router, prefix="/api/gems", tags=["gems"])


@app.get("/")
def health_check():
    return {"status": "ok"}
