import logging
from pathlib import Path

from fastapi import Depends, Request, FastAPI
from fastapi.staticfiles import StaticFiles

from dew_gwdata.webapp.handlers import api
from dew_gwdata.webapp.handlers import home
from dew_gwdata.webapp.handlers import schema
from dew_gwdata.webapp.handlers import search
from dew_gwdata.webapp.handlers import well
from dew_gwdata.webapp.handlers import wells

logger = logging.getLogger(__name__)

app = FastAPI(debug=True)

static_path = Path(__file__).parent / "static"
pydocs_path = (
    Path(r"r:\dfw_cbd")
    / "projects"
    / "projects_gw"
    / "state"
    / "groundwater_toolbox"
    / "python"
    / "wheels"
    / "docs"
)

app.mount("/python-docs", StaticFiles(directory=pydocs_path), name="pydocs_path")
app.mount("/static", StaticFiles(directory=static_path), name="static")

app.include_router(api.router)
app.include_router(home.router)
app.include_router(schema.router)
app.include_router(search.router)
app.include_router(well.router)
app.include_router(wells.router)
