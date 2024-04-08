from pathlib import Path
from typing import Annotated

import pandas as pd
from geojson import Feature, Point
from fastapi import APIRouter, Request, Query, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.datastructures import URL

from sageodata_db import connect as connect_to_sageodata
from sageodata_db import load_predefined_query
from sageodata_db.utils import parse_query_metadata

import dew_gwdata as gd
from dew_gwdata.sageodata_datamart import get_sageodata_datamart_connection

from dew_gwdata.webapp import utils as webapp_utils
from dew_gwdata.webapp.models import queries


router = APIRouter(prefix="/app", include_in_schema=False)

templates_path = Path(__file__).parent.parent / "templates"

templates = Jinja2Templates(directory=templates_path)


@router.get("/wells_summary")
def wells_summary(
    request: Request,
    query: Annotated[queries.Wells, Depends()],
):
    db = connect_to_sageodata(service_name=query.env)
    wells, name, name_safe, query_params = query.find_wells()
    dh_nos = wells.dh_no
    title = name
    if len(dh_nos):
        df = db.wells_summary(dh_nos)
    else:
        cols, _, _ = parse_query_metadata(load_predefined_query("wells_summary"))
        df = pd.DataFrame(columns=cols)

    df = df.sort_values(
        [query.sort], ascending=True if query.order.startswith("asc") else False
    )

    df_for_table = df[
        [
            "dh_no",
            "unit_hyphen",
            "obs_no",
            "dh_name",
            "aquifer",
            "latest_status",
            "latest_swl",
            "latest_tds",
            "purpose",
            "owner",
            "orig_drilled_depth",
            "orig_drilled_date",
            "latest_cased_to",
            "comments",
            "pwa",
            "pwra",
        ]
    ]
    title_series = df_for_table.apply(
        lambda well: (
            f'<nobr><a href="/app/well_summary?dh_no={well.dh_no}&env={query.env}">'
            f'{webapp_utils.make_dh_title(well, elements=("unit_no", "obs_no"))}</a></nobr>'
        ),
        axis=1,
    )
    df_for_table.insert(0, "title", title_series)
    df_for_table = df_for_table.drop(["unit_hyphen", "obs_no"], axis=1)
    table = webapp_utils.frame_to_html(df_for_table)

    egis_layer_definition_query = (
        "DHNO IN (" + ",".join([str(dh_no) for dh_no in df.dh_no]) + ")"
    )

    return templates.TemplateResponse(
        "wells_summary.html",
        {
            "request": request,
            "env": query.env,
            "title": title,
            "query": query,
            "redirect_to": "wells_summary",
            "wells_title": title,
            "wells_query_params": query_params,
            "wells": df,
            "wells_table": table,
            "egis_layer_definition_query": egis_layer_definition_query,
        },
    )


@router.get("/wells_data_available")
def wells_data_available(
    request: Request,
    query: Annotated[queries.Wells, Depends()],
):
    db = connect_to_sageodata(service_name=query.env)
    wells, name, name_safe, query_params = query.find_wells()
    dh_nos = wells.dh_no
    title = name
    if len(dh_nos):
        summ = db.wells_summary(dh_nos)
    else:
        cols, _, _ = parse_query_metadata(load_predefined_query("wells_summary"))
        summ = pd.DataFrame(columns=cols)

    if len(dh_nos):
        data = db.data_available(dh_nos)
    else:
        cols, _, _ = parse_query_metadata(load_predefined_query("data_available"))
        data = pd.DataFrame(columns=cols)

    summ = summ.sort_values(
        [query.sort], ascending=True if query.order.startswith("asc") else False
    )

    col_to_endpoint_map = {
        "drill_or_lith_logs": "well_drillhole_logs",
        "strat_or_hydro_logs": "well_drillhole_logs",
        "water_levels": "well_manual_water_level",
        "elev_surveys": "well_summary",
        "aquarius_flag": "well_combined_water_level",
        "salinities": "well_salinity",
        "water_cuts": "well_construction",
        # "geophys_logs": "",
        "dh_docimg_flag": "well_drillhole_document_images",
        # "photo_flag": "",
    }
    for col, endpoint in col_to_endpoint_map.items():
        data[col] = data.apply(
            lambda row: (
                f'<a href="/app/{endpoint}?dh_no={row.dh_no}&env={query.env}">{row[col]}</a>'
                if row[col] > 0
                else 0
            ),
            axis=1,
        )

    summ_keep = [
        "dh_no",
        "unit_hyphen",
        "obs_no",
        "dh_name",
        "aquifer",
        "orig_drilled_depth",
        "orig_drilled_date",
    ]
    summ["orig_drilled_depth"] = summ.orig_drilled_depth.apply(
        lambda v: f"{v:.02f}" if not pd.isnull(v) else ""
    )
    df_for_table = pd.merge(summ[summ_keep], data, on="dh_no")

    title_series = df_for_table.apply(
        lambda well: (
            f'<nobr><a href="/app/well_summary?dh_no={well.dh_no}&env={query.env}">'
            f'{webapp_utils.make_dh_title(well, elements=("unit_no", "obs_no"))}</a></nobr>'
        ),
        axis=1,
    )
    df_for_table.insert(0, "title", title_series)
    df_for_table = df_for_table.drop(["unit_hyphen", "obs_no"], axis=1)

    def series_styler(series):
        def value_function(value):
            if value == 0:
                return "border: 1px solid grey;"
            else:
                return "background-color: lightgreen; border: 1px solid grey;"

        return series.apply(value_function)

    apply_colours_to = [
        c for c in df_for_table.columns if not c in summ.columns and not c == "title"
    ]

    table = webapp_utils.frame_to_html(
        df_for_table,
        apply=series_styler,
        apply_kws=dict(
            axis=1,
            subset=apply_colours_to,
        ),
    )

    egis_layer_definition_query = (
        "DHNO IN (" + ",".join([str(dh_no) for dh_no in summ.dh_no]) + ")"
    )

    return templates.TemplateResponse(
        "wells_data_available.html",
        {
            "request": request,
            "env": query.env,
            "title": title,
            "query": query,
            "redirect_to": "wells_data_available",
            "wells_title": title,
            "wells_query_params": query_params,
            "wells": summ,
            "wells_table": table,
            "egis_layer_definition_query": egis_layer_definition_query,
        },
    )


@router.get("/wells_geojson_summary")
def wells_map(
    request: Request,
    query: Annotated[queries.Wells, Depends()],
):
    db = connect_to_sageodata(service_name=query.env)
    wells, name, name_safe, query_params = query.find_wells()
    dh_nos = wells.dh_no
    title = name
    if len(dh_nos):
        df = db.wells_summary(dh_nos)
    else:
        cols, _, _ = parse_query_metadata(load_predefined_query("wells_summary"))
        df = pd.DataFrame(columns=cols)

    df = df.sort_values([query.sort])

    features = []
    for idx, row in df.iterrows():
        feature = Feature(geometry=Point(()))

    return templates.TemplateResponse(
        "wells_map.html",
        {
            "request": request,
            "env": query.env,
            "redirect_to": "wells_map",
            "title": title,
            "wells_title": title,
            "wells_query_params": query_params,
            "wells": df,
        },
    )
