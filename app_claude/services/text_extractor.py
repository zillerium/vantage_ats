class TextExtractor:

    @staticmethod
    def extract(result):

        full_text = []

        for page in result.pages:

            page_content = [
                line.content.strip()
                for line in page.lines
                if line.content and line.content.strip()
            ]

            if page_content:

                full_text.append(
                    "\n".join(page_content)
                )

        return "\n\n".join(full_text)
