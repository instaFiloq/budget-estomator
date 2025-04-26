import openai
from django.conf import settings

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

def get_chat_response(messages):
    
    print("/************************ OPEN-AI API KEY ********************/")
    print(settings.OPEN_AI_API_KEY)
    print("/************************** END API KEY **********************/")

    openai.api_key = settings.OPEN_AI_API_KEY
    messages.insert(0, {
        "role": "system",
        "content": SYSTEM_BUDGET_ESTIMATOR_PROMPT
    })
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
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
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content