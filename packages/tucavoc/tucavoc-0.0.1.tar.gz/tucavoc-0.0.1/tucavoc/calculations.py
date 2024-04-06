from datetime import timedelta
import logging
from warnings import warn
import pandas as pd
import numpy as np
from warnings import simplefilter
from tucavoc.flags import set_flags, set_group_flags


from tucavoc.uncertainties import (
    Calibration,
    FurtherInstrumentalProblems,
    PeakIntegration,
    Linearity,
    Precision,
    Sampling,
    Volume,
)
from tucavoc.abstract_uncertainty import Uncertainty

from tucavoc.plots import (
    plot_calibration_areas,
    plot_calibration_concs,
    plot_uncertainties,
    plot_uncertainties_err_bars,
    plot_uncertainties_parts,
)


def get_groups_dict(df_subs: pd.DataFrame) -> dict[str, list[str]]:
    """Get the substances and their group.

    :return groups_dict: A dictionary where keys are group names and
        values are lists of subtances names.

        For example

        .. code-block::

            {
                '': ['methane', 'isobutane'];
                'my_group': ['nice_sub', 'other_sub', 'another_one']
            }

    """
    return {
        group_name: df_subs.loc[df_subs["group"] == group_name].index.to_list()
        for group_name in np.unique(df_subs["group"])
        if group_name
    }


def check_data_for_calculations(
    df_calc: pd.DataFrame,
    df_subs: pd.DataFrame,
) -> list[str]:
    """Check that the data for the calculations is correct.

    Possible Problems:

        * Group name is the same as a substance name.
        * No substance is in the calibration in a group.

    :return list_of_problems: String explaining what the problem is.
        If empty list, no problems were found.
    """
    list_of_problems = []
    substances = list(df_subs.index.values)
    groups_dict = get_groups_dict(df_subs)

    for group_name, group_members in groups_dict.items():
        if group_name in substances:
            list_of_problems.append(
                f"Group '{group_name}' is already used for the name of "
                "a substance in your data."
            )

        # Commented: because we will use a general crf for these substances
        # if all((not df_subs.loc[sub, "in_calib"] for sub in group_members)):
        #    list_of_problems.append(
        #        f"Group '{group_name}' has only substances that are not in "
        #        "the calibration."
        #    )

    if any((not df_subs.loc[sub, "in_calib"] for sub in substances)):
        if not any(
            (df_subs.loc[sub, "use_for_general_crf"] for sub in substances)
        ):
            # If we have some substance not in the calib and we dont have
            # substances for a general crf, we must check that all the non calib
            # substances are in groups
            for group_name, group_members in groups_dict.items():
                if not any(
                    (df_subs.loc[sub, "in_calib"] for sub in group_members)
                ):
                    list_of_problems.append(
                        "No substance is in the general mean CRF, and"
                        f" '{group_name}' has no calibration substances to"
                        " calculate a group mean CRF."
                    )

            # Check that substances not in any group are all in calib
            if any(
                (not df_subs.loc[sub, "in_calib"] for sub in groups_dict[""])
            ) and all(
                (
                    not df_subs.loc[sub, "use_for_general_crf"]
                    for sub in substances
                )
            ):
                list_of_problems.append(
                    f"No substance is in the General mean CRF, and some"
                    f" substance belonging to no groups need to have a general"
                    f" CRF but no calibration substances were set be used in"
                    f" the General CRF."
                )

    return list_of_problems


def main(
    df_calc: pd.DataFrame,
    df_subs: pd.DataFrame,
    uncertainties: list[Uncertainty] = [],
    blanks_in_df_subs: bool = False,
    calib_type="std",
    blank_type="blank",
    ignore_n_first_blanks: int = 0,
    zero_min: bool = True,
    debug: bool = False,
    calibration_sustances: list[str] = [],
    interpolate: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Main calculations.

    :arg df_calc: The dataframe containing the area of the substances
        for which we want to calculate the concentration.
    :arg df_subs: The dataframe containing information on each substances.
        size: substances * parameters
        the parameters required are the name of the parameters in the
        documentation. see :ref:`parameters_glossary` .
    :arg uncertainties: A list of uncertainties to calculate.
        One can choose which one they want.
    :arg blanks_in_df_subs: Whether the blank area to use is a constant
        from df_subs. See :term:`blank_conc_preset` , that should then
        be present in the `df_subs` .
    :arg calib_type: The name in the 'type' column of df_calc that
        corresponds to the calibration runs.
    :arg blank_type: The name in the 'type' column of df_calc that
        corresponds to the blank runs.
    :arg ignore_n_first_blanks: The number of blanks runs to ignore at the
        start of a set of blank runs.
    :arg zero_min: Whether zero should be used as a min value
        in case negative are calculated (clipping).
    :arg debug: Whether to add debug information to the dfs.
    :arg calibration_sustances: The list of substances to use in the calibration
        to calculate the CRF.
        If not given, all substances will be used.
    :arg interpolate: Whether to interpolate the calibration and blank data.

    """
    # Ignore these warnings
    simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
    substances = list(df_subs.index.values)

    # Find which substrances are used for the calibraiton
    calib_substances = calibration_sustances or substances
    substances_not_in_calib = [
        sub for sub in substances if sub not in calib_substances
    ]
    # Find how groups are constituted
    groups_dict = get_groups_dict(df_subs)

    # 1. find the calibrations values
    # This will add
    df_calib = make_calibration(
        df_calc,
        calib_substances,
        calib_type=calib_type,
        debug=debug,
        interpolate=interpolate,
    )

    # 2. find blank data
    if blanks_in_df_subs:
        df_calc["is_blank"] = False
        subs_blank_from_data = []
        # Assign the blanks from the df_subs
        for sub in substances:
            if pd.isna(df_subs.loc[sub, "blank_conc_preset"]):
                # None values mean that we need to read from the data
                subs_blank_from_data.append(sub)
                continue
            if sub in calib_substances:
                # Do now for calib substances, as FID substances are handled later
                # Retreive the area using the BLANK_AREA_FROM_CONC equation
                df_calc[(sub, "area_blank")] = (
                    df_calc[(sub, "area_calib")]
                    * df_subs.loc[sub, "blank_conc_preset"]
                    / (
                        df_subs.loc[sub, "blank_conc_preset"]
                        + df_subs.loc[sub, "conc_calib"]
                        * df_subs.loc[sub, "volume_calib"]
                        / df_subs.loc[sub, "volume_sample"]
                    )
                )
    else:
        # All substance must be read from the data
        subs_blank_from_data = substances

    if subs_blank_from_data:
        # Read the blanks from the data
        # finding the blank averages is the same as finding the calibration
        # averages but using blank data
        df_calib = make_calibration(
            df_calc,
            subs_blank_from_data,
            calib_type=blank_type,
            calib_name="blank",
            ignore_n_first=ignore_n_first_blanks,
            debug=debug,
            interpolate=interpolate,
        )

    # 3. calculate the calibration factor
    # ml * pmol/mol / area = ml * pmol/mol / area
    for sub in calib_substances:
        df_calc[(sub, "calib_factor")] = (
            df_subs.loc[sub, "volume_calib"]
            * df_subs.loc[sub, "conc_calib"]
            / (df_calc[(sub, "area_calib")] - df_calc[(sub, "area_blank")])
        )
        # Also calucalte the calibraiton error
        df_calc[(sub, "rel_std_area_cal_series")] = (
            df_calc[(sub, "area_std_calib")] / df_calc[(sub, "area_calib")]
        )

    # 4. calculate the concentration of the samples using the simple formula
    # area * (ml * pmol/mol / area) / ml = pmol/mol
    for sub in calib_substances:
        df_calc[(sub, "conc")] = (
            (df_calc[(sub, "area")] - df_calc[(sub, "area_blank")])
            * df_calc[(sub, "calib_factor")]
            / df_subs.loc[sub, "volume_sample"]
        )

    # 4.b Calculate the concentration of the samples using the FID formula
    if substances_not_in_calib:
        for sub in calib_substances:
            df_calc[(sub, "carbon_response_factor")] = 1.0 / (
                df_calc[(sub, "calib_factor")]
                * df_subs.loc[sub, "carbon_number"]
                * df_subs.loc[sub, "effective_carbon_number_contribution"]
            )

        # Get substances used to compute the general mean crf
        general_crf_substances = [
            sub
            for sub in calib_substances
            if df_subs.loc[sub, "use_for_general_crf"]
        ]

        # Calculate a general mean CRF
        df_calc[("-", "general_mean_carbon_response_factor")] = df_calc[
            [(sub, "carbon_response_factor") for sub in general_crf_substances]
        ].mean(axis=1)

        # The general error on the calibration
        df_calc[("-", "general_rel_std_area_cal_series")] = (
            df_calc[
                [
                    (sub, "rel_std_area_cal_series")
                    for sub in general_crf_substances
                ]
            ]
            .pow(2)
            .sum(axis=1)
            .pow(0.5)
            .divide(len(general_crf_substances))
        )
        # Calculate the mean carbon response factor of each group
        for group_name, group_members in groups_dict.items():
            # Find the calibration group substances
            group_calib_substances = [
                sub for sub in group_members if sub in calib_substances
            ]
            # If the group has some substance and the group is not the default
            if group_calib_substances and group_name != "":
                # Mean CRF of the group
                df_calc[(group_name, "mean_carbon_response_factor")] = df_calc[
                    [
                        (sub, "carbon_response_factor")
                        for sub in group_calib_substances
                    ]
                ].mean(axis=1)
                # Error on the calibration of the group uses the std of the
                # calibration substances in the group
                # (same one used for the crf calculation)
                df_calc[(group_name, "rel_std_area_cal_series")] = (
                    df_calc[
                        [
                            (sub, "rel_std_area_cal_series")
                            for sub in group_calib_substances
                        ]
                    ]
                    .pow(2)
                    .sum(axis=1)
                    .pow(0.5)
                    .divide(len(group_calib_substances))
                )
            else:
                # Use the general crf of all supstances
                # if there are no calibrated substance in this group
                df_calc[(group_name, "mean_carbon_response_factor")] = df_calc[
                    ("-", "general_mean_carbon_response_factor")
                ]
                df_calc[(group_name, "rel_std_area_cal_series")] = df_calc[
                    ("-", "general_rel_std_area_cal_series")
                ]

        for sub in substances_not_in_calib:
            # Get the name of the group
            # Substances with no group will be empty sting : ""
            group_of_sub = df_subs.loc[sub, "group"]
            # Choose the mean crf of the group if the sub is in a group
            mean_crf = (
                df_calc[(group_of_sub, "mean_carbon_response_factor")]
                if group_of_sub
                else df_calc[("-", "general_mean_carbon_response_factor")]
            )
            if blanks_in_df_subs and sub not in subs_blank_from_data:
                # Retreive the blank area using the BLANK_AREA_FROM_CONC_FID equation
                df_calc[(sub, "area_blank")] = (
                    df_subs.loc[sub, "blank_conc_preset"]
                    * df_subs.loc[sub, "volume_sample"]
                    * df_subs.loc[sub, "carbon_number"]
                    * df_subs.loc[sub, "effective_carbon_number_contribution"]
                    * mean_crf
                )
            # Apply the concentration using crf equation
            df_calc[(sub, "conc")] = (
                df_calc[(sub, "area")] - df_calc[(sub, "area_blank")]
            ) / (
                df_subs.loc[sub, "volume_sample"]
                * df_subs.loc[sub, "carbon_number"]
                * df_subs.loc[sub, "effective_carbon_number_contribution"]
                * mean_crf
            )
            # Add the error on the calibration, which comes now from computing the crf (see above)
            df_calc[(sub, "rel_std_area_cal_series")] = (
                df_calc[(group_of_sub, "rel_std_area_cal_series")]
                if group_of_sub
                else df_calc[("-", "general_rel_std_area_cal_series")]
            )

    # 4.c Set to zero the negative values
    if zero_min:
        for sub in substances:
            col = (sub, "conc")
            df_calc.loc[df_calc[col] < 0, col] = 0

    # 5. calculate the uncertainties
    for u in uncertainties:
        for sub in substances:
            match u:
                case Precision():
                    df_calc[(sub, f"u_{u.name}")] = u.calculate(
                        df_calc[(sub, "conc")],
                        df_calc[(sub, "rel_std_area_cal_series")],
                        df_subs.loc[(sub, "detection_limit")],
                    )
                case Calibration():
                    df_calc[(sub, f"u_{u.name}")] = u.calculate(
                        df_calc[(sub, "conc")],
                        df_subs.loc[sub, "conc_calib"],
                        df_subs.loc[sub, "abs_u_cal"],
                    )
                    # TODO: remove this temporary correction
                    # It is dued to CRF, not having their uncertainty
                    # formula calculated yet
                    mask_inf = df_calc[(sub, f"u_{u.name}")] == np.inf
                    mask_conc_0 = df_calc[(sub, "conc")] == 0.0
                    df_calc.loc[
                        mask_inf | mask_conc_0, (sub, f"u_{u.name}")
                    ] = 0.0
                case PeakIntegration():
                    if sub in calib_substances:
                        df_calc[(sub, f"u_{u.name}")] = u.calculate(
                            df_calc[(sub, "calib_factor")],
                            df_subs.loc[sub, "volume_calib"],
                            df_subs.loc[sub, "conc_calib"],
                            df_calc[(sub, "area_calib")],
                            df_calc[(sub, "area")],
                            df_subs.loc[sub, "volume_sample"],
                            df_subs.loc[sub, "u_peak_area_integ_sample"],
                            df_subs.loc[sub, "u_peak_area_integ_calib"],
                        )
                    else:
                        df_calc[(sub, f"u_{u.name}")] = 0
                        warn(
                            "PeakIntegration Uncertainty not implemented for"
                            " substances wihtout calibrant."
                        )
                case Volume():
                    df_calc[(sub, f"u_{u.name}")] = u.calculate(
                        df_calc[(sub, "conc")],
                        df_subs.loc[sub, "volume_sample"],
                        df_subs.loc[sub, "volume_calib"],
                        df_subs.loc[sub, "volume_uncertainty_sample"],
                        df_subs.loc[sub, "volume_uncertainty_calib"],
                    )
                case FurtherInstrumentalProblems():
                    df_calc[(sub, f"u_{u.name}")] = u.calculate(
                        df_calc[(sub, "conc")],
                        df_subs.loc[sub, "error_systematic_instrument"],
                    )
                case Linearity():
                    df_calc[(sub, f"u_{u.name}")] = u.calculate(
                        df_subs.loc[sub, "uncertainty_due_to_linearity"],
                    )
                case Sampling():
                    df_calc[(sub, f"u_{u.name}")] = u.calculate(
                        df_subs.loc[
                            sub, "uncertainty_sampling_volume_accuracy"
                        ],
                    )

                case _:
                    raise NotImplementedError(u)

    # 7. calculate the concentration and uncertainties of the groups
    for group_name, group_members in groups_dict.items():
        # This will return all the columns of the attribute for each group member
        group_attr = lambda attr: [(sub, attr) for sub in group_members]
        df_calc[(group_name, "conc")] = df_calc[group_attr("conc")].sum(axis=1)

        # When any of the group members is invalid, the group is invalid
        mask_invalid = df_calc[group_attr("conc")].isnull().any(axis=1)
        df_calc.loc[mask_invalid, (group_name, "conc")] = np.nan

        # For the uncertainties, we use the propagation of uncertainties formula
        for u in uncertainties:
            df_calc[(group_name, f"u_{u.name}")] = (
                df_calc[group_attr(f"u_{u.name}")].pow(2).sum(axis=1).pow(0.5)
            )

    # 8. calculate the total and expanded uncertatinties
    for sub in substances + list(groups_dict.keys()):
        u_s_2 = df_calc[[(sub, f"u_{u.name}") for u in uncertainties]] ** 2
        df_calc[(sub, "u_combined")] = np.sqrt(u_s_2.sum(axis="columns"))
        df_calc[(sub, "u_expanded")] = 2 * df_calc[(sub, "u_combined")]

        # 8.b caculate the relative uncertainties
        df_calc[(sub, "u_rel_combined")] = (
            df_calc[(sub, "u_combined")] / df_calc[(sub, "conc")]
        )
        df_calc[(sub, "u_rel_expanded")] = (
            df_calc[(sub, "u_expanded")] / df_calc[(sub, "conc")]
        )
        # Note: they should be in % as defined in doc, but here we don't
        #       do convert and keep them as fraction, only in export they
        #       are converted to %
        # Put nan in the uncertainty where the
        mask_conc_0 = df_calc[(sub, "conc")] == 0.0
        df_calc.loc[mask_conc_0, (sub, "u_rel_combined")] = np.nan
        df_calc.loc[mask_conc_0, (sub, "u_rel_expanded")] = np.nan

    # 9. Calculate the part of the uncertainties in the total uncertainty
    for u in uncertainties:
        for sub in substances:
            # Simply take the ratio
            df_calc[(sub, f"ratio_u_{u.name}_in_u_combined")] = (
                df_calc[(sub, f"u_{u.name}")] / df_calc[(sub, "u_combined")]
            )

    # 10. Adding the flags
    set_flags(df_calc, df_subs)
    set_group_flags(df_calc, df_subs, groups_dict)

    return df_calc, df_calib


def make_calibration(
    df_calc: pd.DataFrame,
    substances: list[str],
    calib_type="std",
    calib_name="calib",
    ignore_n_first: int = 0,
    interpolate: bool = True,
    debug: bool = False,
):
    """Calculate the data for calibration.

    This will look for the `calib_type` in the `df_calc` using the column
    `("-", "type")`.
    The samples which are from the same type
    and that were measured successively
    will be groupped together in
    a "calibration" which has mean and std.
    Columns are added to the `df_calc`:

    Two colums per substances :

    1. (sub,"{calib_name}_area")

        The calibration area of the substance

    2. (sub,"{calib_name}_area_std")

        The standard deviation of calibration area of the substance

    3. (sub,"{calib_name}_used")

        Wheter the value was used to compute the calibration
        Some outliers or nan or zero values will be ignored.


    And one global

    1. "is_{calib_name}"

        A Mask for the lines used for calibration.

    where `calib_name` is an argument of this function (default calib)
    and sub is the name of the substance.
    This means that every sample will have a calibration value.

    The substances that must be processed can be selected by the
    :py:arg:`substances`.

    For all the other run, to find the corresponding calibration value,
    we use a time interpolation between the previous and next samples.
    This means for example that if :math:`t_{meas}` is the time of the
    measurment and :math:`t_{prev}`, :math:`t_{next}` are the times of
    respectively the previous and next calibration, and :math:`v_{...}` are
    the values measured at each of these times, the calibration value
    for the measurement :math:`c_{meas}` will be equal to

    :math:`v_{prev} * (t_{meas} - t_{prev}) / (t_{next} - t_{prev}) + v_{next} * (t_{next} - t_{meas}) / (t_{next} - t_{prev})`

    This assumes that the device was linearly shifted from on mean value
    to another.

    :arg ignore_n_first: The number of first runs that should be ignored during
        the calibration.
    :arg interpolate: Whether to interpolate the values between the calibrations
        If not, the previous calibration value will be used.

    """

    if calib_name in ["std"]:
        raise ValueError(f"Cannot use {calib_name=}")

    mask_calib = df_calc[("-", "type")] == calib_type
    # Add a column that retrives this info
    df_calc[f"is_{calib_name}"] = False

    # Exctract the standard runs values
    # Batches of  few runs in a row
    indexes_calib = np.where(mask_calib)[0]
    indexes_calib_batches_start = indexes_calib[
        ~np.isin(indexes_calib - 1, indexes_calib)
    ]
    indexes_calib_batches_end = indexes_calib[
        ~np.isin(indexes_calib + 1, indexes_calib)
    ]

    # Ignore the first indexes
    indexes_calib_batches_start += ignore_n_first
    if np.any(indexes_calib_batches_start > indexes_calib_batches_end):
        raise RuntimeError(
            f"The number of ignored first samples {ignore_n_first} is to large"
            f" for the calibration of the '{calib_type=}' using"
            f" '{calib_name=}'."
        )

    # Create all the columns for the calibration and the df
    subs_areas = [(sub, "area") for sub in substances]
    subs_area_std = [(sub, "area_std") for sub in substances]
    df_calib = pd.DataFrame(
        columns=["datetime"] + subs_areas + subs_area_std,
    )

    # Iterate over the std battches to compute the means and std
    for start, end in zip(
        indexes_calib_batches_start, indexes_calib_batches_end
    ):
        df_calc.loc[start:end, f"is_{calib_name}"] = True
        df_this_calib = df_calc.loc[start:end, subs_areas]

        # Calculate mean and std
        mean_values = df_this_calib.mean(axis="index")
        std_values = df_this_calib.std(axis="index").rename(
            {"area": "area_std"}
        )
        df_calib.loc[start] = mean_values
        df_calib.loc[end] = mean_values
        df_calib.loc[start, subs_area_std] = std_values
        df_calib.loc[end, subs_area_std] = std_values

    # Finds out the indexes where the calibration occured
    indexes_calib = np.sort(
        np.concatenate(
            [indexes_calib_batches_start, indexes_calib_batches_end]
        )
    )
    # Add datetime info
    df_calib.loc[indexes_calib, "datetime"] = df_calc.loc[
        indexes_calib, "datetime"
    ]

    # Add calib info
    df_calc[f"previous_{calib_name}"] = indexes_calib[
        np.maximum(
            np.searchsorted(indexes_calib, df_calc.index, side="right") - 1,
            0,
        )
    ]
    df_calc[f"next_{calib_name}"] = indexes_calib[
        np.minimum(
            np.searchsorted(indexes_calib, df_calc.index, side="left"),
            len(indexes_calib) - 1,
        )
    ]

    sample_dt = df_calc["datetime"].to_numpy()
    previous_calib_time = sample_dt[
        df_calc[f"previous_{calib_name}"].to_numpy()
    ]
    next_calib_time = sample_dt[df_calc[f"next_{calib_name}"].to_numpy()]
    # Find the timedeltas to the other calibrations
    previous_td = np.maximum(
        sample_dt - previous_calib_time, np.timedelta64(0)
    )
    next_td = np.maximum(next_calib_time - sample_dt, np.timedelta64(0))

    # Find the weigths
    # Remove 0 values
    mask_0 = previous_td == next_td
    next_td[mask_0] = np.timedelta64(timedelta(seconds=1))
    total = previous_td + next_td
    # previous and next weights
    previous_w = previous_td / total
    next_w = next_td / total

    if debug:
        df_calc[f"previous_{calib_name}_time"] = previous_calib_time
        df_calc[f"next_{calib_name}_time"] = next_calib_time
        df_calc["previous_td"] = previous_td
        df_calc["next_td"] = next_td
        df_calc["previous_w"] = previous_w
        df_calc["next_w"] = next_w

    # Set the calibration values in the df

    #    for sub in substances:
    #        df_calc[(sub, f"{calib_name}_area")] = df_calib[(sub, "area")]
    #        df_calc[(sub, f"{calib_name}_area_std2")] = (
    #            df_calib[(sub, "area_std")] ** 2
    #        )

    df_calc[[(sub, f"area_{calib_name}") for sub in substances]] = df_calib[
        [(sub, "area") for sub in substances]
    ]
    df_calc[[(sub, f"area_std2_{calib_name}") for sub in substances]] = (
        df_calib[[(sub, "area_std") for sub in substances]] ** 2
    )

    df_calc["row_index"] = df_calc.index

    df_calc.set_index("datetime", inplace=True)
    for sub in substances:
        if not interpolate:
            # Use the previous value as calibration value
            df_calc[(sub, f"area_{calib_name}")].interpolate(
                method="pad", inplace=True, limit_direction="forward"
            )
            df_calc[(sub, f"area_std2_{calib_name}")].interpolate(
                method="pad", inplace=True, limit_direction="forward"
            )
            # The first values will be have the first calibration value
            # From the intepolation below

        # Interpolate the values according to the time weights
        df_calc[(sub, f"area_{calib_name}")].interpolate(
            method="time", inplace=True, limit_direction="both"
        )
        df_calc[(sub, f"area_std2_{calib_name}")].interpolate(
            method="time", inplace=True, limit_direction="both"
        )

        df_calc[(sub, f"area_std_{calib_name}")] = np.sqrt(
            df_calc[(sub, f"area_std2_{calib_name}")]
        )
    df_calc["datetime"] = df_calc.index
    df_calc.set_index("row_index", inplace=True)

    return df_calib


# %%
if __name__ == "__main__":
    from tucavoc import read_gcwerks

    df_calc = read_gcwerks(
        r"C:\Users\coli\Documents\ovoc-calculations\data\TestData.dat"
    )

    substances = [
        sub
        for sub, _ in df_calc.columns
        if sub not in ["-", "datetime", "datetime_start", "datetime_end"]
    ]

    df_subs = pd.DataFrame(
        columns=["volume_calib", "conc_calib"], index=substances
    )

    df_subs["volume_calib"] = 600
    df_subs["volume_sample"] = 600
    df_subs["detection_limit"] = 10
    df_subs["volume_uncertainty_sample"] = 20
    df_subs["volume_uncertainty_calib"] = 20
    df_subs["error_systematic_instrument"] = 1.0
    df_subs["uncertainty_due_to_linearity"] = 0.0
    df_subs["uncertainty_sampling_volume_accuracy"] = 0.0
    df_subs["u_peak_area_integ_sample"] = 2.0
    df_subs["u_peak_area_integ_calib"] = 2.0
    df_subs["conc_calib"] = 4000
    df_subs["abs_u_cal"] = 1.0
    df_subs["carbon_number"] = 2.0
    df_subs["effective_carbon_number_contribution"] = 1.0
    df_subs["use_for_general_crf"] = True
    df_subs["blank_conc_preset"] = 0.0

    df_subs["group"] = ""

    uncs = [
        Precision(),
        Calibration(),
        PeakIntegration(),
        Volume(),
        FurtherInstrumentalProblems(),
        Linearity(),
        Sampling(),
    ]
    main(
        df_calc,
        df_subs,
        uncertainties=uncs,
        debug=True,
        blanks_in_df_subs=True,
        calibration_sustances=substances[1:3],
        interpolate=False,
    )
    # print(df_calc.loc[505:520])
    # print(df_calc.loc[1285:1295])
    # print(df_calc.loc[2624:2632])
    # print(df_calc.columns)

    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 1, sharex=True)

    name = "ethane"
    # name = "methane"
    plot_calibration_areas(axes[0], name, df_calc, df_subs)
    plot_uncertainties(
        axes[1], name, uncs, df_calc[~df_calc["is_calib"]], df_subs
    )
    plot_uncertainties_parts(
        axes[2], name, uncs, df_calc[~df_calc["is_calib"]], df_subs
    )
    # plot_uncertainties_err_bars(axes[1], name, uncs, df_calc, df_subs)

    plt.show()

# %%
