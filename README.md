# NanoCluster-Drug-MD: GROMACS Pipeline for Protein-Stabilized Metal Nanocluster Drug-Loading Simulations

## Overview

This repository provides a reproducible, hardware-agnostic pipeline for
generating and running production molecular dynamics (MD) simulations of
drug-loading behavior in protein-scaffolded metal nanoclusters using GROMACS.
It was built out of a real research pipeline studying hydrophobic-drug
loading into a protein-templated bimetallic nanocluster, and is designed to
generalize to other protein-scaffold / metal-nanocluster / small-molecule
systems.

## Why this exists

Setting up production MD for nanocluster-protein-ligand systems involves a
lot of manual, error-prone bookkeeping: checkpoint-based restart logic across
heterogeneous compute environments (university clusters, personal GPUs, cloud
notebooks), correct thermostat/barostat group setup across
protein/ligand/metal-core components, and hardware-portable mdrun
configuration. There is no small, transparent, script-level reference
pipeline that covers this specific setup-and-restart loop for nanomedicine /
drug-delivery MD workflows. This repository fills that narrow gap.

## What's included

- `make_mdp.py` — generates a production `.mdp` tuned for CHARMM36-class
  protein-ligand systems (h-bond constraints, PME electrostatics,
  force-switch van der Waals, V-rescale thermostat, Parrinello-Rahman
  barostat).
- `run_md.py` — hardware-aware `mdrun` launcher with automatic
  checkpoint-based restart, safe fallback between append/no-append
  continuation, and configurable CPU/GPU/thread-MPI settings — built to
  survive migrating a single run across different machines, a common
  reality for compute-constrained academic labs.

## What's not included (yet)

The full downstream analysis pipeline (binding-kinetics extraction,
contact-residue identification, SASA-based pocket-burial analysis,
restraint-based extended sampling, and MM-PBSA binding free-energy
estimation) is part of an unpublished manuscript currently under
preparation/review. Those analysis scripts specific to that manuscript will
be released upon publication, to avoid disclosing unpublished findings ahead
of peer review. The two scripts here are the general-purpose infrastructure
layer, independent of any project-specific results.

## Status

Early, actively-developed release extracted from an ongoing academic
research project on protein-scaffolded metal-nanocluster drug delivery. Not
yet distributed via a package registry; being open-sourced so other labs
working on similar systems don't have to rebuild this setup/restart
infrastructure from scratch.

## License

MIT — see [LICENSE](./LICENSE).

## Citation

If you use this pipeline in your research, please cite this repository (a
manuscript citation will be added here upon publication).