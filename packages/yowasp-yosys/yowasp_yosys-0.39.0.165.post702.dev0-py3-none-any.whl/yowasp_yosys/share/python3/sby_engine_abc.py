#
# SymbiYosys (sby) -- Front-end for Yosys-based formal verification flows
#
# Copyright (C) 2016  Claire Xenia Wolf <claire@yosyshq.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

import re, getopt
import json
from sby_core import SbyProc
from sby_engine_aiger import aigsmt_exit_callback, aigsmt_trace_callback


def abc_getopt(args, long):
    long = set(long)
    output = []
    parsed = []
    toggles = set()
    pos = 0

    while pos < len(args):
        arg = args[pos]
        pos += 1
        if not arg.startswith('-'):
            output.append(arg)
        elif arg == '--':
            output.extend(args[pos:])
            break
        elif arg.startswith('--'):
            if '=' in arg:
                prefix, param = arg.split('=', 1)
                if prefix + "=" in long:
                    parsed.append(prefix, param)
            elif arg[2:] in long:
                parsed.append((arg, ''))
            elif arg[2:] + "=" in long:
                parsed.append((arg, args[pos]))
                pos += 1
            else:
                output.append(arg)
        elif arg.startswith('-'):
            output.append(arg)
            for c in arg[1:]:
                if 'A' <= c <= 'Z':
                    if pos < len(args):
                        output.append(args[pos])
                        pos += 1
                else:
                    toggles.symmetric_difference_update([c])

    return output, parsed, toggles


def run(mode, task, engine_idx, engine):
    keep_going = False

    fold_command = "fold"
    if task.opt_aigfolds:
        fold_command += " -s"

    abc_command, custom_options, toggles = abc_getopt(engine[1:], [
        "keep-going",
    ])

    if len(abc_command) == 0:
        task.error("Missing ABC command.")

    if abc_command[0].startswith('-'):
        task.error(f"Unexpected ABC engine option '{abc_command[0]}'.")

    if abc_command[0] == "bmc3":
        if mode != "bmc":
            task.error("ABC command 'bmc3' is only valid in bmc mode.")
        for o, a in custom_options:
            task.error(f"Option {o} not supported by 'abc {abc_command[0]}'")
        abc_command[0] += f" -F {task.opt_depth} -v"

    elif abc_command[0] == "sim3":
        if mode != "bmc":
            task.error("ABC command 'sim3' is only valid in bmc mode.")
        for o, a in custom_options:
            task.error(f"Option {o} not supported by 'abc {abc_command[0]}'")
        abc_command[0] += f" -F {task.opt_depth} -v"

    elif abc_command[0] == "pdr":
        if mode != "prove":
            task.error("ABC command 'pdr' is only valid in prove mode.")

        for o, a in custom_options:
            if o == '--keep-going':
                keep_going = True
            else:
                task.error(f"Option {o} not supported by 'abc {abc_command[0]}'")

        abc_command[0] += " -v -l"

        if keep_going:
            abc_command += ["-a", "-X", f"engine_{engine_idx}/trace_"]

        if 'd' in toggles:
            abc_command += ["-I", f"engine_{engine_idx}/invariants.pla"]
            if not task.opt_aigfolds:
                fold_command += " -s"

    else:
        task.error(f"Invalid ABC command {abc_command[0]}.")

    smtbmc_vcd = task.opt_vcd and not task.opt_vcd_sim
    run_aigsmt = smtbmc_vcd or (task.opt_append and task.opt_append_assume)
    smtbmc_append = 0
    sim_append = 0
    log = task.log_prefix(f"engine_{engine_idx}")

    if task.opt_append_assume:
        smtbmc_append = task.opt_append
    elif smtbmc_vcd:
        if not task.opt_append_assume:
            log("For VCDs generated by smtbmc the option 'append_assume off' is ignored")
        smtbmc_append = task.opt_append
    else:
        sim_append = task.opt_append

    proc = SbyProc(
        task,
        f"engine_{engine_idx}",
        task.model("aig"),
        f"""cd {task.workdir}; {task.exe_paths["abc"]} -c 'read_aiger model/design_aiger.aig; {
            fold_command}; strash; {" ".join(abc_command)}; write_cex -a engine_{engine_idx}/trace.aiw'""",
        logfile=open(f"{task.workdir}/engine_{engine_idx}/logfile.txt", "w")
    )
    proc.checkretcode = True

    proc.noprintregex = re.compile(r"^\.+$")
    proc_status = "UNKNOWN"

    procs_running = 1

    aiger_props = None
    disproved = set()
    proved = set()

    def output_callback(line):
        nonlocal proc_status
        nonlocal procs_running
        nonlocal aiger_props

        if aiger_props is None:
            with open(f"{task.workdir}/model/design_aiger.ywa") as ywa_file:
                ywa = json.load(ywa_file)
                aiger_props = []
                for path in ywa["asserts"]:
                    aiger_props.append(task.design.properties_by_path.get(tuple(path)))

        if keep_going:
            match = re.match(r"Writing CEX for output ([0-9]+) to engine_[0-9]+/(.*)\.aiw", line)
            if match:
                output = int(match[1])
                prop = aiger_props[output]
                if prop:
                    prop.status = "FAIL"
                    task.status_db.set_task_property_status(prop, data=dict(source="abc pdr",  engine=f"engine_{engine_idx}"))
                disproved.add(output)
                proc_status = "FAIL"
                proc = aigsmt_trace_callback(task, engine_idx, proc_status,
                    run_aigsmt=run_aigsmt, smtbmc_vcd=smtbmc_vcd, smtbmc_append=smtbmc_append, sim_append=sim_append,
                    name=match[2],
                )
                proc.register_exit_callback(exit_callback)
                procs_running += 1
        else:
            match = re.match(r"^Output [0-9]+ of miter .* was asserted in frame [0-9]+.", line)
            if match: proc_status = "FAIL"

        match = re.match(r"^Proved output +([0-9]+) in frame +-?[0-9]+", line)
        if match:
            output = int(match[1])
            prop = aiger_props[output]
            if prop:
                prop.status = "PASS"
                task.status_db.set_task_property_status(prop, data=dict(source="abc pdr",  engine=f"engine_{engine_idx}"))
            proved.add(output)

        match = re.match(r"^Simulation of [0-9]+ frames for [0-9]+ rounds with [0-9]+ restarts did not assert POs.", line)
        if match: proc_status = "UNKNOWN"

        match = re.match(r"^Stopping BMC because all 2\^[0-9]+ reachable states are visited.", line)
        if match: proc_status = "PASS"

        match = re.match(r"^No output asserted in [0-9]+ frames.", line)
        if match: proc_status = "PASS"

        match = re.match(r"^Property proved.", line)
        if match: proc_status = "PASS"

        if keep_going:
            match = re.match(r"^Properties:  All = (\d+). Proved = (\d+). Disproved = (\d+). Undecided = (\d+).", line)
            if match:
                all_count = int(match[1])
                proved_count = int(match[2])
                disproved_count = int(match[3])
                undecided_count = int(match[4])
                if (
                    all_count != len(aiger_props) or
                    all_count != proved_count + disproved_count + undecided_count or
                    disproved_count != len(disproved) or
                    proved_count != len(proved)
                ):
                    log("WARNING: inconsistent status output")
                    proc_status = "UNKNOWN"
                elif proved_count == all_count:
                    proc_status = "PASS"
                elif disproved_count == 0:
                    proc_status = "UNKNOWN"
                else:
                    proc_status = "FAIL"

        return line

    def exit_callback(retcode):
        nonlocal procs_running
        if keep_going:
            procs_running -= 1
            if not procs_running:
                if proc_status == "FAIL" and mode == "bmc" and keep_going:
                    task.pass_unknown_asserts(dict(source="abc pdr", keep_going=True, engine=f"engine_{engine_idx}"))
                task.update_status(proc_status)
                task.summary.set_engine_status(engine_idx, proc_status)
                if proc_status != "UNKNOWN" and not keep_going:
                    task.terminate()
        else:
            aigsmt_exit_callback(task, engine_idx, proc_status,
                run_aigsmt=run_aigsmt, smtbmc_vcd=smtbmc_vcd, smtbmc_append=smtbmc_append, sim_append=sim_append)

    proc.output_callback = output_callback
    proc.register_exit_callback(exit_callback)
