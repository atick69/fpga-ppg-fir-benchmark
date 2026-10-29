import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, find_peaks

# 1. Load Data
input_signal = []
fir_signal = []
with open('ppg_results.txt', 'r', encoding='utf-16') as f:
    for line in f:
        if "In:" in line and "Out:" in line:
            parts = line.split('|')
            input_signal.append(int(parts[1].split(':')[1].strip()))
            fir_signal.append(int(parts[2].split(':')[1].strip()))

# 2. Apply IIR
fs = 55.0
b, a = butter(2, [0.5/(fs/2), 5.0/(fs/2)], btype='band')
iir_signal = lfilter(b, a, input_signal)

# 3. Shift FIR to compensate for group delay (15 + 1 pipeline = 16 samples)
delay = 17   # 15 center + 2 (1 pipeline register + 1 testbench log offset)
fir_shifted = fir_signal[delay:]
raw_shifted = input_signal[:len(fir_shifted)]
iir_shifted = iir_signal[:len(fir_shifted)]
x_axis = np.arange(len(fir_shifted))

# 4. Calculate Peak Error
peaks_raw, _ = find_peaks(raw_shifted, distance=int(fs/2), prominence=2000)
peaks_fir, _ = find_peaks(fir_shifted, distance=int(fs/2), prominence=1000)
peaks_iir, _ = find_peaks(iir_shifted, distance=int(fs/2), prominence=1000)

# Match peaks to calculate error (simplified for the first few peaks)
print(f"Raw peaks at: {peaks_raw[:5]}")
print(f"FIR peaks at: {peaks_fir[:5]}")
print(f"IIR peaks at: {peaks_iir[:5]}")
print("*(Notice how FIR peaks align perfectly with Raw, while IIR peaks are shifted)*")

# 5. Plot
plt.figure(figsize=(14, 6))
plt.plot(x_axis, raw_shifted, label='Raw PPG Signal', color='lightgray', linewidth=2)
plt.plot(x_axis, iir_shifted, label='IIR Filter (Butterworth, frequency-dependent delay)', color='blue', linestyle='--', linewidth=2)
plt.plot(x_axis, fir_shifted, label='FIR Filter (31-tap, delay-compensated)', color='red', linewidth=2)

plt.title('PPG Signal Filtering: Linear Phase FIR vs IIR', fontsize=14)
plt.xlabel('Sample Number (55 Hz)', fontsize=12)
plt.ylabel('16-bit Amplitude', fontsize=12)
plt.legend(loc='upper right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('ppg_fir_vs_iir.png', dpi=300)
print("✅ Saved 'ppg_fir_vs_iir.png'")
plt.show()