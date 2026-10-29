import matplotlib.pyplot as plt

input_signal = []
output_signal = []

# 1. Read the file with 'utf-16' encoding to handle PowerShell's output redirection
try:
    with open('ppg_results.txt', 'r', encoding='utf-16') as f:
        for line in f:
            if "In:" in line and "Out:" in line:
                # Split the line: "Sample 0 | In: 274 | Out: 0"
                parts = line.split('|')
                in_val = int(parts[1].split(':')[1].strip())
                out_val = int(parts[2].split(':')[1].strip())
                input_signal.append(in_val)
                output_signal.append(out_val)
except UnicodeDecodeError:
    # Fallback in case it was saved in utf-8
    with open('ppg_results.txt', 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if "In:" in line and "Out:" in line:
                parts = line.split('|')
                in_val = int(parts[1].split(':')[1].strip())
                out_val = int(parts[2].split(':')[1].strip())
                input_signal.append(in_val)
                output_signal.append(out_val)

print(f"✅ Loaded {len(input_signal)} samples successfully!")

# 2. Plot the raw vs filtered PPG data
plt.figure(figsize=(14, 6))

# Plot Raw PPG (shifted down slightly for visual clarity)
plt.plot(input_signal, label='Raw PPG Input (with baseline wander)', color='gray', alpha=0.7)

# Plot Filtered PPG
plt.plot(output_signal, label='Filtered PPG (31-Tap Folded FIR)', color='red', linewidth=2)

# Formatting
plt.title('Hardware FPGA Filtering of Real Wearable PPG Data', fontsize=16)
plt.xlabel('Sample Number (55 Hz Sampling Rate)', fontsize=12)
plt.ylabel('16-bit Amplitude', fontsize=12)
plt.legend(loc='upper right', fontsize=12)
plt.grid(True, alpha=0.3)

# Save the plot as an image for GitHub
plt.tight_layout()
plt.savefig('ppg_filter_proof.png', dpi=300)
print("✅ Success! Saved plot as 'ppg_filter_proof.png'")

# Show the plot on screen
plt.show()