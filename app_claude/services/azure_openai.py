from openai import AzureOpenAI


class AzureOpenAIService:

    def __init__(
        self,
        endpoint,
        api_key,
        api_version="2024-12-01-preview"
    ):

        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )

    def parse_structured_output(
        self,
        model,
        system_prompt,
        user_text,
        response_schema,
        temperature=0
    ):

        response = (
            self.client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_text
                    }
                ],
                response_format=response_schema,
                temperature=temperature
            )
        )

        return (
            response
            .choices[0]
            .message
            .parsed
        )
