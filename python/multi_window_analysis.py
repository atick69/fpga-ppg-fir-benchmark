import numpy as np
import os
from scipy.signal import butter, lfilter, filtfilt

fs = 55.0
b, a = butter(2, [0.5/(fs/2), 5.0/(fs/2)], btype='band')
coeffs = [0, 20, 24, -15, -140, -377, -697, -991, -1083, -791, 0, 1263, 
          2804, 4300, 5389, 5787, 5389, 4300, 2804, 1263, 0, -791, 
          -1083, -991, -697, -377, -140, -15, 24, 20, 0]

def xlag(x, r, maxlag=30):
    x = x - x.mean(); r = r - r.mean()
    best, bl = -1e30, 0
    for l in range(-maxlag, maxlag + 1):
        c = np.dot(x[max(0, l):len(x) + min(0, l)], r[max(0, -l):len(r) + min(0, -l)])
        if c > best: best, bl = c, l
    return bl

fir_lags = []
iir_lags = []
base_dir = '../data/data'
sessions = [d for d in os.listdir(base_dir) if d.startswith('session_')]

print(f"Processing {len(sessions)} sessions...")
for sess in sessions:
    file_path = os.path.join(base_dir, sess, 'windows_input.npy')
    if not os.path.exists(file_path): continue
    data = np.load(file_path) # shape (60, 7, 550)
    
    for w in range(data.shape[0]):
        raw_float = data[w, 0, :].astype(float)
        max_val = np.max(np.abs(raw_float))
        if max_val == 0: continue
        
        # FIX: Explicitly convert to integer after scaling
        raw_int = np.round((raw_float / max_val) * (32767 * 0.8)).astype(int)
        raw_int = np.clip(raw_int, -32768, 32767)
        
        # FIR Model
        fir_out = []
        shift_reg = [0] * 31
        for i in range(len(raw_int)):
            accum = sum(shift_reg[k] * coeffs[k] for k in range(31))
            scaled = (accum + (1 << 14)) >> 15
            if scaled > 32767: scaled = 32767
            elif scaled < -32768: scaled = -32768
            fir_out.append(scaled)
            for j in range(30, 0, -1):
                shift_reg[j] = shift_reg[j-1]
            shift_reg[0] = raw_int[i]
        fir_out = np.array(fir_out)
        
        # References (use the float version for Python filtering)
        ref = filtfilt(b, a, raw_float)
        iir = lfilter(b, a, raw_float)
        
        delay = 17
        fir_shifted = fir_out[delay:]
        iir_shifted = iir[:len(fir_shifted)]
        ref_shifted = ref[:len(fir_shifted)]
        
        fir_lags.append(xlag(fir_shifted, ref_shifted))
        iir_lags.append(xlag(iir_shifted, ref_shifted))

print(f"\nTotal Windows Analyzed: {len(fir_lags)}")
print(f"FIR Lags: Median {np.median(fir_lags):+.1f}, Mean {np.mean(fir_lags):+.1f} +/- {np.std(fir_lags):.1f}")
print(f"IIR Lags: Median {np.median(iir_lags):+.1f}, Mean {np.mean(iir_lags):+.1f} +/- {np.std(iir_lags):.1f}")