import os
from pathlib import Path
from typing import Any


ROUTE_TOOLS = {
    "route_to_billing",
    "route_to_technical",
    "route_to_faq",
    "route_to_escalation",
}


def _message_text(message: Any) -> str:
    content = getattr(message, "content", "")
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(str(block.get("text", block)))
            else:
                parts.append(str(block))
        return " ".join(parts)
    return str(content)


def _final_text(run_result: dict) -> str:
    return _message_text(run_result["messages"][-1])


def _all_text(run_result: dict) -> str:
    return "\n".join(_message_text(message) for message in run_result["messages"])


def _called_routes(run_result: dict) -> list[str]:
    routes = []
    for message in run_result["messages"]:
        for tool_call in getattr(message, "tool_calls", []) or []:
            name = tool_call.get("name")
            if name in ROUTE_TOOLS:
                routes.append(name)
    return routes


def grade_no_error(run_result: dict, expected: dict) -> dict:
    """Checks the agent completed without obvious runtime failure text."""
    text = _final_text(run_result).lower()
    error_signals = ["exception:", "traceback", "internal server error", "tool failed"]
    found = [signal for signal in error_signals if signal in text]
    return {
        "score": 0.0 if found else 1.0,
        "reason": f"Error signals found: {found}" if found else "No runtime error signals found",
    }


def grade_content_contains(run_result: dict, expected: dict) -> dict:
    """Checks required phrases appear in the final output message."""
    phrases = expected.get("expected_contains", [])
    if not phrases:
        return {"score": 1.0, "reason": "No required phrases to check"}

    final_text = _final_text(run_result).lower()
    found = [phrase for phrase in phrases if phrase.lower() in final_text]
    missing = [phrase for phrase in phrases if phrase.lower() not in final_text]
    score = len(found) / len(phrases)

    return {
        "score": score,
        "reason": f"Found: {found} | Missing: {missing}",
    }


def grade_not_contains(run_result: dict, expected: dict) -> dict:
    """Checks forbidden phrases do not appear in the final output message."""
    forbidden = expected.get("expected_not_contains", [])
    if not forbidden:
        return {"score": 1.0, "reason": "No forbidden phrases to check"}

    final_text = _final_text(run_result).lower()
    violations = [phrase for phrase in forbidden if phrase.lower() in final_text]

    return {
        "score": 0.0 if violations else 1.0,
        "reason": f"Forbidden phrases found: {violations}" if violations else "No forbidden phrases found",
    }


def grade_expected_route(run_result: dict, expected: dict) -> dict:
    """Checks the supervisor called the expected route tool."""
    expected_route = expected.get("expected_route")
    called_routes = _called_routes(run_result)

    if expected_route is None:
        return {
            "score": 1.0 if not called_routes else 0.0,
            "reason": f"Expected no route tool. Called routes: {called_routes}",
        }

    return {
        "score": 1.0 if expected_route in called_routes else 0.0,
        "reason": f"Expected route: {expected_route} | Called routes: {called_routes}",
    }


def grade_expected_escalation(run_result: dict, expected: dict) -> dict:
    """Checks whether the structured route result had the expected escalation flag."""
    expected_escalation = expected.get("expected_escalation")
    if expected_escalation is None:
        return {"score": 1.0, "reason": "No escalation expectation set"}

    text = _all_text(run_result)
    called_routes = _called_routes(run_result)
    expected_token = f"needs_escalation={expected_escalation}"
    opposite_token = f"needs_escalation={not expected_escalation}"

    if expected_escalation and "route_to_escalation" in called_routes:
        return {"score": 1.0, "reason": "Escalation route was called"}

    if expected_token in text:
        return {"score": 1.0, "reason": f"Found {expected_token}"}

    if opposite_token in text:
        return {"score": 0.0, "reason": f"Found {opposite_token}, expected {expected_token}"}

    if not expected_escalation and "route_to_escalation" not in called_routes:
        return {"score": 1.0, "reason": "No escalation route or escalation flag found"}

    return {
        "score": 0.0,
        "reason": f"No structured escalation flag found. Expected {expected_token}",
    }


def grade_file_written(run_result: dict, expected: dict) -> dict:
    """Checks if the expected file exists when the test case requires one."""
    file_path = expected.get("expected_file")
    if not file_path:
        return {"score": 1.0, "reason": "No file expected"}

    path = Path(file_path)
    exists = os.path.exists(path)
    return {
        "score": 1.0 if exists else 0.0,
        "reason": f"{file_path} found on disk" if exists else f"{file_path} not found",
    }


def grade_under_hop_limit(run_result: dict, expected: dict, max_hops: int = 8) -> dict:
    """Checks the agent finished in a reasonable number of messages."""
    hop_count = len(run_result["messages"])
    passed = hop_count <= max_hops
    return {
        "score": 1.0 if passed else 0.0,
        "reason": f"{hop_count} messages (limit: {max_hops})",
    }
