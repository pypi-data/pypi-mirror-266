# openai_requests_utils

You need to create an environment variable called "OPENAI_API_KEY" which contains your OpenAI API key. You also need to create a config file called oai_config.json in the same folder as your script to choose the model and the API call parameters. Every parameter except "model" is optional and can be removed.

Example of oai_config.json:
{
    "model": "gpt-3.5-turbo-1106",
    "max_response_length": 400,
    "timeout": 10,
    "temperature": 1,
    "top_p": 0.95,
    "presence_penalty": 0.5,
    "frequency_penalty": 0.5
}