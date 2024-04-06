"""Module to handle data of the format required by ebas."""

from __future__ import annotations

import datetime
import logging
import re
from datetime import datetime, timedelta
from enum import IntEnum
from os import PathLike
from pathlib import Path
from typing import Any
from warnings import warn

import numpy as np
import pandas as pd
from ebas.io.file.nasa_ames import EbasNasaAmes
from nilutility.datatypes import DataObject
from nilutility.datetime_helper import DatetimeInterval

from avoca.flags import QA_Flag

logger = logging.getLogger(__name__)

# https://projects.nilu.no/ccc/flags/flags.html for more info on what ebas uses
flags_to_ebas: dict[QA_Flag, int] = {
    QA_Flag.MISSING: 999,  # 	M 	Missing measurement, unspecified reason
    QA_Flag.ZERO_NEG_CONC_EXT: 999,
    QA_Flag.INVALIDATED_EXT: 900,  # 	H 	Hidden and invalidated by data originator
    QA_Flag.EXTREME_VALUE: 458,  # V 	Extremely high value, outside four times standard deviation in a lognormal distribution
    QA_Flag.CALIBRATION: 683,  # 	I 	Invalid due to calibration. Used for Level 0.
    QA_Flag.BLANK: 684,  #  	Invalid due to zero/span check. Used for Level 0.
    QA_Flag.HEIGHT_INTEGRATION: 0,  # 	Valid
    QA_Flag.UNCORRELATED: 0,  # 	Valid
    QA_Flag.MET_OFFICE_BASELINE: 0,  # 	Valid
    QA_Flag.BELOW_DETECTION_LIMIT: 147,  # 	B 	Below detection limit
    QA_Flag.POLLUTION: 900,
    QA_Flag.SUSPICIOUS_RT: 900,
}

ebas_flag_to_avoca: dict[int, QA_Flag] = {
    ebas_flag: avoca_flag for avoca_flag, ebas_flag in flags_to_ebas.items()
}
# Set some flags with Multiple values to the same value
ebas_flag_to_avoca.pop(0)  # 0 is valid in avoca
ebas_flag_to_avoca[999] = QA_Flag.MISSING
ebas_flag_to_avoca[900] = QA_Flag.INVALIDATED_EXT

missing_flags = set(QA_Flag) - set(flags_to_ebas.keys())
if missing_flags:
    raise RuntimeError(
        f"Not all QA flags are mapped to Ebas flags. Missing: {missing_flags}"
    )


class DataLevel(IntEnum):
    """Values for different type of data used by ebas."""

    AREAS = 0
    CONCS = 1
    QA_CONCS = 2


def data_level_after_qa(data_level: DataLevel) -> DataLevel:
    """Return the data level after the QA."""
    if data_level == DataLevel.CONCS:
        return DataLevel.QA_CONCS
    return data_level


def set_dataframe(
    nas,
    df_export: pd.DataFrame,
    compounds: dict[str, str],
    data_level: DataLevel,
    start_offset: timedelta | None = None,
    end_offset: timedelta | None = None,
    flag_all: list[int] = [],
):
    """Put the data from the export dataframe into the nas object.

    :arg nas: The nas object to fill
    :arg df_export: The dataframe with the data to export. Format follows the
        other avoca format.
    :arg compounds: The dictionary with the compounds. The keys are the
        the names in df_export. Values are the names in ebas.
    :arg data_level: The level of the data to export.
    :arg start_offset: The offset to add to the start time
    :arg end_offset: The offset to add to the end time

    """

    if ("-", "start_datetime") not in df_export.columns:
        if start_offset is None:
            raise ValueError(
                "start_offset is required if start_datetime is not in df_export"
            )
        df_export[("-", "start_datetime")] = df_export.index + start_offset
    if ("-", "end_datetime") not in df_export.columns:
        if end_offset is None:
            raise ValueError(
                "end_offset is required if end_datetime is not in df_export"
            )
        df_export[("-", "end_datetime")] = df_export.index + end_offset

    nas.sample_times = [
        DatetimeInterval(start, end)
        for start, end in zip(
            df_export[("-", "start_datetime")],
            df_export[("-", "end_datetime")],
        )
    ]

    vars_to_export = {
        DataLevel.AREAS: ["area", "rt", "w"],
        DataLevel.CONCS: ["C"],
    }

    unit_of_var = {
        "C": "pmol/mol",
        "rt": "s",
        "w": "s",
        "area": "area_unit",
    }

    ebas_varname_of_var = {
        "rt": "rt",
        "w": "pw",
        "area": "pa",
    }

    ebas_compname_of_var = {
        "rt": "retention_time",
        "w": "peak_width",
        "area": "peak_area",
    }

    metadatas = {}
    for sub in compounds:
        flags = [
            sorted(flag_all + [flags_to_ebas[f] for f in QA_Flag if f in QA_Flag(flag)])
            for flag in df_export[(sub, "flag")]
        ]
        nan_flag = df_export[(sub, "flag")] & QA_Flag.MISSING.value
        for var in vars_to_export[data_level]:
            ebas_name = compounds[sub]
            serie_to_export = df_export[(sub, var)]
            if pd.isna(serie_to_export).all():
                # Ignore this compound
                continue
            values = [
                None if pd.isna(val) or isnan else val
                for val, isnan in zip(serie_to_export, nan_flag)
            ]

            metadata = DataObject()
            metadata.comp_name = (
                f"{ebas_name}_{ebas_compname_of_var[var]}"
                if var in ebas_compname_of_var
                else ebas_name
            )
            metadata.title = (
                f"{ebas_name}_{ebas_varname_of_var[var]}"
                if var in ebas_varname_of_var
                else ebas_name
            )
            metadata.unit = unit_of_var[var]

            # add the variable
            nas.variables.append(
                DataObject(values_=values, flags=flags, flagcol=True, metadata=metadata)
            )

            metadatas[sub] = metadata
    return metadatas


def get_last_written_nas_file(directory: Path) -> Path | None:
    """Return path to the last nas file."""

    # Find the last submited files the format is:
    last_file = None
    last_submision_time = None
    for file in directory.glob(f"*.nas"):
        try:
            time_str = file.name.split(".")[2]
            time = datetime.datetime.strptime(time_str, "%Y%m%d%H%M%S")
            if last_submision_time is None or time > last_submision_time:
                last_submision_time = time
                last_file = file
        except Exception as e:
            logger.warning(f"Could not parse time from {file}: {e}")

    return last_file


def get_data_level(nas: EbasNasaAmes) -> DataLevel:
    """Get the data level of the nas file."""
    data_level = nas.metadata["datalevel"]

    match data_level:
        case "1":
            return DataLevel.CONCS
        case "2":
            return DataLevel.QA_CONCS
        case "0":
            return DataLevel.AREAS
        case _:
            raise ValueError(f"Data level {data_level} not recognized")


def nas_to_avoca(nas: EbasNasaAmes) -> pd.DataFrame:
    """Convert the ebas file to a pandas dataframe for @voc@.

    To read the nas file, you can do:

    .. code-block:: python

        from ebas.io.file.nasa_ames import EbasNasaAmes

        file = "path/to/file.nas"
        nas = EbasNasaAmes()
        nas.read(file)
        df = nas_to_avoca(nas)


    Doing this will remove some specific flag information.
    In particular, @voc@ only accepts flags per compound and not per variable as in ebas.

    This for each compound, the flag collects all the compounds of the variables.

    @voc@ also requires a runtype for each run.
    We use for that the calibration flag suggested by ebas.
    We have to assume that this flag is the same for all compounds.
    """

    logger = logging.getLogger(__name__)
    clean_for_df = {}

    ebas_name_to_avoca = {
        "pa": "area",
        "pw": "w",
        "rt": "rt",
        "C": "C",
    }

    compounds = []

    for var in nas.variables:
        if "metadata" not in var:
            continue

        metadata = var["metadata"]
        if "comp_name" not in metadata:
            continue

        values = var["values_"]

        title = metadata["title"]

        # Split the title on the _

        title = title.split("_")

        if len(title) != 2:

            print("passing", title)
            continue

        compund, variable = title
        if compund not in compounds:
            compounds.append(compund)

        # Convert the variable name to the avoca format
        if variable not in ebas_name_to_avoca:
            raise ValueError(f"Variable {variable} not recognized")
        variable = ebas_name_to_avoca[variable]

        clean_for_df[(compund, variable)] = values

        flag_serie = pd.Series(
            [
                sum([ebas_flag_to_avoca[f].value for f in flag_row])
                for flag_row in var["flags"]
            ],
            dtype=int,
        )
        flag_col = (compund, "flag")
        if flag_col not in clean_for_df:
            clean_for_df[flag_col] = flag_serie
        else:
            clean_for_df[flag_col] |= flag_serie

    # Use the start of the intervals as the datetime (use 1 for the end)
    clean_for_df[("-", "datetime")] = [dt[0] for dt in nas.sample_times]
    clean_for_df[("-", "start_datetime")] = clean_for_df[("-", "datetime")]
    clean_for_df[("-", "end_datetime")] = [dt[1] for dt in nas.sample_times]

    is_calibration = {
        compound: (QA_Flag.CALIBRATION.value & clean_for_df[(compound, "flag")]).astype(
            bool
        )
        for compound in compounds
    }

    # Assert all the calibration flags are the same
    ref_calib = is_calibration[compounds[0]]
    for compound in compounds[1:]:
        mask_same = is_calibration[compounds[0]] == is_calibration[compound]
        if not np.all(mask_same):
            # Show the rows where not all have the same flag
            mask_different = ~mask_same
            logger.warning(
                f"Calibration flags are not the same for all compounds: {compound} "
                f"is different from reference compound {compounds[0]}"
                f"at rows {np.argwhere(mask_different).reshape(-1)}"
            )
            # Combine the calib in both samples
            ref_calib = ref_calib | is_calibration[compound]

    runtype = pd.Series(is_calibration[compounds[0]].map({True: "std", False: "air"}))
    clean_for_df[("-", "type")] = runtype

    return pd.DataFrame(clean_for_df).set_index(("-", "datetime"))


def read_ebas_csv(file: PathLike) -> pd.DataFrame:
    """Read the EBAS csv file and return a DataFrame.

    This format comes from other EBAS tools.
    """

    # Check if file is a dir or a file
    kwargs: dict[str, Any] = {"parse_dates": ["Start", "End"], "sep": ";"}
    file = Path(file)
    if file.is_dir():
        # Read all the csv files in the directory
        dfs: list[pd.DataFrame] = [pd.read_csv(f, **kwargs) for f in file.glob("*.csv")]
        df = pd.concat(dfs, axis="index")
    else:
        # Read the csv file
        df = pd.read_csv(file, **kwargs)

    # Read all the columns which are not time
    columns = [c for c in df.columns if c not in ["Start", "End"]]
    # Get the compounds names
    compounds = set(["-".join(c.split("-")[:-1]) for c in columns])
    # Check that for each compounds we have the 4 required parameters
    parameters = ["Value", "Precision", "Accuracy", "Flag"]
    expected_columns = [f"{c}-{p}" for c in compounds for p in parameters]
    missing_columns = [c for c in expected_columns if c not in columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")
    # Make it a multiindex dataframe
    df = df.set_index("Start")
    # Get the values for each compound
    df_out = pd.DataFrame(
        columns=pd.MultiIndex.from_product([compounds, ["C", "flag"]])
    )
    flags = {
        0.999: QA_Flag.MISSING.value,
        0.559: QA_Flag.EXTREME_VALUE.value,
        0.147: QA_Flag.BELOW_DETECTION_LIMIT.value,
        0.000: 0,  # Valid
    }
    for c in compounds:
        df_out[(c, "C")] = df[f"{c}-Value"]
        df_out[(c, "flag")] = int(0)
        # Assigne the flag
        df_out[(c, "flag")] |= df[f"{c}-Flag"].apply(lambda x: flags[x])
        # Set values to nan when flagged missing
        # df_out.loc[(df_out[(c, 'flag')] & (QA_Flag.MISSING.value | QA_Flag.BELOW_DETECTION_LIMIT.value)) != 0, (c, 'C')] = np.nan
        df_out.loc[df_out[(c, "flag")] != 0, (c, "C")] = np.nan

    df_out[("-", "type")] = "air"

    return df_out


def extract_concentration_field(text: str) -> dict[str, float]:
    """Extract the concentrations from the text.

    This is a temporary solution that we found to communicate the concentrations
    of the standards thgrough the nas files.
    """
    # Define the regular expression pattern to match the concentrations field
    concentration_pattern = r"Concentrations:\s*\{([^}]*)\}"
    # Search for the concentration field in the text
    concentration_match = re.search(concentration_pattern, text)
    if concentration_match:
        # Extract the concentration substring
        concentration_substring = concentration_match.group(1)
        # Split the substring by comma to separate individual concentrations
        concentration_list = concentration_substring.split(",")
        # Initialize an empty dictionary to store concentrations
        concentrations = {}
        for concentration in concentration_list:
            # Split each concentration by '=' to separate compound and value
            compound, value = concentration.split("=")
            # Remove leading and trailing whitespaces
            compound = compound.strip()
            value = float(value.strip())  # Convert value to float
            concentrations[compound] = value
        return concentrations
    else:
        return {}
