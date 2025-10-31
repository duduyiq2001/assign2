#!/usr/bin/env python3
"""
Script to extract CPI data from gem5 simulations and generate plots.
"""

import os
import re
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Configuration
BASE_OUTPUT_DIR = Path("simulation_results")
ARCHITECTURES = ["ARM", "RISCV"]
PREDICTOR_CONFIGS = ["Loc1", "Loc2", "Tour"]
TABLE_SIZES = [16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]

def extract_cpi(stats_file):
    """Extract CPI value from stats.txt file."""
    try:
        with open(stats_file, 'r') as f:
            content = f.read()
            # Look for system.processor.cores.core.cpi or similar pattern
            # The exact stat name might vary, so we'll search for CPI-related stats
            patterns = [
                r'system\.processor\.cores\.core\.cpi\s+([0-9.]+)',
                r'system\.processor\.cores\d*\.core\.cpi\s+([0-9.]+)',
                r'board\.processor\.cores\.core\.cpi\s+([0-9.]+)',
                r'board\.processor\.cores\d*\.core\.cpi\s+([0-9.]+)',
            ]

            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    return float(match.group(1))

            print(f"Warning: CPI not found in {stats_file}")
            return None
    except Exception as e:
        print(f"Error reading {stats_file}: {e}")
        return None

def collect_data():
    """Collect CPI data from all simulations."""
    data = {}

    for arch in ARCHITECTURES:
        data[arch] = {}
        for pred_config in PREDICTOR_CONFIGS:
            data[arch][pred_config] = {}
            for size in TABLE_SIZES:
                stats_file = BASE_OUTPUT_DIR / arch / pred_config / f"size_{size}" / "stats.txt"

                if stats_file.exists():
                    cpi = extract_cpi(stats_file)
                    if cpi is not None:
                        data[arch][pred_config][size] = cpi
                        print(f"✓ {arch}/{pred_config}/size_{size}: CPI = {cpi:.4f}")
                    else:
                        print(f"✗ {arch}/{pred_config}/size_{size}: CPI extraction failed")
                else:
                    print(f"✗ {arch}/{pred_config}/size_{size}: stats.txt not found")

    return data

def plot_data(data):
    """Generate plots for CPI vs table size."""

    # Create plots directory
    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)

    # Colors and markers for each predictor
    styles = {
        'Loc1': {'color': 'blue', 'marker': 'o', 'label': 'Local 1-bit'},
        'Loc2': {'color': 'green', 'marker': 's', 'label': 'Local 2-bit'},
        'Tour': {'color': 'red', 'marker': '^', 'label': 'Tournament 2-bit'},
    }

    for arch in ARCHITECTURES:
        # Create figure
        plt.figure(figsize=(12, 8))

        # Plot each predictor configuration
        for pred_config in PREDICTOR_CONFIGS:
            if pred_config in data[arch] and data[arch][pred_config]:
                # Extract sizes and CPIs
                sizes = sorted(data[arch][pred_config].keys())
                cpis = [data[arch][pred_config][size] for size in sizes]

                # Plot
                plt.plot(sizes, cpis,
                        color=styles[pred_config]['color'],
                        marker=styles[pred_config]['marker'],
                        linewidth=2,
                        markersize=8,
                        label=styles[pred_config]['label'])

        # Formatting
        plt.xlabel('Branch Predictor Table Size', fontsize=12)
        plt.ylabel('CPI (Cycles Per Instruction)', fontsize=12)
        plt.title(f'CPI vs Branch Predictor Table Size ({arch})', fontsize=14, fontweight='bold')
        plt.xscale('log', base=2)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.legend(fontsize=11, loc='best')
        plt.tight_layout()

        # Save plot
        plot_file = plots_dir / f"cpi_vs_size_{arch}.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved plot: {plot_file}")

        # Also create a separate plot for each predictor (optional, for clarity)
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle(f'CPI vs Table Size - {arch} Architecture', fontsize=14, fontweight='bold')

        for idx, pred_config in enumerate(PREDICTOR_CONFIGS):
            ax = axes[idx]
            if pred_config in data[arch] and data[arch][pred_config]:
                sizes = sorted(data[arch][pred_config].keys())
                cpis = [data[arch][pred_config][size] for size in sizes]

                ax.plot(sizes, cpis,
                       color=styles[pred_config]['color'],
                       marker=styles[pred_config]['marker'],
                       linewidth=2,
                       markersize=8)

                ax.set_xlabel('Table Size', fontsize=11)
                ax.set_ylabel('CPI', fontsize=11)
                ax.set_title(styles[pred_config]['label'], fontsize=12)
                ax.set_xscale('log', base=2)
                ax.grid(True, alpha=0.3, linestyle='--')

        plt.tight_layout()
        plot_file_separate = plots_dir / f"cpi_vs_size_{arch}_separate.png"
        plt.savefig(plot_file_separate, dpi=300, bbox_inches='tight')
        print(f"✓ Saved plot: {plot_file_separate}")

        plt.close('all')

def generate_summary_table(data):
    """Generate a summary table of results."""

    print("\n" + "="*80)
    print("SUMMARY TABLE")
    print("="*80)

    for arch in ARCHITECTURES:
        print(f"\n{arch} Architecture:")
        print("-" * 80)
        print(f"{'Size':<10} {'Loc1 CPI':<12} {'Loc2 CPI':<12} {'Tour CPI':<12}")
        print("-" * 80)

        for size in TABLE_SIZES:
            loc1_cpi = data[arch].get('Loc1', {}).get(size, None)
            loc2_cpi = data[arch].get('Loc2', {}).get(size, None)
            tour_cpi = data[arch].get('Tour', {}).get(size, None)

            loc1_str = f"{loc1_cpi:.4f}" if loc1_cpi else "N/A"
            loc2_str = f"{loc2_cpi:.4f}" if loc2_cpi else "N/A"
            tour_str = f"{tour_cpi:.4f}" if tour_cpi else "N/A"

            print(f"{size:<10} {loc1_str:<12} {loc2_str:<12} {tour_str:<12}")

def main():
    """Main execution function."""

    if not BASE_OUTPUT_DIR.exists():
        print(f"Error: Simulation results directory not found: {BASE_OUTPUT_DIR}")
        print("Run run_simulations.py first to generate data.")
        return

    print("Collecting CPI data from simulation results...")
    data = collect_data()

    print("\nGenerating plots...")
    plot_data(data)

    generate_summary_table(data)

    print("\n" + "="*80)
    print("Done! Plots saved in ./plots/")
    print("="*80)

if __name__ == "__main__":
    main()
