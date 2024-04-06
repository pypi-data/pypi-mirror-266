"""Flagging in TUCAVOC.

TUCAVOC add a flag value for each measurement of each substance.

"""
from enum import IntEnum
import pandas as pd

try:
    import enum_tools.documentation

    dec = enum_tools.documentation.document_enum
except ImportError as ie:
    # Basic decorator
    def dec(original_class):
        return original_class


# This enum is documented using enum_tools
# this implies that line comments will be present in the documentation
@dec
class Flags(IntEnum):
    """Flags supported by TUCAVOC.

    They are based on https://projects.nilu.no/ccc/flags/flags.html .

    """

    #: Valid measurement
    VALID = 0
    #: Below theoretical detection limit or formal Q/A limit, but a value has been measured and reported and is considered valid
    BELOW_DETECTION_LIMIT = 147
    #: Unspecified contamination or local influence, but considered valid
    UNSPECIFIED_LOCAL_CONTAMINATION = 559
    #: Missing measurement, unspecified reason
    MISSING_MEASUREMENT_UNSPECIFED_REASON = 999


def set_flags(df: pd.DataFrame, df_substances: pd.DataFrame):
    """Set automatic flags to the dataframe.

    This will add a sub column to all the substances based on
    automatic recognition of the data.

    * :py:enum:mem:`Flags.VALID` by default for any measurement
    * :py:enum:mem:`Flags.MISSING_MEASUREMENT_UNSPECIFED_REASON` if
        the amount fraction value is nan.
        This is the case when the base value was nan.
    * :py:enum:mem:`Flags.BELOW_DETECTION_LIMIT` if :term:`conc` is
        below the :term:`detection_limit` or is smaller than
        :term:`u_precision` / 3

    """

    for sub in df_substances.index:
        df[(sub, "flag")] = Flags.VALID

        # Value samller than detection limit or not precise enough,
        # = below detection limit
        if (sub, "detection_limit") in df:
            df.loc[
                (df[(sub, "conc")] < df[(sub, "detection_limit")]),
                (sub, "flag"),
            ] = Flags.BELOW_DETECTION_LIMIT

        if (sub, "u_precision") in df:
            df.loc[
                (df[(sub, "conc")] < 3 * df[(sub, "u_precision")]),
                (sub, "flag"),
            ] = Flags.BELOW_DETECTION_LIMIT

        # Invalid when is nan
        df.loc[
            pd.isna(df[(sub, "conc")]),
            (sub, "flag"),
        ] = Flags.MISSING_MEASUREMENT_UNSPECIFED_REASON


def set_group_flags(
    df: pd.DataFrame,
    df_substances: pd.DataFrame,
    group_dict: dict[str, list[str]],
):
    """Set flags for the groups.

    Similar to :py:func:`set_flags` but adapted for groups.

    * :py:enum:mem:`Flags.VALID` by default for any measurement
    * :py:enum:mem:`Flags.MISSING_MEASUREMENT_UNSPECIFED_REASON` if
        the amount fraction value is nan.
        This is the case when the base value was nan.

    """

    for group in group_dict.keys():
        df[(group, "flag")] = Flags.VALID

        # Invalid when is nan
        df.loc[
            pd.isna(df[(group, "conc")]),
            (group, "flag"),
        ] = Flags.MISSING_MEASUREMENT_UNSPECIFED_REASON
