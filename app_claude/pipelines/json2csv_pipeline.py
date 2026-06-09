import json
from pathlib import Path

class Json2CsvPipeline:
    def __init__(
        self,
        settings,
        file_reader,
        file_mover,
        json_input_dir,
        csv_output_dir,
        json_processed_dir
    ):
        self.settings = settings
        self.file_reader = file_reader
        self.file_mover = file_mover
        self.json_input_dir = json_input_dir
        self.csv_output_dir = csv_output_dir
        self.json_processed_dir = json_processed_dir

    def process_all_files(self):
        # Using pathlib to find all JSON files in the input directory
        input_path = Path(self.json_input_dir)
        json_files = list(input_path.glob("*.json"))

        print(f"\n📂 Found {len(json_files)} JSON files to transform into CSV")

        for index, json_file in enumerate(json_files, 1):
            print("\n" + "=" * 70)
            print(f"📄 Processing JSON file ({index}/{len(json_files)}): {json_file.name}")
            
            self._process_single_file(json_file)

        print("\n🎉 CSV Generation and archiving complete")

    def _process_single_file(self, json_file: Path):
        # 1. Safely read and parse JSON file
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Successfully read and parsed {json_file.name}")
        except Exception as e:
            print(f"❌ Failed to parse JSON from '{json_file}': {e}")
            return

        # 2. Extract array of identified products
        products = data.get("identified_products", [])
        if not products:
            print(f"⚠️ Warning: No 'identified_products' array found inside '{json_file.name}'.")
            return

        # 3. Create out filepath with the same base name, but with a .csv extension
        output_file = Path(self.csv_output_dir) / f"{json_file.stem}.csv"

        # 4. Write data using the required precise triple-quote layout formatting
        try:
            with open(output_file, mode='w', encoding='utf-8', newline='') as csv_file:
                for item in products:
                    name = item.get("product_name", "").strip()
                    desc = item.get("product_description", "").strip()
                    cat = item.get("category", "").strip()
                    
                    # Row schema: 3 populated fields wrapper in triple quotes, followed by 2 trailing empty sets
                    row_str = f'"""{name}""","""{desc}""","""{cat}""","""""",""""""\n'
                    csv_file.write(row_str)
                    
            print(f"✅ Generated graph load file: '{output_file}' ({len(products)} products exported).")
        except Exception as e:
            print(f"❌ Failed to write CSV file layout: {e}")
            return

        # 5. Archive raw file after completely successful transform
        try:
            destination = self.file_mover.move_file(
                json_file,
                self.json_processed_dir
            )
            print(f"📦 Archived JSON file to: {destination}")
        except Exception as e:
            print(f"❌ Failed archiving JSON file: {e}")