from openai import AzureOpenAI

class AzureJobAdClassifierWrapper:
    """
    A domain-specific wrapper around Azure OpenAI.
    Responsible exclusively for transforming unstructured job ad text into validated structured formats.
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

    def extract_structured_job_data(
        self,
        deployment_name: str,
        system_prompt: str,
        raw_job_text: str,
        response_schema,
        temperature: float = 0.0
    ):
        """
        Uses Azure OpenAI Structured Outputs to enforce JSON syntax 
        matching the provided response_schema.
        """
        response = self.client.beta.chat.completions.parse(
            model=deployment_name,  # In Azure, this maps to your deployment name
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": raw_job_text
                }
            ],
            response_format=response_schema,
            temperature=temperature
        )

        # Returns the cleanly parsed Pydantic object directly
        return response.choices[0].message.parsed