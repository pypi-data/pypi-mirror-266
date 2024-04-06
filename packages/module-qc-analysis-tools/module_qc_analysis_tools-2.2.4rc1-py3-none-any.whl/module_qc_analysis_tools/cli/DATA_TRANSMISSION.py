from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import typer
from module_qc_data_tools import (
    get_layer_from_sn,
    get_nlanes_from_sn,
    load_json,
    outputDataFrame,
    qcDataFrame,
    save_dict_list,
)

from module_qc_analysis_tools import __version__
from module_qc_analysis_tools.cli.globals import (
    CONTEXT_SETTINGS,
    OPTIONS,
    LogLevel,
)
from module_qc_analysis_tools.utils.analysis import (
    check_layer,
    perform_qc_analysis,
    print_result_summary,
)
from module_qc_analysis_tools.utils.misc import (
    DataExtractor,
    JsonChecker,
    bcolors,
    get_inputs,
    get_qc_config,
    get_time_stamp,
)

app = typer.Typer(context_settings=CONTEXT_SETTINGS)


@app.command()
def main(
    input_meas: Path = OPTIONS["input_meas"],
    base_output_dir: Path = OPTIONS["output_dir"],
    qc_criteria_path: Path = OPTIONS["qc_criteria"],
    input_layer: str = OPTIONS["layer"],
    permodule: bool = OPTIONS["permodule"],
    site: str = OPTIONS["site"],
    verbosity: LogLevel = OPTIONS["verbosity"],
):
    test_type = Path(__file__).stem

    allinputs = get_inputs(input_meas)
    qc_config = get_qc_config(qc_criteria_path, test_type)

    time_start = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = base_output_dir.joinpath(test_type).joinpath(f"{time_start}")
    output_dir.mkdir(parents=True, exist_ok=False)

    log = logging.getLogger("analysis")
    log.setLevel(verbosity.value)
    log.addHandler(logging.FileHandler(f"{output_dir}/output.log"))

    # Turn off matplotlib DEBUG messages
    plt.set_loglevel(level="warning")
    # Turn off pytest DEBUG messages
    pil_logger = logging.getLogger("PIL")
    pil_logger.setLevel(logging.INFO)

    linestyles = ["solid", "dotted", "dashed", "dashdot"]
    markerstyles = ["*", "o", "v", "s"]
    colours = ["C0", "C1", "C2", "C3"]

    log.info("")
    log.info(" =======================================")
    log.info(" \tPerforming DATA TRANSMISSION analysis")
    log.info(" =======================================")
    log.info("")

    alloutput = []
    timestamps = []
    for filename in sorted(allinputs):
        log.info("")
        log.info(f" Loading {filename}")
        meas_timestamp = get_time_stamp(filename)
        inputDFs = load_json(filename)

        log.debug(
            f" There are results from {len(inputDFs)} chip(s) stored in this file"
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
            n_lanes_per_chip = get_nlanes_from_sn(module_sn)

            if input_layer == "Unknown":
                try:
                    layer = get_layer_from_sn(module_sn)
                except Exception:
                    log.error(bcolors.WARNING + " Something went wrong." + bcolors.ENDC)
            else:
                log.warning(
                    bcolors.WARNING
                    + f" Overwriting default layer config {get_layer_from_sn(module_sn)} with manual input {input_layer}!"
                    + bcolors.ENDC
                )
                layer = input_layer
            check_layer(layer)

            try:
                chipname = metadata.get("Name")
                log.debug(f" Found chip name = {chipname} from chip config")
            except Exception:
                log.error(
                    bcolors.ERROR
                    + f" Chip name not found in input from {filename}, skipping."
                    + bcolors.ENDC
                )
                continue

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

            if institution == "":
                log.error(
                    bcolors.ERROR
                    + "No institution found. Please specify your testing site either in the measurement data or specify with the --site option. "
                    + bcolors.ENDC
                )
                return

            #   Calculate quanties
            extractor = DataExtractor(inputDF, test_type)
            calculated_data = extractor.calculate()

            log.debug(calculated_data)

            passes_qc = True
            passes_qc_per_lane = n_lanes_per_chip * [True]
            summary = np.empty((0, 4), str)

            DELAY = calculated_data["Delay"]["Values"]
            EYE_OPENING = []
            EYE_WIDTH = []
            DELAY_SETTING = []

            _fig, ax = plt.subplots()

            for lane in range(len(calculated_data.keys()) - 1):
                EYE_OPENING.append(calculated_data[f"EyeOpening{lane}"]["Values"])

                start_val = 0
                width = 0
                last_width = 0
                best_val = 0
                best_width = 0
                best_delay = 0

                for j in DELAY:
                    if EYE_OPENING[-1][j] == 1:
                        if width == 0:
                            start_val = j
                        width += 1
                        if j == DELAY[-1] and width > last_width:
                            best_val = start_val
                            best_width = width
                    else:
                        if width > last_width:
                            best_val = start_val
                            best_width = width
                        last_width = best_width
                        width = 0

                if best_width != 0:
                    best_delay = int(best_val + (best_width / 2))
                    log.info(
                        f"Delay setting for lane {lane} with eye width {best_width}: {best_delay}"
                    )
                else:
                    log.info(f"No good delay setting for lane {lane}")

                EYE_WIDTH.append(best_width)
                DELAY_SETTING.append(best_delay)

                # # Internal eye diagram visualisation
                ax.step(
                    calculated_data["Delay"]["Values"],
                    calculated_data[f"EyeOpening{lane}"]["Values"],
                    linestyle=linestyles[lane],
                    color=colours[lane],
                    label=f"Eye Opening [{lane}]: {best_width}",
                )
                ax.plot(
                    best_delay,
                    1,
                    linestyle="None",
                    marker=markerstyles[lane],
                    markersize=5,
                    color=colours[lane],
                    label=f"Best Delay [{lane}]: {best_delay}",
                )

                ax.legend()

                # Load values to dictionary for QC analysis
                results = {}
                results.update({"EYE_WIDTH": best_width})

                # Perform QC analysis
                chiplog = logging.FileHandler(f"{output_dir}/{chipname}.log")
                log.addHandler(chiplog)
                (
                    passes_qc_per_lane[lane],
                    summary_per_lane,
                    _rounded_results,
                ) = perform_qc_analysis(test_type, qc_config, layer, results)
                summary_per_lane[0] = summary_per_lane[0] + str(lane)
                log.debug(summary_per_lane)
                summary = np.append(summary, [summary_per_lane], axis=0)
            summary.reshape(-1, 4)
            log.debug(summary)

            print_result_summary(summary, test_type, output_dir, chipname)

            ax.set_xlabel("Delay")
            ax.set_ylabel("Eye Opening")
            ax.set_title(f"{module_sn} {chipname}")
            plt.grid()
            plt.tight_layout()
            outfile = output_dir.joinpath(f"{chipname}_eye.png")
            log.info(f" Saving {outfile}")
            plt.savefig(outfile)
            plt.close()

            passes_qc = all(passes_qc_per_lane)

            if passes_qc == -1:
                log.error(
                    bcolors.ERROR
                    + f" QC analysis for {chipname} was NOT successful. Please fix and re-run. Continuing to next chip.."
                    + bcolors.ENDC
                )
                continue
            log.info("")
            if passes_qc:
                log.info(
                    f" Chip {chipname} passes QC? "
                    + bcolors.OKGREEN
                    + f"{passes_qc}"
                    + bcolors.ENDC
                )
            else:
                log.info(
                    f" Chip {chipname} passes QC? "
                    + bcolors.BADRED
                    + f"{passes_qc}"
                    + bcolors.ENDC
                )
            log.info("")
            log.removeHandler(chiplog)
            chiplog.close()

            #  Output a json file
            outputDF = outputDataFrame()
            outputDF.set_test_type(test_type)
            data = qcDataFrame()
            data._meta_data.update(metadata)
            data.add_property(
                "ANALYSIS_VERSION",
                __version__,
            )
            data.add_meta_data(
                "MEASUREMENT_VERSION",
                qcframe.get_properties().get(test_type + "_MEASUREMENT_VERSION"),
            )
            data.add_meta_data("QC_LAYER", layer)
            data.add_meta_data("INSTITUTION", institution)

            # Add eye widths to output file
            for lane in range(n_lanes_per_chip):
                data.add_parameter(f"EYE_WIDTH{lane}", EYE_WIDTH[lane], 0)

            outputDF.set_results(data)
            outputDF.set_pass_flag(passes_qc)
            if permodule:
                alloutput += [outputDF.to_dict(True)]
                timestamps += [meas_timestamp]
            else:
                outfile = output_dir.joinpath(f"{chipname}.json")
                log.info(f" Saving output of analysis to: {outfile}")
                save_dict_list(outfile, [outputDF.to_dict(True)])
    if permodule:
        # Only store results from same timestamp into same file
        dfs = np.array(alloutput)
        tss = np.array(timestamps)
        for x in np.unique(tss):
            outfile = output_dir.joinpath("module.json")
            log.info(f" Saving output of analysis to: {outfile}")
            save_dict_list(
                outfile,
                dfs[tss == x].tolist(),
            )


if __name__ == "__main__":
    typer.run(main)
