import numpy as np
import os

# 1. Target the first session's input file
# The '../' goes up one folder to find the 'data' directory
file_path = '../data/data/session_001/windows_input.npy'

if not os.path.exists(file_path):
    print(f"Error: Could not find {file_path}")
    exit()

print(f"Loading {file_path}...")
raw_data = np.load(file_path)
print(f"Original Shape: {raw_data.shape} (Windows, Channels, Samples)")

# 2. Extract a 1D chunk of PPG data
# Shape is (60 windows, 7 channels, 550 samples).
# We take window 0, channel 0, and ALL 550 samples.
ppg_signal = raw_data[0, 0, :] 

print(f"Extracted PPG length: {len(ppg_signal)} samples")
print(f"Original Range: {np.min(ppg_signal):.4f} to {np.max(ppg_signal):.4f}")

# 3. Scale to 16-bit signed integers (-32768 to 32767)
# We scale to 80% of the max range to leave headroom and avoid clipping in the FIR filter
max_val = np.max(np.abs(ppg_signal))
if max_val == 0: 
    max_val = 1 # Prevent division by zero
scale_factor = (32767 * 0.8) / max_val 

ppg_scaled = (ppg_signal * scale_factor).astype(int)

# Ensure strictly within 16-bit signed bounds (just in case)
ppg_scaled = np.clip(ppg_scaled, -32768, 32767)

# 4. Save to a text file for Verilog $readmemh
# Verilog expects 2's complement hexadecimal (e.g., -1 becomes FFFF)
output_file = 'ppg_input_vectors.hex'
with open(output_file, 'w') as f:
    for val in ppg_scaled:
        f.write(f"{val & 0xFFFF:04X}\n")

print(f"✅ Success! Saved {len(ppg_scaled)} samples to '{output_file}'")
print(f"Scaled Range: {np.min(ppg_scaled)} to {np.max(ppg_scaled)}")
print("You can now run your Verilog testbench!")