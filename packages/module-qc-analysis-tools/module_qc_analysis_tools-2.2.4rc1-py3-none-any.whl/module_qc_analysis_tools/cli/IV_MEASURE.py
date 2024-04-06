from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import typer
from module_qc_data_tools import (
    get_layer_from_sn,
    load_json,
    outputDataFrame,
    qcDataFrame,
    save_dict_list,
)
from scipy import constants

from module_qc_analysis_tools import __version__
from module_qc_analysis_tools.cli.globals import (
    CONTEXT_SETTINGS,
    OPTIONS,
    LogLevel,
)
from module_qc_analysis_tools.utils.analysis import check_layer
from module_qc_analysis_tools.utils.misc import (
    JsonChecker,
    bcolors,
    convert_prefix,
    get_inputs,
    get_time_stamp,
    guess_prefix,
)

log = logging.getLogger("analysis")

app = typer.Typer(context_settings=CONTEXT_SETTINGS)


def coth(x):
    return np.cosh(x) / np.sinh(x)


def normalise_current(current, temp):
    T1 = temp + 273.15  ## measurement temperature
    T2 = 293.15  ## temperature to be normalised to

    Eg0 = 1.17  ## eV, Eg(0K)
    S = 1.49  ## parameter, unitless
    Eph = 25.5e-3  ## eV, average phonon energy

    ## eV, Silicon bandgap energy dependence on T, O'Donnel and Chen
    Eg = Eg0 - S * Eph * (
        coth(
            Eph
            / (2.0 * constants.physical_constants["Boltzmann constant in eV/K"][0] * T1)
        )
        - 1
    )
    # Eg = 1.124 ##eV, PhD thesis

    return (
        current
        * ((T2 / T1) ** 2)
        * np.exp(
            -(Eg / (2 * constants.physical_constants["Boltzmann constant in eV/K"][0]))
            * (1 / T2 - 1 / T1)
        )
    )


def normalise(current, temp):  ## takes lists! as input
    i_norm = []
    if len(current) > 0 and len(temp) > 0:
        if len(current) == len(temp):
            for curr_value, temp_value in zip(current, temp):
                i_norm.append(normalise_current(curr_value, temp_value))
        else:
            i_norm = [normalise_current(i, np.mean(temp)) for i in current]
        return i_norm

    log.warning(bcolors.WARNING + "Current array is not normalised!" + bcolors.ENDC)
    return current


def analyse(iv_array, depl_volt, module_sn, layer, ref=None, temp=None):
    is3Dmodule = layer == "L0"
    cold = False

    #  check input IV array
    for key in ["voltage", "current", "sigma current"]:
        iv_array[key] = [abs(value) for value in iv_array[key]]

    if len(iv_array["voltage"]) == len(iv_array["temperature"]):
        normalised_current = normalise(iv_array["current"], iv_array["temperature"])
        cold = np.average(iv_array["temperature"]) < 0
    elif len(iv_array["temperature"]) > 0:
        normalised_current = normalise(
            iv_array["current"],
            len(iv_array["current"]) * [np.average(iv_array["temperature"])],
        )
        cold = np.average(iv_array["temperature"]) < 0
    elif temp is not None:
        log.warning(
            bcolors.WARNING
            + f"No temperature array recorded, using {temp}degC."
            + bcolors.ENDC
        )
        normalised_current = normalise(
            iv_array["current"], len(iv_array["current"]) * [temp]
        )
        cold = temp < 0
    else:
        log.warning(
            bcolors.WARNING
            + "No temperature recorded, cannot normalise to 20 degC."
            + bcolors.ENDC
        )

    if cold:
        normalised_current = iv_array["current"]

    #  check reference IV data
    if ref is not None:
        try:
            ref["reference_IVs"]
        except Exception as fail:
            log.warning(
                bcolors.WARNING + f"No reference IVs found {fail}" + bcolors.ENDC
            )

            if is3Dmodule and len(ref["reference_IVs"]) == 3:
                log.debug("Found 3 bare single IVs for triplet.")
            elif not is3Dmodule and len(ref["reference_IVs"]) == 1:
                log.debug("Found one bare quad IV.")
            else:
                log.error(
                    bcolors.ERROR
                    + "Incorrect number of reference IVs found \U0001F937"
                    + bcolors.ENDC
                )

            for item in ref["reference_IVs"]:
                if not (
                    item["Vbd"]
                    and item["Vfd"]
                    and item["temperature"]
                    and item["IV_ARRAY"]
                ):
                    log.error(
                        bcolors.ERROR
                        + 'Key words missing in "reference_IVs"'
                        + bcolors.ENDC
                    )

    #  get values
    ## sensor area
    if is3Dmodule:  ## "L0"
        area = 3 * 4.25  ## for triplet
    elif layer == "L1":
        area = 15.76
    else:  ## "L2"
        area = 15.92  # [cm^2]

    #  depletion voltage, operation voltage
    ## sensor measurement range is 0V to 200V (planar)
    Vdepl = 0
    if depl_volt is not None and abs(depl_volt) > 0 and abs(depl_volt) < 200:
        Vdepl = abs(depl_volt)
        log.info(f"Using manual input depletion voltage {Vdepl}V.")
    elif ref is not None:
        try:
            tmp_vfd = max(abs(v["Vfd"]) for v in ref["reference_IVs"])
            if 0 < tmp_vfd < 200:
                Vdepl = tmp_vfd
                log.info(f"Found depletion voltage from sensor data: {Vdepl}V.")
            else:
                log.warning(
                    bcolors.WARNING
                    + f"Depletion voltage provided in the bare module IV is not valid: {tmp_vfd}V. Proceed using default value!"
                    + bcolors.ENDC
                )
        except KeyError:
            depl_volt = None
            log.warning(
                bcolors.WARNING
                + "No depletion voltage found in bare module IV."
                + bcolors.ENDC
            )

    if Vdepl == 0:
        Vdepl = 5.0 if is3Dmodule else 50.0
        log.warning(
            bcolors.WARNING
            + f"No valid depletion voltage provided, proceed using default value of {Vdepl}V."
            + bcolors.ENDC
        )

    ## same for sensor and module
    operation_voltage = Vdepl + 20.0 if is3Dmodule else Vdepl + 50.0

    #  breakdown voltage and leakage current at operation voltage from previous stage
    ## *0 values are from previous stage (bare module reception)
    Vbd0 = -999  ## get from bare module stage below
    Ilc0 = 0

    if ref is not None:
        Vbd0 = min(v["Vbd"] for v in ref["reference_IVs"])
        for iv in ref["reference_IVs"]:
            for index, v in enumerate(iv["IV_ARRAY"]["voltage"]):
                if v >= operation_voltage:
                    temperatures = iv["IV_ARRAY"]["temperature"] or []
                    voltages = iv["IV_ARRAY"]["voltage"]
                    if not temperatures:
                        log.warning(
                            f"No temperature array found for bare module {iv['component_sn']}"
                        )

                    _temp: float = (
                        temperatures[index]
                        if len(temperatures) == len(voltages)
                        else iv["temperature"]
                    )

                    Ilc0 += normalise_current(
                        iv["IV_ARRAY"]["current"][index], _temp
                    )  ## += for triplets

                    break

        log.debug(f"Ilc0: {Ilc0}uA at {operation_voltage}V")

    #  breakdown voltage and leakage current at operation voltage
    Vbd = -999  ## -999V if no breakdown occurred during the measurement
    Vbd_reduction = 0
    Ilc = 0

    ## thresholds AT2-IP-ES-0009 (module), AT2-IP-QC-0004 (planar), AT2-IP-QC-0003 (3D)
    Vdepl_threshold = 0
    if layer == "L0":
        Vdepl_threshold = 10.0
    elif layer == "L1":
        Vdepl_threshold = 60.0
    elif layer == "L2":
        Vdepl_threshold = 100.0

    ## same for sensor and module
    breakdown_threshold = Vdepl + 20.0 if is3Dmodule else Vdepl + 70.0
    ## compared to bare module reception IV
    breakdown_reduction_threshold = 10 if Vbd0 != -999 else 0
    ## uA/cm^2; module criteria is 2x sensor criteria
    current_threshold = 2.5 * 2 if is3Dmodule else 0.75 * 2
    ## increase allowed by a factor of 2 compared to bare module stage
    current_increase_threshold = 2.0 * Ilc0

    ## pass flags from previous stage
    Vbd0_pass = None
    if Vbd0 and ref is not None:
        Vbd0_pass = Vbd0 > breakdown_threshold or Vbd0 == -999

    Ilc0_pass = None
    if Ilc0 and ref is not None:
        Ilc0_pass = (
            Ilc0 / area < current_threshold / 2.0
        )  ## use sensor criteria; what are the values for bare module?

    Vdepl_pass = None
    if Vdepl:
        Vdepl_pass = Vdepl <= Vdepl_threshold

    # Finding leakage current at threshold voltage
    fig, ax = plt.subplots(1, figsize=(7.2, 4.0))
    for idx, V in enumerate(iv_array["voltage"]):
        if Vdepl > V:
            continue

        if Ilc == 0 and operation_voltage <= V:
            Ilc = normalised_current[idx]

        # Finding breakdown voltage for 3D using temperature-normalised current
        if (
            is3Dmodule
            and normalised_current[idx] > normalised_current[idx - 5] * 2
            and iv_array["voltage"][idx - 5] > Vdepl
        ):
            Vbd = normalised_current[idx - 5]
            log.info(f"Breakdown at {Vbd:.1f} V for 3D sensor")
            ax.axvline(
                Vbd,
                linewidth=4,
                color="r",
                label=f"Bd @ {Vbd:.0f}V",
            )
            break

        # Finding breakdown voltage for Planar using temperature-normalised current
        if (
            normalised_current[idx] > normalised_current[idx - 1] * 1.2
            and normalised_current[idx - 1] != 0
        ):
            Vbd = V
            log.info(f"Breakdown at {Vbd:.1f} V for planar sensor")
            ax.axvline(
                Vbd,
                linewidth=4,
                color="r",
                label=f"Bd @ {Vbd:.0f}V",
            )
            break

    #  plot IV, temperature and humidity
    style_data = "ko"
    style_normdata = "*k"
    if len(iv_array["sigma current"]) == 0:
        (p1,) = ax.plot(
            iv_array["voltage"][1:],
            iv_array["current"][1:],
            style_data,
            label="current (raw)",
            markersize=3,
        )
        if not cold:
            (p11,) = ax.plot(
                iv_array["voltage"][1:],
                normalised_current[1:],
                style_normdata,
                label="current (norm. 20$^\\circ$C)",
                markersize=5,
            )
    else:
        p1 = ax.errorbar(
            iv_array["voltage"][1:],
            iv_array["current"][1:],
            yerr=iv_array["sigma current"][1:],
            fmt=style_data,
            elinewidth=1,
            label="current (raw)",
            markersize=3,
        )

        if not cold:
            p11 = ax.errorbar(
                iv_array["voltage"][1:],
                normalised_current[1:],
                yerr=iv_array["sigma current"][1:],
                fmt=style_normdata,
                elinewidth=1,
                label="current (norm. 20$^\\circ$C)",
                markersize=5,
            )
    if not cold:
        first_legend = plt.legend(
            handles=[p1, p11], loc="lower center", bbox_to_anchor=(0.15, -0.33)
        )
    else:
        first_legend = plt.legend(
            handles=[p1], loc="lower center", bbox_to_anchor=(0.15, -0.33)
        )
    plt.gca().add_artist(first_legend)

    if len(iv_array["temperature"]) == 0 and temp is None:
        log.warning(bcolors.WARNING + "No temperature to plot!" + bcolors.ENDC)
    else:
        ax1 = ax.twinx()
        if len(iv_array["voltage"][1:]) == len(iv_array["temperature"][1:]):
            (p2,) = ax1.plot(
                iv_array["voltage"][1:],
                iv_array["temperature"][1:],
                color="C1",
                linewidth=1,
                label="temperature",
            )
        elif len(iv_array["temperature"]) > 0:
            (p2,) = ax1.axhline(
                np.average(iv_array["temperature"][1:]),
                color="C1",
                linewidth=1,
                label="temperature",
            )
        else:
            (p2,) = ax1.axhline(
                temp,
                color="C1",
                linewidth=1,
                label="temperature",
            )

        ax1.set_ylabel("T ($^\\circ$C)", color="C1", fontsize="large")
        second_legend = plt.legend(
            handles=[p2], loc="lower center", bbox_to_anchor=(0.55, -0.33)
        )
        plt.gca().add_artist(second_legend)

    if len(iv_array["humidity"]) == 0:
        log.warning(bcolors.WARNING + "No humidity array to plot" + bcolors.ENDC)
    else:
        ax2 = ax.twinx()
        if len(iv_array["voltage"][1:]) == len(iv_array["humidity"][1:]):
            (p3,) = ax2.plot(
                iv_array["voltage"][1:],
                iv_array["humidity"][1:],
                color="C2",
                linewidth=1,
                label="humidity",
            )
        else:
            # # if len(iv_array["humidity"]) > 0:
            (p3,) = ax2.axhline(
                np.average(iv_array["humidity"][1:]),
                color="C2",
                linewidth=1,
                label="humidity",
            )
        ax2.set_ylabel("RH (%)", color="C2", fontsize="large")
        ax2.spines["right"].set_position(("outward", 60))
        third_legend = plt.legend(
            handles=[p3], loc="lower center", bbox_to_anchor=(0.85, -0.33)
        )
        plt.gca().add_artist(third_legend)

    #  plot reference bare module IV
    if ref is not None:
        ref_plots = []
        ref_voltage = []

        for iv in ref["reference_IVs"]:
            iv["IV_ARRAY"]["voltage"] = [abs(v) for v in iv["IV_ARRAY"]["voltage"]]
            iv["IV_ARRAY"]["current"] = [abs(c) for c in iv["IV_ARRAY"]["current"]]
            _prefix = guess_prefix(iv["IV_ARRAY"]["current"])
            if _prefix != "u":
                log.warning(
                    bcolors.WARNING
                    + f'No prefix found. Assuming {_prefix} from data and converting to "uA"!'
                    + bcolors.ENDC
                )
                iv["IV_ARRAY"]["current"] = convert_prefix(
                    iv["IV_ARRAY"]["current"], inprefix=_prefix, targetprefix="u"
                )
            try:
                iv["IV_ARRAY"]["current"] = normalise(
                    iv["IV_ARRAY"]["current"], iv["IV_ARRAY"]["temperature"]
                )
                ref_plots.append(
                    ax.plot(
                        iv["IV_ARRAY"]["voltage"],
                        iv["IV_ARRAY"]["current"],
                        linestyle="dotted",
                        label=iv["component_sn"] + " norm.",
                    )[0]
                )
            except Exception as e:
                log.warning(f"Can't normalise bare module IV: {e}")
                ref_plots.append(
                    ax.plot(
                        iv["IV_ARRAY"]["voltage"],
                        iv["IV_ARRAY"]["current"],
                        linestyle="dotted",
                        label=iv["component_sn"],
                    )[0]
                )

            ref_voltage.append([int(v) for v in iv["IV_ARRAY"]["voltage"]])

        if len(ref["reference_IVs"]) > 1:
            ## check if all measurements have the same length
            if all(i == ref_voltage[0] for i in ref_voltage):
                sum_array = {}
                sum_array["voltage"] = [abs(item) for item in ref_voltage[0]]
                sum_array["current"] = len(sum_array["voltage"]) * [0]
                for iv in ref["reference_IVs"]:
                    sum_array["current"] = [
                        sum(x)
                        for x in zip(
                            sum_array["current"],
                            iv["IV_ARRAY"]["current"],
                        )
                    ]

                ref_plots.append(
                    ax.plot(
                        sum_array["voltage"],
                        sum_array["current"],
                        linestyle="dashed",
                        label="sum(bare modules)",
                    )[0]
                )
            else:
                log.warning(
                    bcolors.WARNING
                    + f"Bare IVs have different lengths {[len(iv['IV_ARRAY']['voltage']) for iv in ref['reference_IVs']]}, cannot sum up the currents."
                    + bcolors.ENDC
                )

        ax.legend(handles=ref_plots, loc="best")

    ax.set_title(f'IV for module "{module_sn}"', fontsize="large")
    ax.set_xlabel("Bias Voltage [V]", ha="right", va="top", x=1.0, fontsize="large")
    ax.set_ylabel(
        "Leakage Current ($\\mathrm{\\mu}$A)",
        ha="right",
        va="bottom",
        y=1.0,
        fontsize="large",
    )

    fig.subplots_adjust(bottom=0.25)
    fig.subplots_adjust(right=0.75)

    ax.grid()

    #  flagging
    Ilc_pass = True

    # # Pass or fail on leakaged current at operational voltage
    Ilc_pass = Ilc / area < current_threshold
    Ilc_increase_pass = Ilc <= current_increase_threshold and Ilc0_pass is not None

    # # Pass or fail on breakdown voltage
    Vbd_pass = (Vbd > breakdown_threshold) or (
        iv_array["voltage"][-1] > breakdown_threshold
    )
    if Vbd != -999:
        ## positive if Vbd reduced (bad), negative if Vbd increased (good)
        Vbd_reduction = Vbd0 - Vbd
    Vbd_reduction_pass = (
        Vbd_reduction == 0 or Vbd_reduction < breakdown_reduction_threshold
    ) and Vbd0_pass is not None

    # # "IV_ARRAY", "IV_IMG", "BREAKDOWN_VOLTAGE", "LEAK_CURRENT", "MAXIMUM_VOLTAGE", "NO_BREAKDOWN_VOLTAGE_OBSERVED"
    results = {}
    results["IV_ARRAY"] = iv_array
    # results["IV_IMG"] ?? ## Required for sensor but not for module
    results["BREAKDOWN_VOLTAGE"] = Vbd
    results["LEAK_CURRENT"] = Ilc
    results["NO_BREAKDOWN_VOLTAGE_OBSERVED"] = Vbd == -999
    results["MAXIMUM_VOLTAGE"] = max(iv_array["voltage"])

    passes_qc = (
        Vbd_pass
        and Ilc_pass
        and Vdepl_pass
        and Vbd_reduction_pass
        and Ilc_increase_pass
        and Vbd0_pass is not None
        and Ilc0_pass is not None
    )

    if passes_qc:
        log.info(
            f"Ilc0_pass: {Ilc0_pass}, Ilc_pass: {Ilc_pass}, Ilc_increase_pass: {Ilc_increase_pass}, Vbd0_pass: {Vbd0_pass}, Vbd_pass: {Vbd_pass}, Vbd_reduction_pass: {Vbd_reduction_pass}, passes_qc: {passes_qc}"
        )
    else:
        log.info(
            f"Ilc0: {Ilc0}uA, Ilc0_pass: {Ilc0_pass} | Ilc: {Ilc}uA, Ilc_pass: {Ilc_pass}"
        )
        log.info(
            f"Vbd0: {Vbd0}V, Vbd0_pass: {Vbd0_pass} | Vbd: {Vbd}V, Vbd_pass: {Vbd_pass}"
        )
        log.info(
            f"Vbd_reduction: {Vbd_reduction}V, Vbd_reduction_pass: {Vbd_reduction_pass}, passes_qc: {passes_qc}"
        )

    return results, fig, passes_qc


def alt_loader(path, dtyper):
    ## loads data from sensor IV json format [1], input into non-electric-GUI [2] and output from non-electric-GUI [3]
    ## [1] https://gitlab.cern.ch/atlas-itk/sw/db/production_database_scripts/-/blob/pixel_preproduction_GUI/pixels/sensors_prototype/data/IV_DATA_TILE.json
    ## [2] https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/uploads/b0c6d5edde5514865e27574810a3a449/ivcurve_result_20230403_235249.json
    ## [3] https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/uploads/8dbdc2f81ff479343318dfe25e6ae96d/20UPGXM2000013_MODULE__INITIAL_WARM_IV_MEASURE_2023Y03m27d__04_49_56+0000.json

    qchelper = False

    with Path(path).open(encoding="utf-8") as serialized:
        if "QCHELPER" in serialized.read():
            qchelper = True
        serialized.seek(0)  ## move cursur back to the beginning of file
        inputdata = json.load(serialized)

    alldf = []
    # Can read one IV measurement in sensor json format at a time
    if not isinstance(inputdata, list):
        inputdata = [inputdata]
        log.info("Found data for one measurement.")
    else:
        log.info(f"Found data for {len(inputdata)} measurement(s).")
        if qchelper:
            log.info("Output format from QC helper/non-electric GUI detected.")

    for item in inputdata:
        module_sn = ""
        test = ""
        institution = ""
        date = ""
        prefix = None
        vdepl = 0
        IV_ARRAY = {}

        keys = {
            "component": module_sn,
            "test": test,
            "institution": institution,
            "date": date,
            "prefix": prefix,
            "depletion_voltage": vdepl,
            "IV_ARRAY": IV_ARRAY,
        }

        for key in keys:
            if key not in item and not qchelper:
                log.warning(
                    bcolors.WARNING
                    + f"Key {key} is missing in the input file!"
                    + bcolors.ENDC
                )
        if not qchelper:
            if item["component"]:
                module_sn = item["component"]
            else:
                log.error(bcolors.ERROR + "No module SN found." + bcolors.ENDC)
                return None

            if "iv" in item["test"].lower():
                test_type = Path(__file__).stem
            else:
                log.error(bcolors.ERROR + "No test type found." + bcolors.ENDC)
                return None

            try:
                institution = item["institution"]
            except Exception:
                log.warning(
                    bcolors.WARNING
                    + "No institution found in measurement file!"
                    + bcolors.ENDC
                )
                institution = ""

            try:
                if item["date"]:
                    try:
                        timestart = time.mktime(
                            datetime.strptime(
                                item["date"], "%d.%m.%Y %H:%M"
                            ).timetuple()
                        )
                    except Exception as err:
                        log.warning(
                            bcolors.WARNING
                            + f"Cannot decode time stamp format {err}"
                            + bcolors.ENDC
                        )
                        timestart = item["date"]
            except Exception:
                log.warning(
                    bcolors.WARNING + "No measurement time found." + bcolors.ENDC
                )
                timestart = datetime.now().strftime("%Y-%m-%d_%H%M%S")

            try:
                vdepl = item["depletion_voltage"]
            except Exception:
                if dtyper["depl_volt"] is not None:
                    vdepl = dtyper["depl_volt"]
                    log.warning(
                        bcolors.WARNING
                        + f"No depletion voltage found, using manual input via --vdepl {dtyper['depl_volt']}"
                        + bcolors.ENDC
                    )
                else:
                    log.warning(
                        bcolors.WARNING
                        + "No depletion voltage found! Will use database or default value."
                        + bcolors.ENDC
                    )

            if item["IV_ARRAY"]:
                iv_array = item["IV_ARRAY"]
            else:
                log.error(bcolors.ERROR + "No measurement data found!" + bcolors.ENDC)
                return None

            try:
                if item["prefix"] and "A" in item["prefix"]:
                    current_unit = item["prefix"]
            except Exception:
                current_unit = guess_prefix(iv_array["current"]) + "A"
                log.warning(
                    bcolors.WARNING
                    + f"No prefix found. Assuming {current_unit} from data!"
                    + bcolors.ENDC
                )
        elif qchelper:
            if len(item) == 1:
                jtem = item[0]
            else:
                log.error("Unknown format.")
                return None
            if jtem["serialNumber"] == jtem["results"]["metadata"]["MODULE_SN"]:
                module_sn = jtem["serialNumber"]
            elif not jtem["serialNumber"] and jtem["results"]["metadata"]["MODULE_SN"]:
                module_sn = jtem["results"]["metadata"]["MODULE_SN"]
            elif jtem["serialNumber"] and not jtem["results"]["metadata"]["MODULE_SN"]:
                module_sn = jtem["serialNumber"]
            else:
                log.error(
                    bcolors.ERROR
                    + "'serialNumber' and 'MODULE_SN' are inconsistent or missing!"
                    + bcolors.ENDC
                )
                return None

            if "IV_MEASURE" in jtem["testType"]:
                test_type = Path(__file__).stem
            else:
                log.error(bcolors.ERROR + "No test type found." + bcolors.ENDC)
                return None

            ## not there by default
            try:
                institution = jtem["institution"]
            except Exception:
                log.warning(
                    bcolors.WARNING
                    + "No institution found in measurement file!"
                    + bcolors.ENDC
                )
                institution = ""

            try:
                if jtem["date"]:
                    try:
                        timestart = time.mktime(
                            datetime.strptime(
                                jtem["date"], "%d.%m.%Y %H:%M"
                            ).timetuple()
                        )
                    except Exception as err:
                        log.warning(
                            bcolors.WARNING
                            + f"Cannot decode time stamp format {err}"
                            + bcolors.ENDC
                        )
                        timestart = jtem["date"]
            except Exception:
                log.warning(
                    bcolors.WARNING + "No measurement time found." + bcolors.ENDC
                )
                timestart = datetime.now().strftime("%Y-%m-%d_%H%M%S")

            try:
                vdepl = jtem["depletion_voltage"]
            except Exception:
                if dtyper["depl_volt"] is not None:
                    vdepl = dtyper["depl_volt"]
                    log.warning(
                        bcolors.WARNING
                        + f"No depletion voltage found, using manual input via --vdepl {dtyper['depl_volt']}"
                        + bcolors.ENDC
                    )
                else:
                    log.warning(
                        bcolors.WARNING
                        + "No depletion voltage found! Will use database or default value."
                        + bcolors.ENDC
                    )

            if jtem["results"]["IV_ARRAY"]:
                iv_array = jtem["results"]["IV_ARRAY"]
            else:
                log.error(bcolors.ERROR + "No measurement data found!" + bcolors.ENDC)
                return None

            try:
                if jtem["prefix"] and "A" in jtem["prefix"]:
                    current_unit = jtem["prefix"]
            except Exception:
                current_unit = guess_prefix(iv_array["current"]) + "A"
                log.warning(
                    bcolors.WARNING
                    + f"No prefix found. Assuming {current_unit} from data!"
                    + bcolors.ENDC
                )
        else:
            log.error(bcolors.ERROR + "Unknown format." + bcolors.ENDC)

        data = qcDataFrame(
            columns=[
                "time",
                "voltage",
                "current",
                "sigma current",
                "temperature",
                "humidity",
            ],
            units=["s", "V", current_unit, current_unit, "C", "%"],
        )

        data.set_x("voltage", True)
        data.add_data(iv_array)
        data.add_meta_data("Institution", institution)
        data.add_meta_data("ModuleSN", module_sn)
        data.add_meta_data("TimeStart", timestart)
        data.add_meta_data("DepletionVoltage", vdepl)
        data.add_meta_data("AverageTemperature", np.average(data["temperature"]))
        outputDF = outputDataFrame()
        outputDF.set_test_type(test_type)
        outputDF.set_results(data)
        alldf.append(outputDF)
    return alldf


@app.command()
def main(
    input_meas: Path = OPTIONS["input_meas"],
    base_output_dir: Path = OPTIONS["output_dir"],
    qc_criteria_path: Path = typer.Option(  # noqa: B008
        None,
        "-q",
        "--qc-criteria",
        help="path to reference IV measurement results from bare module stage.",
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
    ),
    input_layer: str = OPTIONS["layer"],
    verbosity: LogLevel = OPTIONS["verbosity"],
    site: str = OPTIONS["site"],
    input_vdepl: float = OPTIONS["depl_volt"],
):
    test_type = Path(__file__).stem

    time_start = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = base_output_dir.joinpath(test_type).joinpath(f"{time_start}")
    output_dir.mkdir(parents=True, exist_ok=False)

    log.setLevel(verbosity.value)
    log.addHandler(logging.FileHandler(f"{output_dir}/output.log"))

    # Turn off matplotlib DEBUG messages
    plt.set_loglevel(level="warning")
    # Turn off pytest DEBUG messages
    pil_logger = logging.getLogger("PIL")
    pil_logger.setLevel(logging.INFO)

    if "analysis_cuts" in str(qc_criteria_path):
        log.error(
            bcolors.ERROR
            + "Please provide a valid reference IV from the bare module stage."
            + bcolors.ENDC
        )
        return

    allinputs = get_inputs(input_meas)
    if qc_criteria_path is not None:
        reference_iv = get_inputs(qc_criteria_path)
    else:
        reference_iv = None
        log.warning(
            bcolors.WARNING
            + "No reference bare module IV provided, analysis will fail."
            + bcolors.ENDC
        )

    log.info("")
    log.info(" ===============================================")
    log.info(" \tPerforming IV analysis")
    log.info(" ===============================================")
    log.info("")

    alloutput = []
    timestamps = []
    for _ifile, filename in enumerate(sorted(allinputs)):
        log.info("")
        log.info(f" Loading {filename}")
        meas_timestamp = get_time_stamp(filename)
        with Path(filename).open(encoding="utf-8") as infile:
            if "QCHELPER" in infile.read():
                infile.seek(0)
                inputDFs = alt_loader(filename, OPTIONS)
            else:
                try:
                    inputDFs = load_json(filename)
                except Exception:
                    try:
                        log.warning(
                            bcolors.WARNING
                            + "Unusual file format, trying to decode."
                            + bcolors.ENDC
                        )
                        inputDFs = alt_loader(filename, OPTIONS)
                    except Exception as eee:
                        log.error(
                            bcolors.ERROR
                            + f" JsonChecker check not passed. {eee}. Please provide a valid input file."
                            + bcolors.ENDC
                        )
                        raise RuntimeError from eee

        log.info(
            f" There are results from {len(inputDFs)} module(s) stored in this file"
        )

        for inputDF in inputDFs:
            # Check file integrity
            checker = JsonChecker(inputDF, test_type)

            try:
                checker.check()
            except BaseException as exc:
                log.exception(exc)
                log.error(
                    bcolors.ERROR
                    + " JsonChecker check not passed, skipping this input."
                    + bcolors.ENDC
                )
                continue
            else:
                log.debug(" JsonChecker check passed!")

            #   Get info
            qcframe = inputDF.get_results()
            metadata = qcframe.get_meta_data()
            module_sn = metadata.get("ModuleSN")

            if input_layer == "Unknown":
                try:
                    layer = get_layer_from_sn(module_sn)
                except Exception:
                    log.error(bcolors.WARNING + " Something went wrong." + bcolors.ENDC)
            else:
                module_sn = metadata.get("ModuleSN")
                log.warning(
                    bcolors.WARNING
                    + f" Overwriting default layer config {get_layer_from_sn(module_sn)} with manual input {input_layer}!"
                    + bcolors.ENDC
                )
                layer = input_layer
            check_layer(layer)

            institution = metadata.get("Institution")
            if site != "" and institution != "":
                log.warning(
                    bcolors.WARNING
                    + f" Overwriting default institution {institution} with manual input {site}!"
                    + bcolors.ENDC
                )
                institution = site
            elif site != "":
                institution = site

            #  Simplistic QC criteria
            meas_array = {}
            _prefix = None

            try:
                if qcframe._data["current"]["Unit"] != "uA":
                    _prefix = qcframe._data["current"]["Unit"]
            except KeyError:
                _prefix = guess_prefix(qcframe._data["current"]["Values"])
                log.warning(
                    bcolors.WARNING
                    + f"No unit found! Guessing unit from data to be {_prefix}A."
                    + bcolors.ENDC
                )

            try:
                for key in ["current", "sigma current"]:
                    qcframe._data[key]["Values"] = convert_prefix(
                        qcframe._data[key]["Values"],
                        inprefix=qcframe._data[key]["Unit"],
                        targetprefix="u",
                    )
                    qcframe._data[key]["Unit"] = "uA"
            except KeyError as kerr:
                log.warning(kerr)

            for key in qcframe._data:
                meas_array[key] = qcframe._data[key]["Values"]

            baremoduleIV = {}
            if reference_iv is not None:
                for item in reference_iv:
                    with Path(item).open(encoding="utf-8") as serialized:
                        inputdata = json.load(serialized)
                    # Can read one IV measurement in sensor json format at a time
                    if not isinstance(inputdata, list):
                        inputdata = [inputdata]
                        log.info("Found ref data for one measurement.")
                    else:
                        log.info(f"Found ref data for {len(inputdata)} measurement.")

                    for jtem in inputdata:
                        tmp_sn = jtem["target_component"]
                        if tmp_sn == module_sn and jtem["reference_IVs"]:
                            baremoduleIV = jtem
                            break
                        log.error(
                            bcolors.ERROR
                            + "Didn't find correct module SN in or no reference data."
                            + bcolors.ENDC
                        )
                        return
            else:
                baremoduleIV = None

            results, fig, passes_qc = analyse(
                meas_array,
                input_vdepl,
                module_sn,
                layer,
                baremoduleIV,
                metadata.get("AverageTemperature"),
            )
            ## maybe for the future
            # passes_qc, summary = perform_qc_analysis(
            # test_type, qc_config, layer, results
            # )
            # print_result_summary(summary, test_type, output_dir, chipname)
            if passes_qc == -1:
                log.error(
                    bcolors.ERROR
                    + f" QC analysis for {module_sn} was NOT successful. Please fix and re-run. Continuing to next chip.."
                    + bcolors.ENDC
                )
                continue
            log.info("")
            if passes_qc:
                log.info(
                    f" Module {module_sn} passes QC? "
                    + bcolors.OKGREEN
                    + f"{passes_qc}"
                    + bcolors.ENDC
                )
            else:
                log.info(
                    f" Module {module_sn} passes QC? "
                    + bcolors.BADRED
                    + f"{passes_qc}"
                    + bcolors.ENDC
                )
            log.info("")

            #  Output a json file
            outputDF = outputDataFrame()
            outputDF._serialNumber = module_sn
            outputDF.set_test_type(test_type)
            data = qcDataFrame()
            for key, result in results.items():
                data.add_parameter(key, result)
            data.add_property(
                "ANALYSIS_VERSION",
                __version__,
            )
            data.add_property("TEMP", np.mean(meas_array["temperature"]), 2)
            data.add_property(
                "HUM",
                np.mean(meas_array["humidity"])
                if len(meas_array["humidity"]) > 0
                else 0,
                2,
            )

            data._meta_data.update(metadata)

            data.add_meta_data(
                "MEASUREMENT_VERSION",
                qcframe.get_properties().get(test_type + "_MEASUREMENT_VERSION"),
            )
            data.add_meta_data("QC_LAYER", layer)
            data.add_meta_data("INSTITUTION", institution)
            data.add_meta_data("MODULE_SN", module_sn)

            outputDF.set_results(data)
            outputDF.set_pass_flag(bool(passes_qc))

            alloutput += [outputDF.to_dict(True)]
            timestamps += [meas_timestamp]
            plt_outfile = output_dir.joinpath(f"{module_sn}_plot.png")
            fig.savefig(plt_outfile, dpi=150)
    # Only store results from same timestamp into same file
    dfs = np.array(alloutput)
    tss = np.array(timestamps)
    for x in np.unique(tss):
        outfile = output_dir.joinpath(f"{module_sn}.json")
        log.info(f" Saving output of analysis to: {outfile}")
        save_dict_list(
            outfile,
            dfs[tss == x].tolist(),
        )


if __name__ == "__main__":
    typer.run(main)
