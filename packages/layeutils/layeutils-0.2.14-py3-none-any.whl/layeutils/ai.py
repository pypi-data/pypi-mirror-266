
def chatgpt_basic_conversation(api_key: str, prompts: list, model: str = 'gpt-3.5-turbo') -> str:
    """chatgpt最基本的对话，使用前需要使用home_proxy设置代理

    Args:
        api_key (str): _description_
        prompts (list): e.g [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Hello!"}]
        model (str, optional): _description_. Defaults to 'gpt-3.5-turbo'.

    Returns:
        str: ChatGPT response
    """
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(model=model, messages=prompts)
    return completion.choices[0].message.content


def get_pandasai_agent(data, openapi_key: str = None, config: dict = None):
    """获得pandas-ai库中的Agent对象: https://docs.pandas-ai.com/en/latest/
        Agent.chat("XXX") or 
        Agent.clarification_question("XXX") or 
        Agent.explain() or 
        Agent.rephrase_query("XXX")


    Args:
        openapi_key (str): 如果不传，使用pandasbi的免费key
        data (_type_): Dataframe or [Dataframe1, Dataframe2, ...]
        config (dict, optional): https://docs.pandas-ai.com/en/latest/getting-started/#config. Defaults to None.

    Returns:
        _type_: pandasai.Agent
    """
    import os

    from pandasai import Agent
    from pandasai.llm import OpenAI

    if not openapi_key:
        os.environ["PANDASAI_API_KEY"] = "$2a$10$AjBzJYa7M.AV8wRfcUisme4ARgSUVF.ooDDIn4MS4S52Umd7N6O12"
        if not config:
            config = {
                "save_logs": False,
                "save_charts": False,
                "verbose": False,
                "enable_cache": False,
                "open_charts": True
            }
    else:
        llm = OpenAI(api_token=openapi_key)
        if not config:
            config = {
                "llm": llm,
                "save_logs": False,
                "save_charts": False,
                "verbose": False,
                "enable_cache": False,
                "open_charts": True
            }
    agent = Agent(data, config)
    return agent
