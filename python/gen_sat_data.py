import numpy as np
c = [0,20,24,-15,-140,-377,-697,-991,-1083,-791,0,1263,2804,4300,5389,5787,
     5389,4300,2804,1263,0,-791,-1083,-991,-697,-377,-140,-15,24,20,0]
pos = [32767 if v > 0 else -32768 if v < 0 else 0 for v in c]
neg = [-32768 if v > 0 else 32767 if v < 0 else 0 for v in c]
rng = np.random.default_rng(1234)
seq = [0]*31 + pos[::-1] + [0]*31 + neg[::-1] + [0]*31
seq += list(rng.integers(-32768, 32768, 1000 - len(seq)))
with open('sat_input_vectors.hex', 'w') as f:
    for v in seq:
        f.write(f"{int(v) & 0xFFFF:04X}\n")
print("✅ Generated directed saturation vectors.")