import numpy as np

with open('sat_input_vectors.hex', 'r') as f:
    inputs = [int(line.strip(), 16) for line in f.readlines()]
inputs = [x - 65536 if x >= 32768 else x for x in inputs]

verilog_out = []
with open('sat_results.txt', 'r', encoding='utf-16') as f:
    for line in f:
        if "Out:" in line:
            verilog_out.append(int(line.split('Out:')[1].strip()))

coeffs = [0, 20, 24, -15, -140, -377, -697, -991, -1083, -791, 0, 1263, 
          2804, 4300, 5389, 5787, 5389, 4300, 2804, 1263, 0, -791, 
          -1083, -991, -697, -377, -140, -15, 24, 20, 0]
py_out = []
unclamped = []
shift_reg = [0] * 31

for i in range(len(inputs)):
    accum = sum(shift_reg[k] * coeffs[k] for k in range(31))
    scaled = (accum + (1 << 14)) >> 15
    unclamped.append(scaled)
    if scaled > 32767: scaled = 32767
    elif scaled < -32768: scaled = -32768
    py_out.append(scaled)
    for j in range(30, 0, -1): shift_reg[j] = shift_reg[j-1]
    shift_reg[0] = inputs[i]

matches = sum(1 for i in range(len(verilog_out)-1) if verilog_out[i+1] == py_out[i])
hi = sum(s > 32767 for s in unclamped)
lo = sum(s < -32768 for s in unclamped)

print(f"clamped high: {hi}, clamped low: {lo}")
print(f"Matches: {matches}/{len(verilog_out)-1}")

if matches == len(verilog_out)-1 and hi > 0 and lo > 0:
    print("✅ PERFECT! Saturation logic verified.")
else:
    print("❌ Failed.")