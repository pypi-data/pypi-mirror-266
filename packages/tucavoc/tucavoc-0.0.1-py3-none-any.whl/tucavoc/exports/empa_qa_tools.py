"""Few modules for importing and exporting from https://voc-qc.nilu.no/

Note that the export and import functions are the opposite of the
import/export feature from the website.
(We export data from this programm, which is imported to the site.)
(We import data into this programm, which was exported from the site.)
"""
from datetime import datetime
import logging
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import pandas.errors


from tucavoc.additional_data import AdditionalData
from tucavoc.additional_data.station import StationInformation

from tucavoc.flags import Flags


def number_of_digits_required(serie: pd.Series) -> int:
    """Return the number of digits required for the calculation"""
    # TODO: need to check if we need the actual int  value, we can put a .9 at the end
    if all(pd.isna(serie) | (serie == 0)):
        # Only 2 will be required
        return 2
    else:
        number_of_digits = np.log10(serie[serie > 0])
        max_digits = number_of_digits[number_of_digits != np.inf]
        if len(max_digits) == 0:
            return 2
        return int(np.max(max_digits) + 2)


def export_EmpaQATool(
    df: pd.DataFrame,
    df_substances: pd.DataFrame,
    export_file: Path,
    additional_data: dict[type, AdditionalData] = {},
):
    """Export to the EmpaQATool format.

    The exported file from the program can then be imported to
    the tool on https://voc-qc.nilu.no/Import
    The specs fro that file can be found in
    https://voc-qc.nilu.no/doc/CSVImport_FormatSpecifications.pdf

    This will add the additional data from the dataframe.

    :arg df: Calculation dataframe

    """
    warnings.filterwarnings(
        action="ignore",
        category=pandas.errors.PerformanceWarning,
        module="pandas",
    )

    df_out = pd.DataFrame()
    # fmt = "%Y-%m-%d %H:%M:%S"
    fmt = "%d.%m.%Y %H:%M:%S"
    df_out["start"] = df[("StartEndOffsets", "datetime_start")].dt.strftime(
        fmt
    )
    df_out["end"] = df[("StartEndOffsets", "datetime_end")].dt.strftime(fmt)
    substances = df_substances.index.to_list()
    for substance in substances:
        mask_invalid = (
            df[(substance, "flag")]
            == Flags.MISSING_MEASUREMENT_UNSPECIFED_REASON
        )
        # Convert to str so we can control the formatting
        df_out[f"{substance}-Value"] = (
            df[(substance, "conc")].copy().astype(str)
        )

        # Input the missing values as 9. see issue #7 gitlab.empa.ch
        df_out.loc[
            mask_invalid, f"{substance}-Value"
        ] = "9" * number_of_digits_required(df[(substance, "conc")])

        # Convert to str so we can control the formatting
        df_out[f"{substance}-Accuracy"] = df[(substance, "u_expanded")].astype(
            str
        )
        # Input the missing values as 9. see issue #7 gitlab.empa.ch
        df_out.loc[
            mask_invalid, f"{substance}-Accuracy"
        ] = "9" * number_of_digits_required(df[(substance, "u_expanded")])

        # Convert to str so we can control the formatting
        df_out[f"{substance}-Precision"] = df[
            (substance, "u_precision")
        ].astype(str)

        # Input the missing values as 9. see issue #7 gitlab.empa.ch
        df_out.loc[
            mask_invalid, f"{substance}-Precision"
        ] = "9" * number_of_digits_required(df[(substance, "u_precision")])

        df_out[f"{substance}-Flag"] = df[(substance, "flag")] / 1000.0

    addition_data_columns = [
        (data_source, col)
        for data_source, col in df.columns
        if data_source not in substances + ["-", "StartEndOffsets"]
    ]

    # Add the additional data
    for data_source, col in addition_data_columns:
        df_out[col + "-Value"] = df[(data_source, col)]

    export_file.mkdir(exist_ok=True)

    if StationInformation in additional_data:
        station_info: StationInformation = additional_data[StationInformation]
        station = station_info.get_station()

        abbreviation = station.abbreviation

    else:
        logging.warning(
            "No station information found, using default values. "
            "This might not be correct."
        )
        abbreviation = "XXX"
    # [station]_[dataset]_[revision]
    file_name = (
        f"{abbreviation}_{df[('StartEndOffsets', 'datetime_start')].iloc[0]:%Y%m%d}_{datetime.now():%Y%m%d}"
    )
    df_out.to_csv(
        Path(export_file, file_name).with_suffix(".csv"),
        sep=";",
        index=False,
        encoding="utf-8",
    )
