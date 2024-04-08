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


def get_well_metadata(df, dh_no, env="prod"):
    cols = ["dh_no", "unit_hyphen", "obs_no", "dh_name"]

    def check_columns():
        for col in cols:
            if not col in df.columns:
                return False
        return True

    if len(df) and check_columns():
        result = df[cols].iloc[0]
    else:
        db = connect_to_sageodata(service_name=env)
        result = db.wells_summary([dh_no])[cols].iloc[0]
    result["title"] = webapp_utils.make_dh_title(result)
    return result


@router.get("/well_summary")
def well_summary(request: Request, dh_no: int, env: str = "prod") -> str:
    db = connect_to_sageodata(service_name=env)
    well = db.wells_summary([dh_no]).iloc[0]
    groups = db.drillhole_groups([dh_no]).pipe(gd.cleanup_columns)
    elev = db.elevation_surveys([dh_no]).pipe(gd.cleanup_columns)
    groups["sort_key"] = groups.group_type.map(
        {"OMN": 0, "PR": 1, "OMH": 2, "GDU": 3, "MDU": 4}
    )
    groups = groups.sort_values(["sort_key", "group_modified_date"])
    groups = groups.drop(
        [
            "well_id",
            "sort_key",
            "dh_created_by",
            "dh_creation_date",
            "dh_modified_by",
            "dh_modified_date",
            "group_created_by",
            "group_creation_date",
            "group_modified_by",
            "group_modified_date",
        ],
        axis=1,
    )
    elev_cols = [
        "elev_date",
        "applied_date",
        "ground_elev",
        "ref_elev",
        "survey_meth",
        "ref_point_type",
        "comments",
    ]
    elev = elev[elev_cols]

    well["title"] = webapp_utils.make_dh_title(well)
    well_table = webapp_utils.series_to_html(well)
    groups_table = webapp_utils.frame_to_html(groups)
    elev_table = webapp_utils.frame_to_html(elev)

    return templates.TemplateResponse(
        "well_summary.html",
        {
            "request": request,
            "env": env,
            "title": well.title,
            "redirect_to": "well_summary",
            "wells_title": "1 well",
            "wells_query_params": "url_str=" + webapp_utils.dhnos_to_urlstr([dh_no]),
            "well": well,
            "well_table": well_table,
            "groups_table": groups_table,
            "elev_table": elev_table,
        },
    )


@router.get("/well_manual_water_level")
def well_manual_water_level(
    request: Request, dh_no: int, param: str = "swl", env: str = "prod"
) -> str:
    db = connect_to_sageodata(service_name=env)
    df = db.water_levels([dh_no]).sort_values("obs_date", ascending=False)
    well = get_well_metadata(df, dh_no)

    table = webapp_utils.frame_to_html(gd.cleanup_columns(df, keep_cols=[]))

    chart_rows = []
    for idx, record in (
        df.dropna(subset=["swl", "obs_date"], how="any")
        .sort_values("obs_date")
        .iterrows()
    ):
        record = record.to_dict()
        record["js_date"] = record["obs_date"].strftime(f'new Date("%Y/%m/%d")')
        if param in ("dtw", "swl"):
            value = str(record[param] * -1)
        elif param == "rswl":
            value = str(record[param])
        if pd.isnull(value) or value == "NaT" or str(value) == "nan":
            value = "NaN"
        row = "[ " + record["js_date"] + ", " + value + "]"
        chart_rows.append(row)
    chart_data = ",".join(chart_rows)

    return templates.TemplateResponse(
        "well_manual_water_level.html",
        {
            "request": request,
            "env": env,
            "title": well.title,
            "redirect_to": "well_manual_water_level",
            "wells_title": "1 well",
            "wells_query_params": "url_str=" + webapp_utils.dhnos_to_urlstr([dh_no]),
            "well": well,
            "df": df,
            "chart_data": chart_data,
            "table": table,
            "param": param,
        },
    )


@router.get("/well_logger_water_level")
def well_logger_water_level(
    request: Request,
    dh_no: int,
    param: str = "swl",
    freq: str = "1d",
    keep_grades: str = "1, 20, 30",
    max_gap_days: float = 1,
    start: str = "",
    finish: str = "",
    env: str = "prod",
    aqts_env: str = "prod",
) -> str:
    if not start:
        start = None
        start_str = ""
    else:
        start = gd.timestamp_acst(start)
        start_str = start.strftime("%Y-%m-%d")

    if not finish:
        finish = None
        finish_str = ""
    else:
        finish = gd.timestamp_acst(finish)
        finish_str = finish.strftime("%Y-%m-%d")

    keep_grades = [int(g) for g in keep_grades.split(",")] if keep_grades else []
    keep_grades_str = ", ".join([f"{g:.0f}" for g in sorted(keep_grades)])

    db = connect_to_sageodata(service_name=env)
    summ = db.wells_summary([dh_no])
    well = get_well_metadata(summ, dh_no)
    aq = gd.DEWAquarius(env=aqts_env)
    dfs = aq.fetch_timeseries_data(
        well.unit_hyphen,
        param=param,
        freq=freq,
        max_gap_days=max_gap_days,
        start=start,
        finish=finish,
        keep_grades=keep_grades,
    )

    chart_rows = []
    df = gd.join_logger_data_intervals(dfs)
    for idx, record in df.iterrows():
        record = record.to_dict()
        record["js_date"] = record["timestamp"].strftime(f'new Date("%Y/%m/%d %H:%M")')
        if param in ("dtw", "swl"):
            value = str(record[param] * -1)
        elif param == "rswl":
            value = str(record[param])
        if pd.isnull(value) or value == "NaT" or str(value) == "nan":
            value = "NaN"
        row = "[ " + record["js_date"] + ", " + value + "]"
        chart_rows.append(row + "\n")
    chart_data = ",".join(chart_rows)

    download_url = (
        f"/api/well_best_available_logger_data"
        f"?unit_hyphen={well.unit_hyphen}"
        f"&param={param}"
        f"&freq={freq}"
        f"&keep_grades={keep_grades_str}"
        f"&max_gap_days={int(max_gap_days)}"
        f"&start={start_str}"
        f"&finish={finish_str}"
        f"&aqts_env={aqts_env}"
        f"&format=csv"
    )

    dsets = gd.get_logger_interval_details(dfs)
    dsets["csv_download"] = dsets.apply(
        lambda row: (
            f"<a href='"
            f"/api/well_best_available_logger_data"
            f"?unit_hyphen={well.unit_hyphen}"
            f"&param={param}"
            f"&freq={freq}"
            f"&keep_grades={keep_grades_str}"
            f"&max_gap_days={int(max_gap_days)}"
            f"&start={row.start_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            f"&finish={row.finish_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            f"&aqts_env={aqts_env}"
            f"&format=csv"
            f"'>{row.dataset_length}-row CSV</a>"
        ), axis=1
    )
    dsets_table = webapp_utils.frame_to_html(dsets)

    return templates.TemplateResponse(
        "well_logger_water_level.html",
        {
            "request": request,
            "env": env,
            "aqts_env": aqts_env,
            "title": well.title,
            "redirect_to": "well_logger_water_level",
            "wells_title": "1 well",
            "wells_query_params": "url_str=" + webapp_utils.dhnos_to_urlstr([dh_no]),
            "well": well,
            "chart_data": chart_data,
            "start": start_str,
            "finish": finish_str,
            "freq": freq,
            "max_gap_days": max_gap_days,
            "param": param,
            "keep_grades": keep_grades_str,
            "dsets_table": dsets_table,
            "download_url": download_url,
        },
    )


@router.get("/well_combined_water_level")
def well_combined_water_level(
    request: Request,
    dh_no: int,
    param: str = "swl",
    freq: str = "1d",
    keep_grades: str = "1, 20, 30",
    max_gap_days: float = 550,
    start: str = "",
    finish: str = "",
    env: str = "prod",
    aqts_env: str = "prod",
) -> str:
    if not start:
        start = None
        start_str = ""
    else:
        start = gd.timestamp_acst(start)
        start_str = start.strftime("%Y-%m-%d")

    if not finish:
        finish = None
        finish_str = ""
    else:
        finish = gd.timestamp_acst(finish)
        finish_str = finish.strftime("%Y-%m-%d")

    keep_grades = [int(g) for g in keep_grades.split(",")] if keep_grades else []
    keep_grades_str = ", ".join([f"{g:.0f}" for g in sorted(keep_grades)])

    db = connect_to_sageodata(service_name=env)
    summ = db.wells_summary([dh_no])
    well = get_well_metadata(summ, dh_no)

    dfs = gd.get_combined_water_level_dataset(
        [well.dh_no],
        db=db,
        param=param,
        freq=freq,
        start=start,
        finish=finish,
        max_gap_days=max_gap_days,
        keep_grades=keep_grades,
        aq_env=aqts_env,
    )
    df = gd.join_logger_data_intervals(dfs)

    chart_rows = []
    chart_columns = [c for c in [f"{param}-SAGD", f"{param}-AQTS", param] if c in df]
    for idx, record in df.iterrows():
        record = record.to_dict()
        row_str = "[ " + record["timestamp"].strftime(f'new Date("%Y/%m/%d %H:%M")')
        for column in chart_columns:
            value = record[column]
            if not str(value) in ("null", "NaN", "NaT"):
                if column.startswith("rswl"):
                    value = f"{value:.3f}"
                else:
                    value = f"{value * -1:.3f}"

            if value in ("NaT", "NaN", "nan"):
                value = "NaN"
            elif value == "null":
                # important to keep "null" - used by dygraphs
                pass
            else:
                # numerical value has been encoded.
                pass

            row_str += f", {value}"
        row_str += "]"
        chart_rows.append(row_str + "\n")
    chart_data = ",".join(chart_rows)
    chart_columns_str = ", ".join([f'"{col}"' for col in chart_columns])

    url_str = webapp_utils.dhnos_to_urlstr([dh_no])

    download_url = (
        f"/api/well_best_available_combined_water_level_data"
        f"?url_str={url_str}"
        f"&param={param}"
        f"&freq={freq}"
        f"&keep_grades={keep_grades_str}"
        f"&max_gap_days={int(max_gap_days)}"
        f"&start={start_str}"
        f"&finish={finish_str}"
        f"&env={env}"
        f"&aqts_env={aqts_env}"
        f"&format=csv"
    )
    dsets = gd.get_logger_interval_details(dfs)
    if len(dsets):
        dsets["csv_download"] = dsets.apply(
            lambda row: (
                f"<a href='"
                f"/api/well_best_available_combined_water_level_data"
                f"?url_str={url_str}"
                f"&param={param}"
                f"&freq={freq}"
                f"&keep_grades={keep_grades_str}"
                f"&max_gap_days={int(max_gap_days)}"
                f"&start={row.start_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                f"&finish={row.finish_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                f"&env={env}"
                f"&aqts_env={aqts_env}"
                f"&format=csv"
                f"'>{row.dataset_length}-row CSV</a>"
            ), axis=1
        )
    dsets_table = webapp_utils.frame_to_html(dsets)

    return templates.TemplateResponse(
        "well_combined_water_level.html",
        {
            "request": request,
            "env": env,
            "aqts_env": aqts_env,
            "title": well.title,
            "redirect_to": "well_combined_water_level",
            "wells_title": "1 well",
            "wells_query_params": f"url_str={url_str}",
            "well": well,
            "chart_data": chart_data,
            "chart_columns_str": chart_columns_str,
            "start": start_str,
            "finish": finish_str,
            "freq": freq,
            "max_gap_days": max_gap_days,
            "param": param,
            "keep_grades": keep_grades_str,
            "dsets_table": dsets_table,
            "download_url": download_url,
        },
    )


@router.get("/well_salinity")
def well_salinity(request: Request, dh_no: int, env: str = "prod") -> str:
    db = connect_to_sageodata(service_name=env)
    df = db.salinities([dh_no]).sort_values("collected_date", ascending=False)
    well = get_well_metadata(df, dh_no)
    table = webapp_utils.frame_to_html(
        gd.cleanup_columns(df, keep_cols=[]).drop(
            ["amg_easting", "amg_northing"], axis=1
        )
    )

    chart_rows = []
    for idx, record in (
        df.dropna(subset=["ec", "collected_date"], how="any")
        .sort_values("collected_date")
        .iterrows()
    ):
        record = record.to_dict()
        record["js_date"] = record["collected_date"].strftime(f'new Date("%Y/%m/%d")')
        row = (
            "[ "
            + record["js_date"]
            + ", "
            + str(record["ec"])
            + ", "
            + str(record["tds"])
            + "]"
        )
        chart_rows.append(row)
    chart_data = ",".join(chart_rows)

    return templates.TemplateResponse(
        "well_salinity.html",
        {
            "request": request,
            "env": env,
            "title": well.title,
            "redirect_to": "well_salinity",
            "wells_title": "1 well",
            "wells_query_params": "url_str=" + webapp_utils.dhnos_to_urlstr([dh_no]),
            "well": well,
            "df": df,
            "chart_data": chart_data,
            "table": table,
        },
    )


@router.get("/well_drillhole_logs")
def well_drillhole_logs(request: Request, dh_no: int, env: str = "prod") -> str:
    db = connect_to_sageodata(service_name=env)

    logs = db.drillhole_logs([dh_no]).sort_values("log_date", ascending=True)
    log_types = logs.log_type.unique()

    drill = db.drillers_logs([dh_no]).sort_values(["depth_from", "depth_to"])
    lith = db.lith_logs([dh_no]).sort_values(["depth_from", "depth_to"])
    strat = db.strat_logs([dh_no]).sort_values(["depth_from", "depth_to"])
    hstrat = db.hydrostrat_logs([dh_no])  # .sort_values(["depth_from", "depth_to"])

    well = get_well_metadata(logs, dh_no)

    logs_table = webapp_utils.frame_to_html(gd.cleanup_columns(logs, keep_cols=[]))
    drill_table = webapp_utils.frame_to_html(gd.cleanup_columns(drill, keep_cols=[]))
    lith_table = webapp_utils.frame_to_html(gd.cleanup_columns(lith, keep_cols=[]))
    strat_table = webapp_utils.frame_to_html(gd.cleanup_columns(strat, keep_cols=[]))
    hstrat_table = webapp_utils.frame_to_html(gd.cleanup_columns(hstrat, keep_cols=[]))

    return templates.TemplateResponse(
        "well_drillhole_logs.html",
        {
            "request": request,
            "env": env,
            "title": well.title,
            "redirect_to": "well_drillhole_logs",
            "wells_title": "1 well",
            "wells_query_params": "url_str=" + webapp_utils.dhnos_to_urlstr([dh_no]),
            "well": well,
            "logs": logs,
            "log_types": log_types,
            "drill": drill,
            "lith": lith,
            "strat": strat,
            "hstrat": hstrat,
            "logs_table": logs_table,
            "drill_table": drill_table,
            "lith_table": lith_table,
            "strat_table": strat_table,
            "hstrat_table": hstrat_table,
        },
    )


@router.get("/well_construction")
def well_construction(request: Request, dh_no: int, env: str = "prod") -> str:
    db = connect_to_sageodata(service_name=env)

    cevents_df = db.construction_events([dh_no]).sort_values(
        "completion_date", ascending=False
    )

    well = get_well_metadata(cevents_df, dh_no)

    bool_flags = [
        "screened",
        "pcemented",
        "developed",
        "abandoned",
        "backfilled",
        "dry",
        "enlarged",
        "flowing",
        "replacement",
        "rehabilitated",
        "core_flag",
    ]
    cevents_df["activity"] = cevents_df.apply(
        lambda row: " + ".join([col for col in bool_flags if row[col] == "Y"]), axis=1
    )
    summary_cols = [
        "completion_date",
        "event_type",
        "activity",
        "wcr_id",
        "permit_no",
        "comments",
        "total_depth",
        "final_depth",
        "current_depth",
        "final_swl",
        "final_yield",
        "drill_method",
        "drill_to",
        "casing_material",
        "casing_min_diam",
        "casing_to",
        "pzone_type",
        "pzone_material",
        "pzone_diam",
        "pzone_from",
        "pzone_to",
    ]
    summary_table = webapp_utils.frame_to_html(
        gd.cleanup_columns(cevents_df[summary_cols], keep_cols=[])
    )

    # drilling, casing, wcuts, pzones, other_items
    drilling = db.drilled_intervals([dh_no]).sort_values(["depth_from", "depth_to"])
    casing = db.casing_strings([dh_no]).sort_values(["depth_from", "depth_to"])
    seals = db.casing_seals([dh_no]).sort_values("seal_depth")
    wcuts = db.water_cuts([dh_no]).sort_values(["depth_from", "depth_to"])
    pzones = db.production_zones([dh_no]).sort_values(["pzone_from", "pzone_to"])
    other_items = db.other_construction_items([dh_no]).sort_values(
        ["depth_from", "depth_to"]
    )

    cevents = []
    sevents = []

    kws = dict(
        keep_cols=[],
        drop=("construction_aquifer", "completion_no", "completion_date", "event_type"),
    )

    for completion_no, cevent_summ in cevents_df.groupby("completion_no"):
        summary = gd.cleanup_columns(cevent_summ, keep_cols=[]).iloc[0]
        if summary.event_type == "C":
            title = f"Construction event "
        elif summary.event_type == "S":
            title = f"Survey event "
        title += webapp_utils.format_datetime(summary.completion_date)

        summary = summary.drop(
            [
                "latest",
                "max_case",
                "orig_case",
                "lod_case",
                "from_flag",
            ]
        )

        summary_1 = summary[
            [
                "completion_no",
                "event_type",
                "activity",
                "commenced_date",
                "completion_date",
                "wcr_id",
                "permit_no_full",
                "plant_operator",
                "construction_aquifer",
                "start_depth",
                "total_depth",
                "final_depth",
                "created_by",
                "creation_date",
                "modified_by",
                "modified_date",
            ]
        ]

        summary_2 = summary[
            [
                "drill_method",
                "drill_from",
                "drill_to",
                "drill_diam",
                "casing_material",
                "casing_from",
                "casing_to",
                "casing_diam",
                "casing_min_diam",
                "pzone_type",
                "pzone_material",
                "pzone_from",
                "pzone_to",
                "pzone_diam",
                "pcement_from",
                "pcement_to",
            ]
        ]

        cevent = {
            "data_types": [],
            "title": title,
            "summary": summary,
            "summary_1": summary_1,
            "summary_2": summary_2,
            "comments": summary.comments,
            "summary_table": webapp_utils.series_to_html(
                summary.drop(index=["comments"])
            ),
            "summary_1_table": webapp_utils.series_to_html(summary_1),
            "summary_2_table": webapp_utils.series_to_html(summary_2),
        }

        cevent_drilling = drilling[drilling.completion_no == completion_no]
        if len(cevent_drilling) > 0:
            cevent["drilling"] = webapp_utils.frame_to_html(
                gd.cleanup_columns(cevent_drilling, **kws).T
            )
            cevent["data_types"].append("drilling")

        cevent_casing = casing[casing.completion_no == completion_no]
        if len(cevent_casing) > 0:
            cevent["casing"] = webapp_utils.frame_to_html(
                gd.cleanup_columns(cevent_casing, **kws).T
            )
            cevent["data_types"].append("casing")

        cevent_seals = seals[seals.completion_no == completion_no]
        if len(cevent_seals) > 0:
            cevent["seals"] = webapp_utils.frame_to_html(
                gd.cleanup_columns(cevent_seals, **kws).T
            )
            cevent["data_types"].append("seals")

        cevent_wcuts = wcuts[wcuts.completion_no == completion_no]
        if len(cevent_wcuts) > 0:
            cevent["wcuts"] = webapp_utils.frame_to_html(
                gd.cleanup_columns(cevent_wcuts, **kws)
            )
            cevent["data_types"].append("wcuts")

        cevent_pzones = pzones[pzones.completion_no == completion_no]
        if len(cevent_pzones) > 0:
            cevent["pzones"] = webapp_utils.frame_to_html(
                gd.cleanup_columns(cevent_pzones, **kws).T
            )
            cevent["data_types"].append("pzones")

        cevent_other_items = other_items[other_items.completion_no == completion_no]
        if len(cevent_other_items) > 0:
            cevent["other_items"] = webapp_utils.frame_to_html(
                gd.cleanup_columns(cevent_other_items, **kws).T
            )
            cevent["data_types"].append("other_items")

        if summary.event_type == "C":
            cevents.append(cevent)
        elif summary.event_type == "S":
            sevents.append(cevent)

    cevents = sorted(cevents, key=lambda x: x["summary"].completion_date)
    sevents = sorted(sevents, key=lambda x: x["summary"].completion_date)

    return templates.TemplateResponse(
        "well_construction.html",
        {
            "request": request,
            "env": env,
            "title": well.title,
            "redirect_to": "well_construction",
            "wells_title": "1 well",
            "wells_query_params": "url_str=" + webapp_utils.dhnos_to_urlstr([dh_no]),
            "well": well,
            "summary_table": summary_table,
            "events": [cevents, sevents],
        },
    )


@router.get("/well_drillhole_document_images")
def well_drillhole_document_images(
    request: Request,
    dh_no: int,
    env: str = "prod",
    width: int = 950,
    height: int = -1,
    inline: bool = False,
    new_tab: bool = False,
) -> str:
    db = connect_to_sageodata(service_name=env)
    df = db.drillhole_document_image_list([dh_no])
    well = get_well_metadata(df, dh_no)

    images = [im for idx, im in df.iterrows()]

    return templates.TemplateResponse(
        "well_drillhole_document_images.html",
        {
            "request": request,
            "env": env,
            "title": well.title,
            "redirect_to": "well_drillhole_document_images",
            "wells_title": "1 well",
            "wells_query_params": "url_str=" + webapp_utils.dhnos_to_urlstr([dh_no]),
            "well": well,
            "df": df,
            "images": images,
            "width": width,
            "height": height,
            "inline": inline,
            "new_tab": new_tab,
            "target": "_blank" if new_tab else "",
        },
    )
