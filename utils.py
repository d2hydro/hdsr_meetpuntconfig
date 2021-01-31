from typing import Tuple

import numpy as np
import pandas as pd
import re


def sort_validation_attribs(rule):
    result = {}
    for key, value in rule.items():
        if isinstance(value, str):
            result[key] = [value]
        elif isinstance(value, list):
            periods = [val["period"] for val in value]
            attribs = [val["attribute"] for val in value]
            result[key] = [attrib for _, attrib in sorted(zip(periods, attribs))]
    return result


def update_histtag(row, grouper):
    """Assign last histTag to waterstandsloc in df.apply method."""
    return next(
        (
            df.sort_values("total_max_end_dt", ascending=False)["serie"].values[0]
            for loc_id, df in grouper
            if loc_id == row["LOC_ID"]
        ),
        None,
    )


def update_date(row, mpt_df, date_threshold):
    """Return start and end-date in df.apply() method."""
    int_loc = row["LOC_ID"]
    if int_loc in mpt_df.index:
        start_date = mpt_df.loc[int_loc]["STARTDATE"].strftime("%Y%m%d")
        end_date = mpt_df.loc[int_loc]["ENDDATE"]
        if end_date > date_threshold:
            end_date = pd.Timestamp(year=2100, month=1, day=1)
        end_date = end_date.strftime("%Y%m%d")
    else:
        start_date = row["START"]
        end_date = row["EIND"]

    return start_date, end_date


def update_hlocs(row: pd.Series, h_locs: np.ndarray, mpt_df: pd.DataFrame) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """Add startdate and enddate op hoofdloc dataframe with df.apply() method."""
    loc_id = row.name
    start_date = row["STARTDATE"]
    end_date = row["ENDDATE"]

    if loc_id in h_locs:
        start_date = mpt_df[mpt_df.index.str.contains(loc_id[0:-1])]["STARTDATE"].dropna().min()

        end_date = mpt_df[mpt_df.index.str.contains(loc_id[0:-1])]["ENDDATE"].dropna().max()

    return start_date, end_date


def get_validation_attribs(validation_rules, int_pars=None, loc_type=None):
    """Get attributes from validationRules."""
    if int_pars is None:
        int_pars = [rule["parameter"] for rule in validation_rules]
    result = []
    for rule in validation_rules:
        if "type" in rule.keys():
            if rule["type"] == loc_type:
                if any(re.match(rule["parameter"], int_par) for int_par in int_pars):
                    for key, attribute in rule["extreme_values"].items():
                        if isinstance(attribute, list):
                            result += [value["attribute"] for value in attribute]
                        else:
                            result += [attribute]
        elif any(re.match(rule["parameter"], int_par) for int_par in int_pars):
            for key, attribute in rule["extreme_values"].items():
                if isinstance(attribute, list):
                    result += [value["attribute"] for value in attribute]
                else:
                    result += [attribute]
    return result


def idmap2tags(row, idmap):
    """Add FEWS-locationIds to hist_tags in df.apply() method."""
    # TODO: fix typing args
    # TODO: return type is np.NaN or a List[str]?
    # def idmap2tags(row: pd.Series, idmap: Optional[List[str]]) -> Union[np.NaN, List[str]]:
    exloc, expar = row["serie"].split("_", 1)
    fews_locs = [
        col["internalLocation"]
        for col in idmap
        if col["externalLocation"] == exloc and col["externalParameter"] == expar
    ]
    return np.NaN if fews_locs == 0 else fews_locs
