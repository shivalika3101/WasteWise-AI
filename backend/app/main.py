import contextlib as _contextlib
import fastapi as _fastapi
import fastapi.middleware.cors as _cors
import app.bootstrap as _bootstrap
import app.config as _config
import app.predictor as _predictor
import app.routers.admin as _admin
import app.routers.auth as _auth
import app.routers.blog as _blog
import app.routers.users as _users
import app.routers.predictions as _predictions


@_contextlib.asynccontextmanager
async def lifespan(app: _fastapi.FastAPI):
    _bootstrap.run()
    yield


app = _fastapi.FastAPI(lifespan=lifespan)
app.add_middleware(
    _cors.CORSMiddleware,
    allow_origins=_config.get_settings().frontend_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(_admin.router)
app.include_router(_auth.router)
app.include_router(_blog.router)
app.include_router(_users.router)
app.include_router(_predictions.router)


@app.get("/health")
def health():
    return {"status": "ok"}
