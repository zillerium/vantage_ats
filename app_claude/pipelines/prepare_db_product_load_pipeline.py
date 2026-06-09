from pathlib import Path

class PrepareDbProductLoadPipeline:

    def __init__(
        self,
        settings,
        file_reader,
        file_mover,
        product_csv_dir,
        load_csv_dir,
        load_csv_file_name,
        processed_csv_dir
    ):
        self.settings = settings
        self.file_reader = file_reader
        self.file_mover = file_mover
        self.product_csv_dir = product_csv_dir
        self.load_csv_dir = load_csv_dir
        self.load_csv_file_name = load_csv_file_name
        self.processed_csv_dir = processed_csv_dir

    def process_preparation(self):
        """Converts to a pure 'cat *.csv > target' streaming operation."""
        source_dir = Path(self.product_csv_dir)
        target_dir = Path(self.load_csv_dir)
        
        target_dir.mkdir(parents=True, exist_ok=True)
        combined_filepath = target_dir / self.load_csv_file_name

        # 1. Gather files, explicitly ignoring the output file if folders overlap
        csv_files = [
            f for f in source_dir.glob("*.csv") 
            if f.resolve() != combined_filepath.resolve()
        ]

        if not csv_files:
            print(f"⚠️ No CSV files found in: '{source_dir}'")
            return

        print(f"📂 Concatenating {len(csv_files)} files into '{combined_filepath}'...")

        try:
            # 2. Open output file once, then stream copy every input file into it
            with open(combined_filepath, mode='w', encoding='utf-8') as outfile:
                for csv_file in csv_files:
                    with open(csv_file, mode='r', encoding='utf-8') as infile:
                        # shutil optimized block copy or direct stream read
                        outfile.write(infile.read())
                    
                    # Ensure files without a trailing newline don't mash headers together
                    outfile.write('\n')
                    
            print(f"✅ Cat operation complete.")
            
        except Exception as e:
            print(f"❌ Error during file concatenation: {e}")
            return

        # 3. Archive the processed files safely after the output file handles are closed
        print(f"\n📦 Moving source files to archive...")
        archive_dir = Path(self.processed_csv_dir)
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        for csv_file in csv_files:
            try:
                dest = self.file_mover.move_file(csv_file, str(archive_dir))
                print(f"  ➡️ Moved '{csv_file.name}' to archive.")
            except Exception as e:
                print(f"  ❌ Failed to move '{csv_file.name}': {e}")

        print("\n🎉 Process complete.")