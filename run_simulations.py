#!/usr/bin/env python3
"""
Automation script to run branch predictor simulations for Assignment 2.
Runs 60 total simulations: 30 for ARM and 30 for RISC-V.
"""

import os
import subprocess
import sys
from pathlib import Path

# Configuration
GEM5_PATH = os.environ.get("GEM5")
if not GEM5_PATH:
    print("Error: GEM5 environment variable not set")
    sys.exit(1)

# Simulation parameters
ARCHITECTURES = ["ARM", "RISCV"]
TABLE_SIZES = [16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
PROGRAM = "queens"
QUEENS_N = 10

# Predictor configurations: (label, bp_type, bp_bits)
PREDICTOR_CONFIGS = [
    ("Loc1", "LocalBP", 1),
    ("Loc2", "LocalBP", 2),
    ("Tour", "TournamentBP", 2),
]

# Base output directory
BASE_OUTPUT_DIR = Path("simulation_results")
BASE_OUTPUT_DIR.mkdir(exist_ok=True)

def run_simulation(arch, pred_label, bp_type, bp_size, bp_bits):
    """Run a single gem5 simulation."""

    # Create output directory
    output_dir = BASE_OUTPUT_DIR / arch / pred_label / f"size_{bp_size}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build command
    gem5_binary = f"{GEM5_PATH}/build/{arch}/gem5.opt"

    cmd = [
        gem5_binary,
        f"--outdir={output_dir}",
        "assignment2.py",
        f"--prog={PROGRAM}",
        f"--queens-N={QUEENS_N}",
        f"--bp={bp_type}",
        f"--bp_size={bp_size}",
        f"--bp_bits={bp_bits}",
    ]

    # Print simulation info
    sim_name = f"{arch}/{pred_label}/size_{bp_size}"
    print(f"\n{'='*60}")
    print(f"Running: {sim_name}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    # Run simulation
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,  # Show output in real-time
            text=True
        )
        print(f"✓ Completed: {sim_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {sim_name}")
        print(f"  Error: {e}")
        return False

def main():
    """Main execution function."""

    total_runs = len(ARCHITECTURES) * len(PREDICTOR_CONFIGS) * len(TABLE_SIZES)
    completed = 0
    failed = 0

    print(f"Starting {total_runs} simulations...")
    print(f"Architectures: {', '.join(ARCHITECTURES)}")
    print(f"Predictor configs: {', '.join([p[0] for p in PREDICTOR_CONFIGS])}")
    print(f"Table sizes: {TABLE_SIZES}")

    # Run all simulations
    for arch in ARCHITECTURES:
        for pred_label, bp_type, bp_bits in PREDICTOR_CONFIGS:
            for bp_size in TABLE_SIZES:
                success = run_simulation(arch, pred_label, bp_type, bp_size, bp_bits)
                if success:
                    completed += 1
                else:
                    failed += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total simulations: {total_runs}")
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    print(f"\nResults saved in: {BASE_OUTPUT_DIR.absolute()}")

if __name__ == "__main__":
    main()
