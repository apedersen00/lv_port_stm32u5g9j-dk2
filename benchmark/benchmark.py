import os
import re
import subprocess
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from saleae import automation

# --- Configuration ---

# 1. Set the project's root directory.
# The script assumes it's located in 'project_root/benchmark/'.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 2. Define file paths relative to the project root.
MAIN_C_PATH = os.path.join(PROJECT_ROOT, 'Core/Src', 'main.c')
LV_CONF_H_PATH = os.path.join(PROJECT_ROOT, 'Core/Inc/lv_conf.h') # Adjust if lv_conf.h is elsewhere
CMAKE_TOOLCHAIN_PATH = os.path.join(PROJECT_ROOT, 'cmake/gcc-arm-none-eabi.cmake')
BUILD_DIR = os.path.join(PROJECT_ROOT, 'build')
FLASH_SCRIPT_PATH = os.path.join(PROJECT_ROOT, 'flash.bat')

# lv_demo_widgets();
# demo_screen_blit();
# demo_screen_blend();
# demo_screen_text();
# demo_bitmap();
# demo_bitmap_blend();

# 3. Define the benchmark configurations to run.
# Add or remove dictionaries to this list to customize your tests.
BENCHMARK_CONFIGS = [
    {'name': 'Widgets, Nema, GCC O3'        , 'demo': 0, 'nema_gfx': 1, 'dma2d': 0, 'opt': '3'},
    {'name': 'Screen Fill, Nema, GCC O3'    , 'demo': 1, 'nema_gfx': 1, 'dma2d': 0, 'opt': '3'},
    {'name': 'Screen Blend, Nema, GCC O3'   , 'demo': 2, 'nema_gfx': 1, 'dma2d': 0, 'opt': '3'},
    {'name': 'Screen Text, Nema, GCC O3'    , 'demo': 3, 'nema_gfx': 1, 'dma2d': 0, 'opt': '3'},
    {'name': 'Bitmap, Nema, GCC O3'         , 'demo': 4, 'nema_gfx': 1, 'dma2d': 0, 'opt': '3'},
    {'name': 'Bitmap Blend, Nema, GCC O3'   , 'demo': 5, 'nema_gfx': 1, 'dma2d': 0, 'opt': '3'},

    {'name': 'Widgets, Nema, GCC Os'        , 'demo': 0, 'nema_gfx': 1, 'dma2d': 0, 'opt': 's'},
    {'name': 'Screen Fill, Nema, GCC Os'    , 'demo': 1, 'nema_gfx': 1, 'dma2d': 0, 'opt': 's'},
    {'name': 'Screen Blend, Nema, GCC Os'   , 'demo': 2, 'nema_gfx': 1, 'dma2d': 0, 'opt': 's'},
    {'name': 'Screen Text, Nema, GCC Os'    , 'demo': 3, 'nema_gfx': 1, 'dma2d': 0, 'opt': 's'},
    {'name': 'Bitmap, Nema, GCC Os'         , 'demo': 4, 'nema_gfx': 1, 'dma2d': 0, 'opt': 's'},
    {'name': 'Bitmap Blend, Nema, GCC Os'   , 'demo': 5, 'nema_gfx': 1, 'dma2d': 0, 'opt': 's'},

    {'name': 'Widgets, DMA2D, GCC O3'       , 'demo': 0, 'nema_gfx': 0, 'dma2d': 1, 'opt': '3'},
    {'name': 'Screen Fill, DMA2D, GCC O3'   , 'demo': 1, 'nema_gfx': 0, 'dma2d': 1, 'opt': '3'},
    {'name': 'Screen Blend, DMA2D, GCC O3'  , 'demo': 2, 'nema_gfx': 0, 'dma2d': 1, 'opt': '3'},
    {'name': 'Screen Text, DMA2D, GCC O3'   , 'demo': 3, 'nema_gfx': 0, 'dma2d': 1, 'opt': '3'},
    {'name': 'Bitmap, DMA2D, GCC O3'        , 'demo': 4, 'nema_gfx': 0, 'dma2d': 1, 'opt': '3'},
    {'name': 'Bitmap Blend, DMA2D, GCC O3'  , 'demo': 5, 'nema_gfx': 0, 'dma2d': 1, 'opt': '3'},

    {'name': 'Widgets, DMA2D, GCC Os'       , 'demo': 0, 'nema_gfx': 0, 'dma2d': 1, 'opt': 's'},
    {'name': 'Screen Fill, DMA2D, GCC Os'   , 'demo': 1, 'nema_gfx': 0, 'dma2d': 1, 'opt': 's'},
    {'name': 'Screen Blend, DMA2D, GCC Os'  , 'demo': 2, 'nema_gfx': 0, 'dma2d': 1, 'opt': 's'},
    {'name': 'Screen Text, DMA2D, GCC Os'   , 'demo': 3, 'nema_gfx': 0, 'dma2d': 1, 'opt': 's'},
    {'name': 'Bitmap, DMA2D, GCC Os'        , 'demo': 4, 'nema_gfx': 0, 'dma2d': 1, 'opt': 's'},
    {'name': 'Bitmap Blend, DMA2D, GCC Os'  , 'demo': 5, 'nema_gfx': 0, 'dma2d': 1, 'opt': 's'},

    {'name': 'Widgets, SW, GCC O3'       , 'demo': 0, 'nema_gfx': 0, 'dma2d': 0, 'opt': '3'},
    {'name': 'Screen Fill, SW, GCC O3'   , 'demo': 1, 'nema_gfx': 0, 'dma2d': 0, 'opt': '3'},
    {'name': 'Screen Blend, SW, GCC O3'  , 'demo': 2, 'nema_gfx': 0, 'dma2d': 0, 'opt': '3'},
    {'name': 'Screen Text, SW, GCC O3'   , 'demo': 3, 'nema_gfx': 0, 'dma2d': 0, 'opt': '3'},
    {'name': 'Bitmap, SW, GCC O3'        , 'demo': 4, 'nema_gfx': 0, 'dma2d': 0, 'opt': '3'},
    {'name': 'Bitmap Blend, SW, GCC O3'  , 'demo': 5, 'nema_gfx': 0, 'dma2d': 0, 'opt': '3'},

    {'name': 'Widgets, SW, GCC Os'       , 'demo': 0, 'nema_gfx': 0, 'dma2d': 0, 'opt': 's'},
    {'name': 'Screen Fill, SW, GCC Os'   , 'demo': 1, 'nema_gfx': 0, 'dma2d': 0, 'opt': 's'},
    {'name': 'Screen Blend, SW, GCC Os'  , 'demo': 2, 'nema_gfx': 0, 'dma2d': 0, 'opt': 's'},
    {'name': 'Screen Text, SW, GCC Os'   , 'demo': 3, 'nema_gfx': 0, 'dma2d': 0, 'opt': 's'},
    {'name': 'Bitmap, SW, GCC Os'        , 'demo': 4, 'nema_gfx': 0, 'dma2d': 0, 'opt': 's'},
    {'name': 'Bitmap Blend, SW, GCC Os'  , 'demo': 5, 'nema_gfx': 0, 'dma2d': 0, 'opt': 's'},
]

# --- Core Functions ---

def run_command(command, working_dir):
    """Executes a shell command and raises an exception on failure."""
    print(f"Running command: '{' '.join(command)}' in '{working_dir}'")
    try:
        result = subprocess.run(
            command,
            cwd=working_dir,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(command)}")
        print(e.stderr)
        raise

def modify_file(file_path, pattern, replacement):
    """Searches a file for a pattern and replaces the line."""
    try:
        with open(file_path, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            for line in lines:
                f.write(re.sub(pattern, replacement, line))
    except FileNotFoundError:
        print(f"Error: Could not find file at {file_path}")
        raise

def setup_source_files(config):
    """Modifies source files based on the given benchmark configuration."""
    print("--- Modifying source files ---")
    # 1. Modify demo in main.c
    modify_file(
        MAIN_C_PATH,
        r"(^\s*#define\s+DEMO\s+)\w+",
        f"\\g<1>{config['demo']}"
    )
    # 2. Modify lv_conf.h
    modify_file(
        LV_CONF_H_PATH,
        r"(^\s*#define\s+LV_USE_NEMA_GFX\s+)\w+",
        f"\\g<1>{config['nema_gfx']}"
    )
    modify_file(
        LV_CONF_H_PATH,
        r"(^\s*#define\s+LV_USE_DRAW_DMA2D\s+)\w+",
        f"\\g<1>{config['dma2d']}"
    )
    # 3. Modify optimization level in CMake toolchain file
    modify_file(
        CMAKE_TOOLCHAIN_PATH,
        r'(-O)[0-9s]+',
        f"-O{config['opt']}"
    )
    print("Source files modified successfully.")

def build_project():
    """Builds the CMake project."""
    print("--- Building project ---")
    # Configure step (optional, but good practice)
    run_command(['cmake', '-B', BUILD_DIR, '-S', PROJECT_ROOT], PROJECT_ROOT)
    # Build step
    run_command(['cmake', '--build', BUILD_DIR, '--clean-first'], PROJECT_ROOT)
    print("Build complete.")

def flash_target():
    """Flashes the binary to the target using the provided batch script."""
    print("--- Flashing target ---")
    run_command([FLASH_SCRIPT_PATH], PROJECT_ROOT)
    print("Flashing complete. Target should be running.")

def measure_with_saleae(name, output_dir, capture_duration_seconds=5):
    """Performs a capture with a connected Saleae device."""
    print("--- Starting Saleae measurement ---")
    os.makedirs(output_dir, exist_ok=True)

    try:
        with automation.Manager.connect(port=10430) as manager:
            device_configuration = automation.LogicDeviceConfiguration(
                enabled_digital_channels=[0, 1, 2, 3],
                digital_sample_rate=12_000_000
            )
            capture_configuration = automation.CaptureConfiguration(
                capture_mode=automation.TimedCaptureMode(duration_seconds=capture_duration_seconds)
            )

            with manager.start_capture(
                device_configuration=device_configuration,
                capture_configuration=capture_configuration
            ) as capture:
                print(f"Saleae capturing for {capture_duration_seconds} seconds...")
                capture.wait()
                print("Capture finished.")
                
                # Export raw data for plotting
                csv_path = os.path.join(output_dir, f'{name}.csv')
                capture.export_raw_data_csv(directory=output_dir, digital_channels=[0, 1, 2, 3])
                run_command(['mv', 'benchmark/saleae_out/digital.csv', f'benchmark/saleae_out/{name}.csv'], PROJECT_ROOT)

                print(f"Data exported to {output_dir}")
                return csv_path
    except Exception as e:
        print(f"Could not connect to Saleae. Is Logic 2 running? Error: {e}")
        print("Skipping measurement.")
        return None


# --- Data Processing and Plotting (Adapted from your script) ---

def add_transition_points(time, values):
    """Helper function to make step plots look clean."""
    new_time = [time[0]]
    new_values = [values[0]]
    for i in range(1, len(time)):
        if values[i] != values[i - 1]:
            new_time.append(time[i])
            new_values.append(values[i - 1])
        new_time.append(time[i])
        new_values.append(values[i])
    return new_time, new_values

def find_first_pulse_edges(data):
    """Finds the start and end index of the first high pulse in a data series."""
    high_edge = (data == 1) & (data.shift(1) == 0)
    low_edge = (data == 0) & (data.shift(1) == 1)
    
    try:
        start_idx = high_edge[high_edge].index[0]
        end_idx = low_edge[low_edge & (low_edge.index > start_idx)].index[0]
        return start_idx, end_idx
    except IndexError:
        return None, None # No pulse found

def process_and_plot_results(config_name, csv_path, results_file='README.md'):
    """Analyzes captured data, generates plots, and appends results to a file."""
    if not csv_path or not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}. Skipping processing.")
        return

    print(f"--- Processing results for {config_name} ---")
    data = pd.read_csv(csv_path)
    # Rename columns to be more descriptive based on your hardware hookups
    # Example: Channel 0 -> flush_cb, Channel 1 -> refr_invalid_areas, etc.
    data.rename(columns={
        'Channel 0': 'lv_timer_handler',
        'Channel 1': 'refr_invalid_areas',
        'Channel 2': 'something_else',
        'Channel 3': 'other_signal' # Adjust as needed
    }, inplace=True)
    
    time_s = data['Time [s]']
    
    # Create plot
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle(f'{config_name}', fontsize=16)
    
    signals = ['lv_timer_handler', 'refr_invalid_areas']
    metrics = {}

    for ax, signal_name in zip(axs, signals):
        if signal_name in data.columns:
            signal_data = data[signal_name]
            plot_time, plot_signal = add_transition_points(time_s.tolist(), signal_data.tolist())
            ax.plot(plot_time, plot_signal, linewidth=2)
            ax.set_title(signal_name)
            ax.set_yticks([0, 1])
            ax.grid(True, axis='y')

            # Calculate and display timing for the first pulse
            start_idx, end_idx = find_first_pulse_edges(signal_data)
            if start_idx is not None and end_idx is not None:
                start_t, end_t = time_s[start_idx], time_s[end_idx]
                duration_ms = (end_t - start_t) * 1000
                metrics[signal_name] = duration_ms
                ax.axvspan(start_t, end_t, color='orange', alpha=0.3)
                ax.text((start_t + end_t) / 2, 0.5, f'{duration_ms:.2f} ms',
                        ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", fc="yellow", lw=1))

    # Zoom in on the first lv_timer_handler event
    if 'lv_timer_handler' in metrics:
        start_idx, end_idx = find_first_pulse_edges(data['lv_timer_handler'])
        if start_idx and end_idx:
            axs[0].set_xlim(time_s[start_idx] - 0.005, time_s[end_idx] + 0.005)

    axs[-1].set_xlabel('Time [s]')
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # Save plot
    waveforms_dir = os.path.join(PROJECT_ROOT, 'benchmark', 'waveforms')
    os.makedirs(waveforms_dir, exist_ok=True)
    plot_path = os.path.join(waveforms_dir, f'{config_name}.png')
    fig.savefig(plot_path)
    plt.close(fig)
    print(f"Waveform plot saved to {plot_path}")

    # Write summary to results file
    with open(results_file, 'a', encoding='utf-8') as f:
        f.write(f"\n## Results for: {config_name}\n\n")
        f.write("| Metric             | Duration (ms) |\n")
        f.write("|--------------------|---------------|\n")
        for name, value in metrics.items():
            f.write(f"| {name:<18} | {value:>13.2f} |\n")
        f.write(f"\n![Waveform](./waveforms/{config_name}.png)\n")
        f.write("\n---\n")
    print(f"Results appended to {results_file}")

# --- Main Execution ---

def main():
    """Main benchmark execution loop."""
    results_readme = os.path.join(PROJECT_ROOT, 'benchmark', 'README.md')
    # Clear previous results
    with open(results_readme, 'w', encoding='utf-8') as f:
        f.write("# Benchmark Results\n")

    for config in BENCHMARK_CONFIGS:
        config_name = config['name']
        print(f"\n{'='*60}\nRunning Benchmark: {config_name}\n{'='*60}")
        try:
            # 1. Modify files
            setup_source_files(config)

            # 2. Build
            build_project()

            # 3. Flash
            flash_target()
            print("Waiting for device to boot...")
            time.sleep(3) # Wait for device to initialize

            # 4. Measure
            name = config_name.lower().replace(' ', '_').replace(',', '')
            saleae_output_dir = os.path.join(PROJECT_ROOT, 'benchmark', 'saleae_out')
            captured_csv_path = measure_with_saleae(name, saleae_output_dir)

            # 5. Process and Plot
            if captured_csv_path:
                process_and_plot_results(name, captured_csv_path, results_readme)

        except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
            print(f"\n!!! Benchmark '{config_name}' failed: {e} !!!")
            continue
    
    print("\nAll benchmark configurations have been processed.")


if __name__ == "__main__":
    # Ensure necessary libraries are installed
    try:
        import pandas
        import numpy
        import matplotlib
        import saleae
    except ImportError as e:
        print(f"Missing required library: {e.name}. Please install it using pip.")
        print("Example: pip install pandas numpy matplotlib saleae-automation")
    else:
        main()
