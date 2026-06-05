import json
import sys
import os

def generate_graph_csv(json_filepath: str, output_filename: str = "products_load.csv"):
    """
    Reads a dynamic JSON classification file from disk and writes the identified products
    to a CSV with triple quotes as column wrappers.
    """
    # 1. Verify that the file exists
    if not os.path.exists(json_filepath):
        print(f"Error: The input file '{json_filepath}' does not exist.")
        return

    # 2. Safely read and parse the dynamic JSON content
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse valid JSON from '{json_filepath}'. Detail: {e}")
        return

    # 3. Extract the array of identified products
    products = data.get("identified_products", [])
    if not products:
        print(f"Warning: No 'identified_products' array found inside '{json_filepath}'.")
        return
    
    # 4. Open output file and write using precise triple-quote formatting
    with open(output_filename, mode='w', encoding='utf-8', newline='') as csv_file:
        for item in products:
            name = item.get("product_name", "").strip()
            desc = item.get("product_description", "").strip()
            cat = item.get("category", "").strip()
            
            # Explicitly wrapping fields in triple quotes and adding 2 trailing empty columns
            row_str = f'"""{name}""","""{desc}""","""{cat}""","""""",""""""\n'
            csv_file.write(row_str)
            
    print(f"Successfully processed '{json_filepath}' -> Generated graph load file: '{output_filename}' ({len(products)} products exported).")


if __name__ == "__main__":
    # This allows you to pass any file path dynamically from the terminal:
    # e.g., python dynamic_graph_csv_exporter.py path/to/any_new_output.json
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Fallback default file name if no argument is passed
        input_file = "aws-glue.json"
        
    generate_graph_csv(input_file)
