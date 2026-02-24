from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from fastapi.responses import RedirectResponse

from app.config import settings
from app.i18n import _, get_available_languages, load_translations
from app.web.deps import WebRedirectException

TEMPLATES_DIR = Path(__file__).parent / "templates"


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_translations()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/docs" if settings.APP_DEBUG else None,
        redoc_url="/redoc" if settings.APP_DEBUG else None,
        lifespan=lifespan,
    )

    # Middleware
    application.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="fleetcore_session",
        max_age=86400 * 7,
    )

    # Templates
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    application.state.templates = templates

    def get_lang(request: Request) -> str:
        return request.session.get("lang", settings.DEFAULT_LANGUAGE)

    def get_translation(key: str, request: Request, **kwargs) -> str:
        return _(key, lang=get_lang(request), **kwargs)

    application.state.get_translation = get_translation

    def template_globals(request: Request) -> dict:
        lang = get_lang(request)
        return {
            "lang": lang,
            "languages": get_available_languages(),
            "_": lambda key, **kw: _(key, lang=lang, **kw),
        }

    application.state.template_globals = template_globals

    # Redirect exception handler (for web auth redirects)
    @application.exception_handler(WebRedirectException)
    async def redirect_exception_handler(request: Request, exc: WebRedirectException):
        return RedirectResponse(url=exc.headers["Location"], status_code=302)

    # Static files
    application.mount("/static", StaticFiles(directory="static"), name="static")

    # API routes
    from app.api.v1.router import api_router

    application.include_router(api_router, prefix="/api/v1")

    # Web routes
    from app.web.router import web_router

    application.include_router(web_router)

    return application


app = create_app()
