import numpy as np
from scipy.signal import butter, lfilter, filtfilt, find_peaks, freqz

FS          = 55.0
FIR_LATENCY = 17
GATE_TOL    = 8      # tolerance used for the headline statistic
PROM        = 1000
DIST        = 27

# 1. Load ----------------------------------------------------------------
raw_l, fir_l = [], []
with open('ppg_results.txt', 'r', encoding='utf-16') as f:
    for line in f:
        if "In:" in line and "Out:" in line:
            p = line.split('|')
            raw_l.append(int(p[1].split(':')[1].strip()))
            fir_l.append(int(p[2].split(':')[1].strip()))
raw = np.asarray(raw_l, float)
fir = np.asarray(fir_l, float)

# 2. Filters -------------------------------------------------------------
b, a = butter(2, [0.5/(FS/2), 5.0/(FS/2)], btype='band')

# NOTE: the zero-phase reference shares the IIR's band edges, so it slightly
# favours the same passband. Harmless for this comparison, but state it.
ref_full = filtfilt(b, a, raw)
iir_full = lfilter(b, a, raw)

# 3. Align ---------------------------------------------------------------
fir_shifted = fir[FIR_LATENCY:]          # compensate the fixed FIR latency
n           = len(fir_shifted)
ref         = ref_full[:n]
iir         = iir_full[:n]

# 4. Helpers -------------------------------------------------------------
def xlag(x, r, maxlag=30):
    x = x - x.mean(); r = r - r.mean()
    best, bl = -1e30, 0
    for l in range(-maxlag, maxlag + 1):
        c = np.dot(x[max(0, l):len(x) + min(0, l)],
                   r[max(0, -l):len(r) + min(0, -l)])
        if c > best:
            best, bl = c, l
    return bl

def match_peaks(sig, ref_sig):
    """One-to-one greedy match; returns all pairs, not just in-gate ones."""
    pr, _ = find_peaks(ref_sig, distance=DIST, prominence=PROM)
    ps, _ = find_peaks(sig,     distance=DIST, prominence=PROM)
    cand = sorted((abs(q - p), i, j, q - p)
                  for i, p in enumerate(pr) for j, q in enumerate(ps))
    used_r, used_s, pairs = set(), set(), []
    for _, i, j, e in cand:
        if i in used_r or j in used_s:
            continue
        used_r.add(i); used_s.add(j)
        pairs.append((int(pr[i]), int(ps[j]), int(e)))
    pairs.sort()
    un_r = [int(pr[i]) for i in range(len(pr)) if i not in used_r]
    un_s = [int(ps[j]) for j in range(len(ps)) if j not in used_s]
    return pairs, un_r, un_s

def phase_delay_samples(f_hz):
    """Analytic phase delay of the causal Butterworth, in samples."""
    _, h = freqz(b, a, worN=[f_hz], fs=FS)
    return -np.angle(h[0]) / (2 * np.pi * f_hz) * FS

# 5. Report --------------------------------------------------------------
print(f"fs = {FS} Hz | FIR latency removed = {FIR_LATENCY} | gate tol = {GATE_TOL}\n")
print("Analytic phase delay of the causal IIR (samples):")
for f in (0.7, 1.0, 1.5, 2.0, 3.0, 5.0):
    print(f"  {f:4.1f} Hz : {phase_delay_samples(f):+6.1f}")
print()

for name, s in [("FIR", fir_shifted), ("IIR", iir)]:
    pairs, un_r, un_s = match_peaks(s, ref)
    e_all = np.array([e for _, _, e in pairs])
    e_gate = e_all[np.abs(e_all) <= GATE_TOL]

    print(f"--- {name} ---")
    print(f"  xcorr lag (whole window): {xlag(s, ref):+d} samples")
    print(f"  peaks: ref={len(pairs) + len(un_r)}  sig={len(pairs) + len(un_s)}  "
          f"matched={len(pairs)}  unmatched ref={len(un_r)} {un_r}  "
          f"unmatched sig={len(un_s)} {un_s}")
    print(f"  in-gate  n={len(e_gate)}/{len(e_all) + len(un_r)}  "
          f"median {np.median(e_gate):+.1f}, "
          f"mean {e_gate.mean():+.1f} ± {e_gate.std():.1f}, "
          f"max |e| {np.abs(e_gate).max():.0f}")
    print("  all pairs (ref -> sig, error):")
    for p, q, e in pairs:
        flag = "" if abs(e) <= GATE_TOL else "   <-- outside gate"
        print(f"    {p:3d} -> {q:3d}   {e:+3d}{flag}")
    print()