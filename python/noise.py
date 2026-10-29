import numpy as np
# Generate 1000 samples of full-scale random noise (-32768 to 32767)
inputs = np.random.randint(-32768, 32767, 1000)
with open('sat_input_vectors.hex', 'w') as f:
    for val in inputs:
        f.write(f"{val & 0xFFFF:04X}\n")
print("Saved sat_input_vectors.hex")