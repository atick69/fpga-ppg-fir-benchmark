import numpy as np
from scipy.signal import firwin

def get_ppg_coeffs(taps, fs=55.0, lowcut=0.5, highcut=5.0):
    # Design bandpass filter
    coeffs = firwin(taps, [lowcut/(fs/2), highcut/(fs/2)], pass_zero=False)
    # Convert to Q1.15 fixed point (16-bit)
    coeffs_int = np.round(coeffs * (2**15)).astype(int)
    # Return only the first half (symmetric folding)
    return coeffs_int[: (taps+1)//2 ]

# Generate for 31, 15, and 5 taps
for taps in [31, 15, 5]:
    c = get_ppg_coeffs(taps)
    print(f"\n// {taps}-tap PPG Coefficients (0.5 - 5.0 Hz)")
    print("initial begin")
    for i, val in enumerate(c):
        print(f"    cb{taps}[{i}] = {val};")
    print("end")