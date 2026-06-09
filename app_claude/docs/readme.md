This is the data flow for the system.

        choices=["extract_jd", "extract_product", "jd", "product", "prepare_load", "csv", "db_load", "all"],

1. extract_jd - takes the pdf and creates the txt file using document intelligence. This is trained on CV_Library jds
2. jd: this takes the txt file and applies a LLM to create a json file for the jd and expands meaning.
3. extract_product: reddit forum post, takes post and converts to text via document intelligence
4. product: this creates the json for the product by finding the actual products using an LLM
5. product_csv: takes product json files and creates csv files in the database folder
6. prepare_load: this takes the csv files and merges into the final csv file to load.
7. db_load: loads the final csv file into the graph db.
