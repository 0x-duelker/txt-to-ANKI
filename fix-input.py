def fix_table_file(input_file, output_file):
    """
    Fix table formatting in a Markdown file to ensure it aligns with expected parsing.
    """
    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        lines = infile.readlines()

        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                outfile.write("\n")
                continue

            # Ensure rows have correct separators and leading/trailing pipes
            if "|" in line:
                values = line.split("|")
                values = [v.strip() for v in values if v.strip()]  # Remove empty splits
                fixed_line = "| " + " | ".join(values) + " |\n"
                outfile.write(fixed_line)
            else:
                # Write non-table lines as-is
                outfile.write(line + "\n")


# Example Usage
if __name__ == "__main__":
    input_filename = "WichtigsteVerben.md"  # Replace with your actual file name
    output_filename = "input_files/WichtigsteVerben-fixed.md"
    try:
        fix_table_file(input_filename, output_filename)
        print(f"File fixed and saved as '{output_filename}'.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
