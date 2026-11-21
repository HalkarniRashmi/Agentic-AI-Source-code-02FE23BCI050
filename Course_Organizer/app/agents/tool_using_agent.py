import json
import re

from app.agents.base_agent import BaseAgent
from app.services.ollama_service import OllamaService
from app.tools.academic_tools import build_academic_tool_registry


class ToolUsingAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Academic Tool Using Agent",
            description=(
                "Uses an LLM to understand academic requests, "
                "select registered tools, execute operations, "
                "and generate contextual responses."
            )
        )

        self.registry = build_academic_tool_registry()

    # --------------------------------------------------
    # STEP 1: Parse JSON returned by the LLM
    # --------------------------------------------------

    def _parse_json(self, response):

        response = response.strip()

        response = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            response
        )

        try:
            return json.loads(response)

        except json.JSONDecodeError as error:

            raise ValueError(
                f"LLM returned invalid JSON: {response}"
            ) from error

    # --------------------------------------------------
    # STEP 2: Inject authenticated identity
    # --------------------------------------------------

    def _inject_identity(self, tool_name, arguments, input_data):

        tool = self.registry.get_tool(tool_name)

        if not tool:
            raise ValueError(
                f"Unknown tool selected: {tool_name}"
            )

        identity = {
            "user_id": input_data.get("user_id"),
            "role": input_data.get("role"),
            "professor_id": input_data.get("user_id"),
            "student_id": input_data.get("user_id")
        }

        for parameter, value in identity.items():

            if (
                parameter in tool.required_parameters
                or parameter in tool.optional_parameters
            ):
                arguments[parameter] = value

        return arguments

    # --------------------------------------------------
    # STEP 3: Prepare conversation context
    # --------------------------------------------------

    def _get_recent_history(self, input_data):

        messages = input_data.get("messages", [])

        if not isinstance(messages, list):
            return []

        # Keep the latest 12 messages to control prompt size.
        return [
            {
                "role": item.get("role"),
                "content": item.get("content", "")
            }
            for item in messages[-12:]
            if isinstance(item, dict)
            and item.get("role") in ("user", "assistant")
            and item.get("content")
        ]

    # --------------------------------------------------
    # STEP 4: Handle general conversational responses
    # --------------------------------------------------

    def _generate_general_response(self, input_data):

        messages = input_data.get("messages", [])

        if not messages:
            messages = [
                {
                    "role": "user",
                    "content": input_data.get("request", "")
                }
            ]

        answer = OllamaService.generate_response(
            messages=messages,
            context=input_data.get("context", {})
        )

        return {
            "status": "responded",
            "final_response": answer,
            "selection_reason": "No academic tool was required."
        }

    # --------------------------------------------------
    # STEP 5: Main agent execution
    # --------------------------------------------------

    def execute(self, input_data):

        user_request = input_data.get("request")
        user_id = input_data.get("user_id")
        role = input_data.get("role")

        if (
            not isinstance(user_request, str)
            or not user_request.strip()
        ):
            raise ValueError("User request is required.")

        if (
            not isinstance(user_id, int)
            or isinstance(user_id, bool)
            or user_id <= 0
            or role not in ("student", "professor")
        ):
            raise ValueError("Valid user identity is required.")

        available_tools = self.registry.list_tools()

        # ----------------------------------------------
        # STEP 1: Retrieve conversation and academic data
        # ----------------------------------------------

        recent_history = self._get_recent_history(input_data)

        academic_context = input_data.get("context", {})

        if not isinstance(academic_context, dict):
            academic_context = {}

        conversation_text = json.dumps(
            recent_history,
            indent=2,
            ensure_ascii=False,
            default=str
        )

        academic_context_text = json.dumps(
            academic_context,
            indent=2,
            ensure_ascii=False,
            default=str
        )

        tools_text = json.dumps(
            available_tools,
            indent=2,
            ensure_ascii=False,
            default=str
        )

        # ----------------------------------------------
        # STEP 2: Conversation-aware tool selection
        # ----------------------------------------------

        selection_prompt = f"""
You are the intelligent decision-making engine of AcademicFlow.

Your responsibility is to understand the user's CURRENT request
using the conversation history and the authenticated user's
academic context.

Choose exactly one action:

1. execute
2. respond
3. clarify

AVAILABLE TOOLS:

{tools_text}

AUTHENTICATED USER:

User ID: {user_id}
Role: {role}

ACADEMIC CONTEXT:

{academic_context_text}

RECENT CONVERSATION HISTORY:

{conversation_text}

CURRENT USER REQUEST:

{user_request}

IMPORTANT CONVERSATION UNDERSTANDING RULES:

1. Always interpret the current request in the context of
   the recent conversation.

2. Resolve references such as:
   - first course
   - second course
   - that course
   - its assignments
   - this assignment
   - that project
   - the previous one
   - its deadline

3. Use the conversation history to identify which academic
   record the user is referring to.

4. Use ACADEMIC CONTEXT to identify the actual record and
   its available identifiers.

5. Never invent course IDs, assignment IDs, project IDs,
   student IDs or professor IDs.

6. If the referenced record exists in academic context,
   use its actual identifier when selecting a tool.

7. If the current request refers to an earlier record,
   do not unnecessarily ask the user to provide its ID.

8. If the information is already available in the academic
   context and no tool is needed, respond using that context.

9. If additional database information is required, execute
   the appropriate registered tool.

10. Never expose another user's private academic information.

DECISION RULES:

- Use "execute" for supported academic database operations.
- Use "respond" for general knowledge, explanations,
  greetings and questions answerable from available context.
- Use "clarify" only when genuinely necessary information
  cannot be identified from history or academic context.

Only select tools listed in AVAILABLE TOOLS.

Do not claim an operation succeeded unless a tool executes.

Return ONLY valid JSON.

OUTPUT FORMAT:

For tool execution:

{{
    "action": "execute",
    "tool_name": "exact_registered_tool_name",
    "arguments": {{}},
    "reason": "Reason for selecting the tool"
}}

For conversational response:

{{
    "action": "respond",
    "reason": "Reason why no tool is required"
}}

For clarification:

{{
    "action": "clarify",
    "message": "Information required from the user"
}}
"""

        selection_response = OllamaService.generate_response(
            messages=[
                {
                    "role": "user",
                    "content": selection_prompt
                }
            ]
        )

        decision = self._parse_json(selection_response)

        if not isinstance(decision, dict):
            raise ValueError(
                "LLM decision must be a JSON object."
            )

        action = decision.get("action")

        # ----------------------------------------------
        # STEP 3: Handle conversational response
        # ----------------------------------------------

        if action == "respond":

            return self._generate_general_response(input_data)

        # ----------------------------------------------
        # STEP 4: Handle clarification
        # ----------------------------------------------

        if action == "clarify":

            return {
                "status": "clarification_required",
                "message": decision.get(
                    "message",
                    "Additional information is required."
                )
            }

        if action != "execute":

            raise ValueError(
                f"Invalid action returned by the LLM: {action}"
            )

        # ----------------------------------------------
        # STEP 5: Validate selected tool
        # ----------------------------------------------

        tool_name = decision.get("tool_name")
        arguments = decision.get("arguments", {})

        if not isinstance(tool_name, str):
            raise ValueError("Invalid tool name.")

        if not isinstance(arguments, dict):
            raise ValueError(
                "Tool arguments must be a dictionary."
            )

        tool = self.registry.get_tool(tool_name)

        if not tool:
            raise ValueError(
                f"LLM selected an unregistered tool: {tool_name}"
            )

        # ----------------------------------------------
        # STEP 6: Inject authenticated identity
        # ----------------------------------------------

        arguments = self._inject_identity(
            tool_name,
            arguments,
            input_data
        )

        # ----------------------------------------------
        # STEP 7: Execute registered tool
        # ----------------------------------------------

        tool_result = self.registry.execute_tool(
            tool_name,
            arguments
        )

        # ----------------------------------------------
        # STEP 8: Generate natural language response
        # ----------------------------------------------

        final_response = OllamaService.generate_response(
            messages=[
                {
                    "role": "user",
                    "content": f"""
You are AcademicFlow AI.

CONVERSATION HISTORY:

{conversation_text}

CURRENT USER REQUEST:

{user_request}

EXECUTED TOOL:

{tool_name}

ACTUAL TOOL RESULT:

{json.dumps(tool_result, default=str, ensure_ascii=False)}

Explain the result clearly and naturally.

RULES:

1. Use only information present in the actual tool result.
2. Never invent academic records or identifiers.
3. Preserve actual marks, deadlines, IDs and statuses.
4. If no records are available, clearly communicate that.
5. Do not claim an operation succeeded unless the tool result
   confirms it.
6. Keep the response relevant to the user's request.
7. Understand references using the conversation history.
"""
                }
            ]
        )

        # ----------------------------------------------
        # STEP 9: Return execution information
        # ----------------------------------------------

        return {
            "status": "completed",
            "selected_tool": tool_name,
            "selection_reason": decision.get("reason"),
            "tool_arguments": arguments,
            "tool_output": tool_result,
            "final_response": final_response
        }