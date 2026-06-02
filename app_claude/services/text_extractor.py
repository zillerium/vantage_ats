# What it should look like to support the clean dictionary:
class TextExtractor:
    def extract(self, result_dict: dict) -> str:
        extracted_lines = []
        
        # Safely get the pages list out of the dictionary
        pages = result_dict.get("pages", [])
        
        for page in pages:
            # Azure dictionary format nests lines under 'lines' inside each page
            for line in page.get("lines", []):
                extracted_lines.append(line.get("content", ""))
                
        return "\n".join(extracted_lines)