from typing import Annotated
import logging

from fastapi import Query

from pydantic import BaseModel

from dew_gwdata import sageodata as connect_to_sageodata
from dew_gwdata.webapp import utils as webapp_utils


logger = logging.getLogger(__name__)

FIND_WELLS_COLUMN_MAPPER = {
    "unit_no.hyphen": "unit_hyphen",
    "unit_no.long": "unit_long",
    "obs_no.id": "obs_no",
}


class Wells(BaseModel):
    env: str = "PROD"

    # Search for wells by text (idq)
    idq: str = ""
    idq_unit_no: bool = True
    idq_dh_no: bool = False
    idq_obs_no: bool = True
    idq_dh_no_as_req: bool = True
    # Additionally, optionally, find wells within X of the first match
    idq_distance: float = 0

    # Find wells by direct reference
    url_str: str = ""

    # Find wells by group membership
    group_code: Annotated[list[str], Query()] = []

    # Find wells by name fragment search
    name_fragment: str = ""

    # FILTER OPTIONS

    # SORT OPTIONS
    sort: str = "dh_no"
    order: str = "ascending"

    def find_wells(self):
        self.group_code = [code.upper() for code in self.group_code]

        db = connect_to_sageodata(service_name=self.env)

        wells = None

        # Search
        if self.idq:
            id_types = []
            if self.idq_unit_no:
                id_types.append("unit_no")
            if self.idq_obs_no:
                id_types.append("obs_no")
            if self.idq_dh_no:
                id_types.append("dh_no")

            logger.debug(f"id_types requested: {id_types}")

            if self.idq_dh_no_as_req:
                # Try and search dh_no only if there is no result
                wells = db.find_wells(
                    self.idq, types=[t for t in id_types if not t == "dh_no"]
                ).df()
                if len(wells) == 0:
                    wells = db.find_wells(self.idq, types=id_types).df()
            else:
                wells = db.find_wells(self.idq, types=id_types).df()

            if self.idq_distance > 0:
                wells = db.drillhole_within_distance(wells.dh_no[0], self.idq_distance)
            else:
                wells = db.drillhole_details(wells.dh_no)

            x = str(self.idq)
            if len(x) > 12:
                x = x[:9] + "..."

            query_params = [
                f"idq={self.idq}",
                f"idq_unit_no={int(self.idq_unit_no)}",
                f"idq_obs_no={int(self.idq_obs_no)}",
                f"idq_dh_no={int(self.idq_dh_no)}",
                f"idq_dh_no_as_req={int(self.idq_dh_no_as_req)}",
            ]

            if self.idq_distance:
                name = f"Wells within {self.idq_distance} km of '{x}'"
                name_safe = f"{self.idq_distance}km_from_" + x.replace(" ", "_")
            else:
                name = f"Search '{x}'"
                name_safe = "search_" + x.replace(" ", "_")

        elif self.url_str:
            dh_nos = webapp_utils.urlstr_to_dhnos(self.url_str)
            wells = db.drillhole_details(dh_nos)
            name = f"Direct selection"
            name_safe = self.url_str
            query_params = [f"url_str={self.url_str}"]

        elif self.group_code:
            wells = db.wells_in_groups(self.group_code)
            name = f"Wells in {', '.join(self.group_code)}"
            name_safe = "_".join(self.group_code)
            query_params = [f"group_code={g}" for g in self.group_code]

        elif self.name_fragment:
            wells = db.drillhole_details_by_name_search(self.name_fragment)
            name = f"Search for '{self.name_fragment}'"
            name_safe = f"search_{self.name_fragment}"
            query_params = [f"name_fragment={self.name_fragment}"]

        else:
            wells = db.drillhole_details([0])
            name = f"Empty search??"
            name_safe = f"empty"
            query_params = [
                f"idq=",
                f"idq_unit_no=1",
                f"idq_obs_no=1",
                f"idq_dh_no=0",
                f"idq_dh_no_as_req=0",
            ]

        if self.sort == "dh_no":
            query_params.append("sort=dh_no")
        elif self.sort == "unit_hyphen":
            query_params.append("sort=unit_hyphen")

        # Filter
        ## TODO
        # if wells is None:
        #     wells = db.drillhole_details(dh_nos)

        name += f" ({len(wells)} wells)" if len(wells) != 1 else " (1 well)"
        if len(wells) == 1 and self.url_str:
            name_safe = f"dh_{wells.dh_no[0]}"

        # print(f"Prior to trimming - name_safe={name_safe}")
        # name_safe_fragments = name_safe.split("_")
        # print(f"name_safe_fragments = {name_safe_fragments}")
        # name_safe = "_".join(name_safe_fragments[:-1] + [name_safe_fragments[-1][:10]])
        name_safe = name_safe[:30]
        # print(f"After trimming - name_safe={name_safe}")

        query_params.append(f"env={self.env}")

        return wells, name, name_safe, "&".join(query_params)
