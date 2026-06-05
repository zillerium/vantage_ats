from openai import AzureOpenAI

class AzureTextClassifierWrapper:
    """
    A class-based wrapper around Azure OpenAI.
    Provides a clean, dedicated boundary for LLM interactions.
    """
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        api_version: str = "2024-12-01-preview"
    ):
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )

    def parse_structured_output(
        self,
        model: str,
        system_prompt: str,
        user_text: str,
        response_schema,
        temperature: float = 0.0
    ):
        """
        Maintains the exact method interface that the working, 
        heavily tested JobDescriptionClassifier expects.
        """
        response = self.client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            response_format=response_schema,
            temperature=temperature
        )
        return response.choices[0].message.parsed