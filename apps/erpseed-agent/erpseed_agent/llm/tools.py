"""Tool registry for ERPSEED AI Builder actions."""

from __future__ import annotations

from typing import Dict, Any, List


def get_builder_tools() -> List[Dict[str, Any]]:
    """Returns tool schemas for ERPSEED low-code model, view, and workflow generation."""
    return [
        {
            "name": "generate_model_schema",
            "description": "Generates a SysModel definition JSON schema based on entity description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_name": {"type": "string", "description": "Entity model name in snake_case"},
                    "verbose_name": {"type": "string", "description": "Human readable title"},
                    "fields": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "required": {"type": "boolean"},
                            },
                        },
                    },
                },
                "required": ["model_name", "fields"],
            },
        },
        {
            "name": "generate_view_layout",
            "description": "Generates a UI form or list layout JSON for an ERP model.",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_name": {"type": "string"},
                    "view_type": {"type": "string", "enum": ["form", "list", "kanban"]},
                    "components": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["model_name", "view_type"],
            },
        },
        {
            "name": "generate_workflow_rule",
            "description": "Generates an automated workflow trigger and action rule for ERPSEED.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string"},
                    "event_type": {"type": "string"},
                    "condition": {"type": "string"},
                    "action": {"type": "string"},
                },
                "required": ["workflow_name", "event_type", "action"],
            },
        },
    ]


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Executes a local AI builder tool function."""
    if tool_name == "generate_model_schema":
        model_name = arguments.get("model_name", "custom_entity")
        return {
            "model_name": model_name,
            "table_name": f"tbl_{model_name}",
            "fields": arguments.get("fields", []),
            "status": "schema_generated",
        }
    elif tool_name == "generate_view_layout":
        return {
            "model_name": arguments.get("model_name"),
            "view_type": arguments.get("view_type", "list"),
            "layout": arguments.get("components", []),
            "status": "view_generated",
        }
    elif tool_name == "generate_workflow_rule":
        return {
            "workflow_name": arguments.get("workflow_name"),
            "trigger": arguments.get("event_type"),
            "condition": arguments.get("condition", "true"),
            "action": arguments.get("action"),
            "status": "workflow_generated",
        }
    else:
        raise ValueError(f"Unknown tool name: {tool_name}")
