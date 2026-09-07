"""
make_mdp.py

Generates a production-MD .mdp file for GROMACS, tuned for CHARMM36-class
protein-ligand(-metal core) systems in explicit solvent (CPU-only capable).

Usage:
    Place npt.gro, npt.cpt, topol.top, and index.ndx in the project directory,
    then run this script to generate md_prod.mdp.

Note: nsteps/dt define total simulation length; adjust as needed for your system.
Thermostat/barostat groups (tc-grps) must match group names in your index.ndx.
"""
import os
import sys

PROJECT_DIR = "."
REQUIRED_INPUT_FILES = ["npt.gro", "npt.cpt", "topol.top", "index.ndx"]

def create_production_mdp():
    missing = [f for f in REQUIRED_INPUT_FILES if not os.path.exists(os.path.join(PROJECT_DIR, f))]
    if missing:
        print("Error: Required input files not found:", missing)
        sys.exit(1)

    md_content = """
; GROMACS Production MD (CPU-only compatible)
title                   = Production MD
integrator              = md
nsteps                  = 25000000  ; 25,000,000 x 0.002 ps = 50,000 ps = 50 ns
dt                      = 0.002     ; 2 fs, requires h-bond constraints

nstxout                 = 0         ; no .trr velocity/force output (disk savings)
nstvout                 = 0
nstfout                 = 0
nstenergy               = 25000     ; every 50 ps
nstlog                  = 25000     ; every 50 ps
nstxout-compressed      = 25000     ; every 50 ps -> 1000 frames over 50 ns
compressed-x-grps       = System

continuation            = yes
constraint_algorithm    = lincs
constraints             = h-bonds
lincs_iter              = 1
lincs_order             = 4

cutoff-scheme           = Verlet
ns_type                 = grid
nstlist                 = 20
verlet-buffer-tolerance = 0.005
rcoulomb                = 1.2
vdwtype                 = cutoff
vdw-modifier            = force-switch   ; recommended for CHARMM36-class force fields
rvdw-switch             = 1.0
rvdw                    = 1.2
DispCorr                = no        ; disable if using CHARMM36 (parameterized without dispersion tail correction)

coulombtype             = PME
pme_order               = 4
fourierspacing          = 0.16

tcoupl                  = V-rescale
tc-grps                 = Protein_NonProtein   ; EDIT: replace with your own tc-grps names
tau_t                   = 0.1     0.1
ref_t                   = 298.15  298.15

pcoupl                  = Parrinello-Rahman
pcoupltype              = isotropic
tau_p                   = 5.0
ref_p                   = 1.0
compressibility         = 4.5e-5

pbc                     = xyz
gen_vel                 = no
""".strip()

    out_path = os.path.join(PROJECT_DIR, "md_prod.mdp")
    with open(out_path, "w") as f:
        f.write(md_content)
    print(f"Successfully created {out_path}")

if __name__ == "__main__":
    create_production_mdp()