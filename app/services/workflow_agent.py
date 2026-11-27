import os
import requests
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


# Initialize Gemini
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)


# -----------------------------------------
# TOOL 1: Get todo item from public API
# -----------------------------------------

def get_todo(todo_id: int) -> dict:

    if type(todo_id) is not int or not 1 <= todo_id <= 200:
        return {"error": "Invalid todo ID"}

    url = f"https://jsonplaceholder.typicode.com/todos/{todo_id}"

    result = call_api_with_retry(url)

    return result


# -----------------------------------------
# TOOL 2: Get user details from public API
# -----------------------------------------

def get_user(user_id: int) -> dict:

    if type(user_id) is not int or not 1 <= user_id <= 10:
        return {"error": "Invalid user ID"}

    url = f"https://jsonplaceholder.typicode.com/users/{user_id}"

    user = call_api_with_retry(url)

    if "error" in user:
        return user

    # Return only required fields
    return {
        "id": user["id"],
        "name": user["name"],
        "username": user["username"],
        "email": user["email"]
    }

# -----------------------------------------
# TOOL DECLARATIONS FOR GEMINI
# -----------------------------------------

workflow_tools = types.Tool(
    function_declarations=[

        types.FunctionDeclaration(
            name="get_todo",
            description="Retrieve a todo item from the public API.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "todo_id": types.Schema(
                        type=types.Type.INTEGER,
                        description="Todo item ID between 1 and 200."
                    )
                },
                required=["todo_id"]
            )
        ),

        types.FunctionDeclaration(
            name="get_user",
            description="Retrieve user details using the user ID.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "user_id": types.Schema(
                        type=types.Type.INTEGER,
                        description="User ID between 1 and 10."
                    )
                },
                required=["user_id"]
            )
        )

    ]
)


# -----------------------------------------
# PYTHON FUNCTION MAPPING
# -----------------------------------------

available_functions = {
    "get_todo": get_todo,
    "get_user": get_user
}


# -----------------------------------------
# AGENT WORKFLOW
# -----------------------------------------

def run_agent(
    question: str,
    max_tool_rounds: int = 5
) -> str:

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=question)
            ]
        )
    ]

    tool_rounds = 0

    while True:

        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="""
                You are a helpful AI assistant.

                You have access to:
                1. get_todo
                2. get_user

                Rules:
                - Use tools when external data is required.
                - For todo ownership, first retrieve the todo.
                - Use the todo's userId to retrieve the user.
                - Use actual tool results as evidence.
                - Never invent API results.
                - Do not call tools unrelated to the user's request.
                """,
                tools=[workflow_tools],
                temperature=0
            )
        )

        # If Gemini has no tool call, return its final answer
        if not response.function_calls:
            return response.text or "No final answer returned."

        # Prevent endless tool execution
        if tool_rounds >= max_tool_rounds:
            return (
                "Workflow stopped because it reached "
                "the maximum allowed tool steps."
            )

        # Save Gemini's tool-call message
        model_content = response.candidates[0].content

        contents.append(model_content)

        tool_response_parts = []

        # Execute requested tools
        for function_call in response.function_calls:

            function_name = function_call.name
            function_args = dict(function_call.args)

            print("\nTool selected:", function_name)
            print("Arguments:", function_args)

            # Allow only registered tools
            if function_name not in available_functions:

                function_result = {
                    "error": "Tool is not allowed"
                }

            else:

                selected_function = available_functions[
                    function_name
                ]

                try:
                    function_result = selected_function(
                        **function_args
                    )

                except Exception:
                    function_result = {
                        "error": "Tool execution failed"
                    }

            print("Tool result:", function_result)

            # Prepare result for Gemini
            tool_response_parts.append(
                types.Part.from_function_response(
                    name=function_name,
                    response={
                        "result": function_result
                    }
                )
            )

        # Send tool results back to Gemini
        contents.append(
            types.Content(
                role="user",
                parts=tool_response_parts
            )
        )

        tool_rounds += 1
        
        
def run_fixed_workflow(todo_id: int) -> dict:
    """
    Fixed workflow:
    1. Get todo
    2. Get todo owner
    3. Return combined result
    """

    # Step 1: Get todo details
    todo = get_todo(todo_id)

    if "error" in todo:
        return {
            "error": "Unable to retrieve todo",
            "details": todo
        }

    # Step 2: Extract user ID from todo result
    user_id = todo.get("userId")

    if user_id is None:
        return {
            "error": "Todo does not contain userId"
        }

    # Step 3: Get user details
    user = get_user(user_id)

    if "error" in user:
        return {
            "error": "Unable to retrieve user",
            "details": user
        }

    # Step 4: Return combined result
    return {
        "todo": {
            "id": todo["id"],
            "title": todo["title"],
            "completed": todo["completed"]
        },
        "owner": {
            "id": user["id"],
            "name": user["name"],
            "username": user["username"]
        }
    }
    

def call_api_with_retry(url: str, max_retries: int = 3) -> dict:

    for attempt in range(max_retries):

        try:
            response = requests.get(url, timeout=10)

            # Retry temporary server errors
            if response.status_code == 429 or response.status_code >= 500:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue

            return {"error": "API request timed out"}

        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue

            return {"error": "Connection failed"}

        except requests.exceptions.HTTPError as e:
            return {
                "error": "API returned an HTTP error",
                "details": str(e)
            }

    return {"error": "API failed after retries"}