import tkinter as tk
from tkinter import filedialog

def capitalize_line(line):
    words = line.split()
    return " ".join(w[0].upper() + w[1:] if w else "" for w in words)

# Hide the main tkinter window
root = tk.Tk()
root.withdraw()

# Ask user to choose input file
input_path = filedialog.askopenfilename(
    title="Select input text file",
    filetypes=[("Text Files", "*.txt")]
)

if not input_path:
    print("No input file selected.")
    exit()

# Ask user to choose output file
output_path = filedialog.asksaveasfilename(
    title="Save output text file",
    defaultextension=".txt",
    filetypes=[("Text Files", "*.txt")]
)

if not output_path:
    print("No output file selected.")
    exit()

# Read input
with open(input_path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace underscores and hyphens with spaces
text = text.replace("_", " ").replace("-", " ")

# Process each line
lines = text.splitlines()
capitalized_lines = [capitalize_line(line) for line in lines]

# Join lines and add 3-line gap
final_output = "\n\n\n" + "\n".join(capitalized_lines)

# Write output
with open(output_path, "w", encoding="utf-8") as f:
    f.write(final_output)

print("Done! Output saved to:", output_path)
