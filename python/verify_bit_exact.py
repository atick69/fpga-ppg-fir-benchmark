import numpy as np

# 1. Load the input data
with open('ppg_input_vectors.hex', 'r') as f:
    hex_lines = f.readlines()
inputs = [int(line.strip(), 16) for line in hex_lines]
inputs = [x - 65536 if x >= 32768 else x for x in inputs] # Convert to signed 16-bit

# 2. Load the Verilog output
verilog_out = []
with open('ppg_results.txt', 'r', encoding='utf-16') as f:
    for line in f:
        if "Out:" in line:
            verilog_out.append(int(line.split('Out:')[1].strip()))

# 3. Define the exact Q1.15 coefficients from your generator
coeffs = [0, 20, 24, -15, -140, -377, -697, -991, -1083, -791, 0, 1263, 
          2804, 4300, 5389, 5787, 5389, 4300, 2804, 1263, 0, -791, 
          -1083, -991, -697, -377, -140, -15, 24, 20, 0]

# 4. Simulate the exact Verilog math in Python
py_out = []
shift_reg = [0] * 31

for i in range(len(inputs)):
    # Calculate MAC from current shift_reg
    accum = sum(shift_reg[k] * coeffs[k] for k in range(31))
    
    # Rounding and scaling
    scaled = (accum + (1 << 14)) >> 15
    
    # Saturation logic
    if scaled > 32767: scaled = 32767
    elif scaled < -32768: scaled = -32768
    
    py_out.append(scaled)
    
    # Shift in the new input (exactly as Verilog does on posedge clk)
    for j in range(30, 0, -1):
        shift_reg[j] = shift_reg[j-1]
    shift_reg[0] = inputs[i]

import numpy as np

# 1. Load the hex input
with open('ppg_input_vectors.hex', 'r') as f:
    hex_lines = f.readlines()
inputs = [int(line.strip(), 16) for line in hex_lines]
inputs = [x - 65536 if x >= 32768 else x for x in inputs]

# 2. Load the Verilog output and logged inputs
verilog_out = []
verilog_in = []
with open('ppg_results.txt', 'r', encoding='utf-16') as f:
    for line in f:
        if "In:" in line and "Out:" in line:
            parts = line.split('|')
            verilog_in.append(int(parts[1].split(':')[1].strip()))
            verilog_out.append(int(parts[2].split(':')[1].strip()))

# 3. Python Golden Model (exact hardware math)
coeffs = [0, 20, 24, -15, -140, -377, -697, -991, -1083, -791, 0, 1263, 
          2804, 4300, 5389, 5787, 5389, 4300, 2804, 1263, 0, -791, 
          -1083, -991, -697, -377, -140, -15, 24, 20, 0]
py_out = []
shift_reg = [0] * 31

for i in range(len(inputs)):
    # MAC
    accum = sum(shift_reg[k] * coeffs[k] for k in range(31))
    # Round & Scale
    scaled = (accum + (1 << 14)) >> 15
    # Saturate
    if scaled > 32767: scaled = 32767
    elif scaled < -32768: scaled = -32768
    py_out.append(scaled)
    # Shift
    for j in range(30, 0, -1):
        shift_reg[j] = shift_reg[j-1]
    shift_reg[0] = inputs[i]

# 4. Diagnostic Checks (From the Reviewer)
print("hex inputs == logged inputs:", inputs[:len(verilog_in)] == verilog_in)
print(f"lengths: inputs={len(inputs)}, verilog_out={len(verilog_out)}, py_out={len(py_out)}")

print("\nChecking alignment lags...")
for lag in range(-3, 4):          
    idx = [i for i in range(len(py_out)) if 0 <= i + lag < len(verilog_out)]
    mism = sum(verilog_out[i + lag] != py_out[i] for i in idx)
    print(f"lag {lag:+d}: {mism} mismatches out of {len(idx)}")