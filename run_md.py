"""
run_md.py

Hardware-aware GROMACS production-MD launcher with automatic checkpoint-based
restart. Designed to survive migrating a single run across different machines
(CPU-only clusters, workstation GPUs, cloud notebooks) using GROMACS's
checkpoint (.cpt) continuation mechanism.

Edit N_MPI / N_OMP / CPU_FLAGS below to match your own hardware.
"""
import os
import sys
import shutil
import subprocess
import platform

PROJECT_DIR = "."
DEFFNM = "md_0_1"
MAX_HOURS = None
GMX_PATH = None
REQUIRED_FOR_FRESH_START = ["md_prod.mdp", "npt.gro", "npt.cpt", "topol.top", "index.ndx"]

def find_gmx():
    if GMX_PATH and os.path.exists(GMX_PATH):
        return GMX_PATH
    candidates = ["gmx_mpi.exe", "gmx.exe", "gmx_mpi", "gmx"]
    if platform.system() != "Windows":
        candidates.append("/usr/local/gromacs/bin/gmx")
    for exe in candidates:
        path = shutil.which(exe)
        if path:
            return path
    raise FileNotFoundError("GROMACS executable not found. Install it or set GMX_PATH.")

GMX = find_gmx()

# EDIT: set these to match your own hardware.
# Example below: 2 sockets x 6 physical cores x 2 (HT) = 24 logical cores,
# split as 4 thread-MPI ranks x 6 OpenMP threads/rank.
N_MPI = 4
N_OMP = 6
CPU_FLAGS = f"-ntmpi {N_MPI} -ntomp {N_OMP} -pin on"
# -dlb left at GROMACS's default "auto": enables dynamic load balancing only
# when real imbalance is detected, avoiding unnecessary rebalancing overhead.

def run_cmd(cmd_list, description):
    print(f"\n>>> {description}")
    print("$ " + " ".join(cmd_list))
    try:
        result = subprocess.run(cmd_list, cwd=PROJECT_DIR, check=False)
        return result.returncode
    except Exception as e:
        print(f"Exception during subprocess execution: {e}")
        return -1

def run_production_md():
    print(f"Working directory: {os.path.abspath(PROJECT_DIR)}")
    tpr_path = os.path.join(PROJECT_DIR, f"{DEFFNM}.tpr")
    cpt_path = os.path.join(PROJECT_DIR, f"{DEFFNM}.cpt")
    maxh_flag = ["-maxh", str(MAX_HOURS)] if MAX_HOURS else []

    if not os.path.exists(tpr_path):
        missing = [f for f in REQUIRED_FOR_FRESH_START if not os.path.exists(os.path.join(PROJECT_DIR, f))]
        if missing:
            print("Error: Missing required files for fresh start:", missing)
            sys.exit(1)
        grompp_cmd = [GMX, "grompp", "-f", "md_prod.mdp", "-c", "npt.gro", "-t", "npt.cpt",
                      "-p", "topol.top", "-n", "index.ndx", "-o", f"{DEFFNM}.tpr", "-maxwarn", "2"]
        rc = run_cmd(grompp_cmd, "Generating binary run input (grompp)")
        if rc != 0:
            print("Error: grompp failed. Check topology and coordinate files.")
            sys.exit(1)
    else:
        print(f"{DEFFNM}.tpr already exists — skipping grompp.")

    mdrun_base = [GMX, "mdrun", "-v", "-deffnm", DEFFNM] + maxh_flag + CPU_FLAGS.split()

    if os.path.exists(cpt_path):
        rc = run_cmd(mdrun_base + ["-cpi", f"{DEFFNM}.cpt", "-append"], "Continuing from checkpoint (append)")
        if rc != 0:
            print("Append failed, attempting noappend continuation...")
            rc = run_cmd(mdrun_base + ["-cpi", f"{DEFFNM}.cpt", "-noappend"], "Continuing from checkpoint (noappend)")
            if rc != 0:
                print("Error: Checkpoint restart failed.")
                sys.exit(1)
    else:
        rc = run_cmd(mdrun_base, "Starting fresh production mdrun")
        if rc != 0:
            print("Error: mdrun failed.")
            sys.exit(1)

    print("\nProduction MD completed successfully.")

if __name__ == "__main__":
    run_production_md()