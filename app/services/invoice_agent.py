import os
import re
from app.db.session import SessionLocal
from sqlalchemy import select
from google import genai
from google.genai import types

from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def ask_invoice_agent(question: str) -> str:

    max_tool_calls = 4
    tool_call_count = 0

    contents = question
    available_functions = {
        "get_invoice_details": get_invoice_details,
        "search_invoice_knowledge": search_invoice_knowledge,
        "get_sample_api_data": get_sample_api_data
    }

    while tool_call_count < max_tool_calls:

        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),

            contents=contents,

            config=types.GenerateContentConfig(
                system_instruction="""
                You are an Invoice Investigation Agent.

                Your job is to investigate invoice-related questions.

                You have access to these tools:
                1. get_invoice_details
                2. search_invoice_knowledge
                3. get_sample_api_data

                Rules:
                - Use invoice details when an invoice number is provided.
                - Use RAG search when additional information is required.
                - Use get_invoice_details for invoice-related questions.
                - Use search_invoice_knowledge when additional invoice knowledge is required.
                - Use get_sample_api_data when the user asks to retrieve sample todo data from the public API.
                - Use tool results as evidence.
                - When a tool is required, call the appropriate tool.
                - Do not invent invoice status or amounts.
                - If information is missing, clearly say so.
                - You are read-only.
                - Never approve, pay, delete, or modify invoices.
                """,

                tools=[invoice_tools]
            )
        )

        # If Gemini doesn't request a tool, return its answer
        if not response.function_calls:
            return response.text

        # Execute the tools requested by Gemini
        for function_call in response.function_calls:

            if tool_call_count >= max_tool_calls:
                break

            function_name = function_call.name
            function_args = function_call.args

            selected_function = available_functions[function_name]

            function_result = selected_function(**function_args)

            tool_call_count += 1

            print("Function:", function_name)
            print("Arguments:", function_args)
            print("Result:", function_result)

            # Send the tool result back to Gemini
            contents = [
                question,
                f"""
                Tool executed: {function_name}
                Arguments: {function_args}
                Tool result: {function_result}

                Use this result to continue investigating.
                """
            ]

    return "Maximum tool calls reached. Please try a more specific question."


def get_invoice_details(invoice_number: str) -> dict:
    """
    Retrieve invoice details from PostgreSQL.
    """

    # Step 1: Validate invoice number
    if not isinstance(invoice_number, str):
        return {"error": "Invalid invoice number"}

    invoice_number = invoice_number.strip()

    if not re.fullmatch(r"[A-Za-z0-9-]{1,50}", invoice_number):
        return {"error": "Invalid invoice number format"}

    # Step 2: Open database session
    with SessionLocal() as db:

        # Step 3: Query the invoice
        statement = select(Invoice).where(
            Invoice.invoice_number == invoice_number
        )

        invoice = db.execute(statement).scalar_one_or_none()

        # Step 4: Handle invoice not found
        if invoice is None:
            return {
                "error": "Invoice not found",
                "invoice_number": invoice_number
            }

        # Step 5: Return only approved fields
        return {
            "invoice_number": invoice.invoice_number,
            "vendor_name": invoice.vendor_name,
            "amount": float(invoice.amount),
            "status": invoice.status
        }

def search_invoice_knowledge(query: str) -> dict:
    """
    Search invoice documents using the existing RAG retrieval system.

    Args:
        query: The question or information to search for.

    Returns:
        Relevant invoice document chunks.
    """

    # Connect this function to your existing
    # semantic search / RAG retrieval service.

    return {
        "query": query,
        "results": [
            "Demo result: invoice matching information was retrieved."
        ]
    }
    
    
get_invoice_details_schema = types.FunctionDeclaration(
    name="get_invoice_details",

    description=(
        "Retrieve invoice details from the database "
        "using the invoice number."
    ),

    parameters_json_schema={
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": (
                    "The invoice number, "
                    "for example INV-1002."
                )
            }
        },
        "required": ["invoice_number"]
    }
)

search_invoice_knowledge_schema = types.FunctionDeclaration(
    name="search_invoice_knowledge",

    description=(
        "Search invoice-related knowledge using "
        "semantic search and return relevant information."
    ),

    parameters_json_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The invoice-related question or "
                    "topic to search for."
                )
            }
        },
        "required": ["query"]
    }
)

get_sample_api_data_schema = types.FunctionDeclaration(
    name="get_sample_api_data",
    description="Retrieve sample todo data from a public API using its ID.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "todo_id": types.Schema(
                type=types.Type.INTEGER,
                description="The ID of the todo item to retrieve, between 1 and 200."
            )
        },
        required=["todo_id"]
    )
)

invoice_tools = types.Tool(
    function_declarations=[
        get_invoice_details_schema,
        search_invoice_knowledge_schema,
        get_sample_api_data_schema
    ]
)


import requests


def get_sample_api_data(todo_id: int) -> dict:
    """
    Retrieve sample data from a public API.
    """

    if not isinstance(todo_id, int) or not 1 <= todo_id <= 200:
        return {"error": "Invalid todo ID"}

    try:
        response = requests.get(
            f"https://jsonplaceholder.typicode.com/todos/{todo_id}",
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException:
        return {"error": "Unable to retrieve sample API data"}