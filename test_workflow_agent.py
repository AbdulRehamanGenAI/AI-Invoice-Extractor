
from app.services.workflow_agent import run_agent


# -----------------------------------------
# SINGLE-STEP WORKFLOW
# -----------------------------------------

question = "Get todo item 1 from the public API."

answer = run_agent(
    question,
    max_tool_rounds=1
)

print("\nSingle-step answer:")
print(answer)


# -----------------------------------------
# MULTI-STEP WORKFLOW
# -----------------------------------------

question = """
Get todo item 1 from the public API.

Then find the user who owns this todo using
the userId returned by the first API call.

Finally, tell me:
1. Todo title
2. Whether it is completed
3. User name
"""

answer = run_agent(
    question,
    max_tool_rounds=5
)

print("\nMulti-step answer:")
print(answer)


