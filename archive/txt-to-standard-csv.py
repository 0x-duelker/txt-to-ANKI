import os
import tkinter as tk
from tkinter import filedialog
import csv

def parse_raw_line(line):
    """
    Example parser that expects lines like:
    Word: Essen
    Meaning: to eat
    Example: Wir essen um acht Uhr abends.
    Notes: (v) irregular verb

    Returns a tuple (key, value).
    """
    parts = line.split(":", 1)
    if len(parts) == 2:
        key = parts[0].strip()
        value = parts[1].strip()
        return key, value
    return None, None

def convert_txt_to_csv(input_txt_file, output_csv_file):
    """
    Convert a text file with lines like:

        Word: Essen
        Meaning: to eat
        Example: Wir essen um acht Uhr abends.
        Notes: (v) irregular verb

        (blank line to separate entries)

    into a CSV with columns: Word,Meaning,Example,Notes
    """
    entries = []
    current_entry = {}

    with open(input_txt_file, "r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if not line:
                # Blank line => finish the current entry
                if current_entry:
                    entries.append(current_entry)
                current_entry = {}
                continue

            k, v = parse_raw_line(line)
            if k and v:
                current_entry[k] = v

        # If there's a leftover entry after the loop
        if current_entry:
            entries.append(current_entry)

    # Define the standard columns
    fieldnames = ["Word", "Meaning", "Example", "Notes"]

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_csv_file), exist_ok=True)

    with open(output_csv_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            # Make sure all columns exist, default to empty
            row = {}
            for fn in fieldnames:
                row[fn] = entry.get(fn, "")
            writer.writerow(row)

    print(f"Converted {input_txt_file} => {output_csv_file} with {len(entries)} entries.")

def main():
    # Hide the main TK root window
    root = tk.Tk()
    root.withdraw()

    # Ask user to pick an input file
    input_txt_file = filedialog.askopenfilename(
        title="Select your TXT/MD file",
        filetypes=[("Text files", "*.txt *.md *.markdown *.rst"), ("All files", "*.*")]
    )
    if not input_txt_file:
        print("No input file selected. Exiting.")
        return

    # Derive output CSV path
    # - Use the same basename as input
    # - Save in the 'csv' subdirectory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_dir = os.path.join(script_dir, "csv")
    base_name = os.path.splitext(os.path.basename(input_txt_file))[0]
    output_csv_file = os.path.join(csv_dir, base_name + ".csv")

    # Convert
    convert_txt_to_csv(input_txt_file, output_csv_file)

if __name__ == "__main__":
    main()
