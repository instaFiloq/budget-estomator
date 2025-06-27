import openai
from django.conf import settings
from openai import OpenAI
import json

apiKey = settings.OPEN_AI_API_KEY
client = OpenAI(api_key=apiKey)

SYSTEM_BUDGET_ESTIMATOR_PROMPT = """
    You are a fix and flip expert for real estate projects. your task is to have a conversation with the user and try to collect as much possible information that will help you estimate the project budget.
    first start by asking the user about his property location (will help determine material commonly used in the area and the cost of building materials, and services), when its build, the structure or units (rooms, kitchens, bathrooms, halls ...), area for the all the property and by unit if possible.
    second ask about the property condition 
    last ask about the renovations details needed on the property 
    try to provide the user a break down on what is needed to do this project and estimate the project budget and you must categorize the expenses into categories and each category into multiple budget line items where each item has a description and estimated amount.
    you can ask any question you want to improve the estimated budget for example it user said he wants to replace tiles fro the kitchen you can ask further question like what is model if he has one in mind if not suggest some  of tiles what is the target area this will improve the estimated cost. 
    you must have a continuous conversation with the user in order to improve the estimated budget.
    check if user wants to make changes on the categorization of the budget or any other changes and apply it.
    when providing the estimated budget ask followup question to improve the estimation.
    the estimated budget should have this format:
    {
        categories: {
            name: string
            lineItems: {
                name: string
                description: string,
                estimatedAmount: number
            }[]
        }[],
        totalBudget: number
    }
"""

SYSTEM_BUDGET_DETAILS_COLLECTOR_PROMPT = """
    You are a fix and flip expert for real estate projects. your task is to have a conversation with the user and try to collect as much possible information that will help you estimate the project budget.
    first start by asking the user about his property location (will help determine material commonly used in the area and the cost of building materials, and services), when its build, the structure or units (rooms, kitchens, bathrooms, halls ...), area for the all the property and by unit if possible.
    second ask about the property condition 
    last ask about the renovations details needed on the property 
    try to provide the user a break down on what is needed to do this project and estimate the project budget and you must categorize the expenses into categories and each category into multiple budget line items where each item has a description and estimated amount.
    you can ask any question you want to improve the estimated budget for example it user said he wants to replace tiles fro the kitchen you can ask further question like what is model if he has one in mind if not suggest some  of tiles what is the target area this will improve the estimated cost. 
    you must have a continuous conversation with the user in order to improve the estimated budget.
    check if user wants to make changes on the categorization of the budget or any other changes and apply it.
    when providing the estimated budget ask followup question to improve the estimation.
    the responses should be in Markdown format.
"""

def get_chat_response(messages):
    openai.api_key = settings.OPEN_AI_API_KEY
    messages.insert(0, {
        "role": "system",
        "content": SYSTEM_BUDGET_DETAILS_COLLECTOR_PROMPT
    })
    response = openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

def get_estimated_budget_response(messages):
    openai.api_key = settings.OPEN_AI_API_KEY
    messages.insert(0, {
        "role": "system",
        "content": SYSTEM_BUDGET_ESTIMATOR_PROMPT
    })
    messages.append({
        "role": "system",
        "content": """
            based on the conversation with the user provide the estimated budget in the following format:
            {
                categories: {
                    name: string
                    lineItems: {
                        name: string
                        description: string,
                        estimatedAmount: number
                    }[]
                }[],
                totalBudget: number
            }
            the response should be a json object this that format.
        """
    })
    response = openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

def perform_web_search(query):
    prompt = f"""
    Search for the details about the property at {query}.
    If found, return the results in the following JSON format:

    {{
        "address": "",
        "property_type": "",
        "bedrooms": "",
        "bathrooms": "",
        "square_footage": "",
        "year_built": "",
        "listing_price": "",
        "status": "",
        "features": ""
    }}

    If the property cannot be found or there's no reliable data, return: null
    Only return the JSON or null, with no explanation or extra text.
    """

    response = client.responses.create(
        model="gpt-4.1",
        tools=[{"type": "web_search_preview"}],
        input=prompt.strip()
    )

    raw_output = response.output_text.strip()

    # Try to parse the JSON or check if "null"
    if raw_output.lower() == "null":
        return None

    try:
        data = json.loads(raw_output)
        return data
    except json.JSONDecodeError:
        return None