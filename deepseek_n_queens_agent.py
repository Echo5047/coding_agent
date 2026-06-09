"""
Student scaffold: build a tiny coding agent for the N-Queens homework.

The concrete tools are already implemented for you. Your job is to finish the
small pieces that connect:

DeepSeek response -> tool parser -> Python tool execution -> tool_result message

Your submission should complete the TODO sections in this file.
"""

import inspect
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


WORKSPACE_ROOT = Path(__file__).resolve().parent
DEFAULT_DEEPSEEK_BASE_URL = "http://81.70.208.221:4000/v1"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"

DEFAULT_TASK = """
Complete the N-Queens homework code in the n_queens folder.

You must:
1. Inspect the files in n_queens.
2. Edit only the TODO sections needed for the assignment.
3. Implement backtracking.py and local_search.py.
4. Run both Python files from the n_queens folder.
5. If either run fails, fix the code and run again.

When both scripts run successfully, summarize the changes and the outputs.
"""

SYSTEM_PROMPT = """
You are a small coding agent for an undergraduate homework exercise.
Your job is to solve coding tasks by using tools.

Available tools:

{tool_list_repr}

Rules:
- Use tools to inspect, edit, and test files. Do not guess file contents.
- Work inside this workspace. For this assignment, only edit files in n_queens.
- Prefer small exact edits with edit_file.
- Use run_bash only for bounded commands such as python backtracking.py.
- Do not install packages, delete files, or modify environment variables.
- When you want to use a tool, reply with exactly one line:
  tool: TOOL_NAME({{"arg": "value"}})
- Use compact single-line JSON with double quotes.
- After receiving tool_result(...), continue the task.
- When the task is complete, respond normally without a tool call.
"""

YOU_COLOR = "\u001b[94m"
ASSISTANT_COLOR = "\u001b[93m"
TOOL_COLOR = "\u001b[92m"
RESET_COLOR = "\u001b[0m"


def make_deepseek_client() -> Any:
    """
    Create an OpenAI-compatible client for DeepSeek.
    """
    if OpenAI is None:
        raise RuntimeError("Please install the openai package before running this agent.")

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("Please set DEEPSEEK_API_KEY before running this agent.")

    base_url = os.environ.get("DEEPSEEK_BASE_URL", DEFAULT_DEEPSEEK_BASE_URL)
    return OpenAI(api_key=api_key, base_url=base_url)


def resolve_workspace_path(path_str: str) -> Path:
    """
    Resolve a path and require it to stay inside this homework workspace.
    """
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = WORKSPACE_ROOT / path
    full_path = path.resolve()

    try:
        full_path.relative_to(WORKSPACE_ROOT)
    except ValueError as exc:
        raise ValueError(f"Path escapes workspace: {path_str}") from exc

    return full_path


def read_file_tool(filename: str) -> Dict[str, Any]:
    """
    Read a UTF-8 text file.
    :param filename: File path, relative to the workspace or absolute.
    :return: The file path and full file content.
    """
    full_path = resolve_workspace_path(filename)
    return {
        "file_path": str(full_path),
        "content": full_path.read_text(encoding="utf-8"),
    }


def list_files_tool(path: str = ".") -> Dict[str, Any]:
    """
    List direct children of a workspace directory.
    :param path: Directory path, relative to the workspace or absolute.
    :return: File and directory names with simple type labels.
    """
    full_path = resolve_workspace_path(path)
    files = []
    for item in sorted(full_path.iterdir(), key=lambda p: p.name):
        files.append({
            "filename": item.name,
            "type": "file" if item.is_file() else "dir",
        })
    return {
        "path": str(full_path),
        "files": files,
    }


def edit_file_tool(path: str, old_str: str, new_str: str) -> Dict[str, Any]:
    """
    Replace the first exact occurrence of old_str with new_str in a UTF-8 file.
    If old_str is empty, create or overwrite the file with new_str.
    :param path: File path, relative to the workspace or absolute.
    :param old_str: Exact text to replace.
    :param new_str: Replacement text.
    :return: The file path and edit action.
    """
    full_path = resolve_workspace_path(path)

    if old_str == "":
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(new_str, encoding="utf-8")
        return {
            "path": str(full_path),
            "action": "created_or_overwritten",
        }

    original = full_path.read_text(encoding="utf-8")
    if old_str not in original:
        return {
            "path": str(full_path),
            "action": "old_str_not_found",
        }

    full_path.write_text(original.replace(old_str, new_str, 1), encoding="utf-8")
    return {
        "path": str(full_path),
        "action": "edited",
    }


def run_bash_tool(command: str, cwd: str = "n_queens", timeout_seconds: int = 10) -> Dict[str, Any]:
    """
    Run a short bash command inside the workspace and return captured output.
    :param command: Command to execute, for example "python backtracking.py".
    :param cwd: Working directory, relative to the workspace or absolute.
    :param timeout_seconds: Timeout in seconds. Values above 30 are capped.
    :return: Exit code, stdout, stderr, and timeout status.
    """
    full_cwd = resolve_workspace_path(cwd)
    timeout = min(max(int(timeout_seconds), 1), 30)

    try:
        completed = subprocess.run(
            ["bash", "-lc", command],
            cwd=str(full_cwd),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "cwd": str(full_cwd),
            "command": command,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "cwd": str(full_cwd),
            "command": command,
            "exit_code": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
        }


TOOL_REGISTRY = {
    "read_file": read_file_tool,
    "list_files": list_files_tool,
    "edit_file": edit_file_tool,
    "run_bash": run_bash_tool,
}


def get_tool_str_representation(tool_name: str) -> str:
    """
    Convert one Python tool function into text the model can read.
    """
    tool = TOOL_REGISTRY[tool_name]
    return f"""
Name: {tool_name}
Description: {tool.__doc__}
Signature: {inspect.signature(tool)}
"""


def get_full_system_prompt() -> str:
    """
    Insert every tool description into the system prompt.
    """
    tool_str_repr = ""
    for tool_name in TOOL_REGISTRY:
        tool_str_repr += "TOOL\n====\n"
        tool_str_repr += get_tool_str_representation(tool_name)
        tool_str_repr += f"{'=' * 20}\n"
    return SYSTEM_PROMPT.format(tool_list_repr=tool_str_repr)


def extract_tool_invocations(text: str) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Parse tool calls like: tool: read_file({"filename": "n_queens/backtracking.py"})

    The system prompt asks the model to emit exactly one tool call per line, but
    some models occasionally concatenate calls without a newline.  Splitting on
    every ``tool:`` marker makes the parser tolerant of both forms.
    """
    invocations = []
    decoder = json.JSONDecoder()
    for chunk in text.split("tool:")[1:]:
        tool_text = chunk.strip()
        if not tool_text:
            continue

        try:
            name, rest = tool_text.split("(", 1)
            name = name.strip()
            if not name:
                continue

            args_text = rest.lstrip()
            args, end_idx = decoder.raw_decode(args_text)
            if not isinstance(args, dict):
                continue
            if not args_text[end_idx:].lstrip().startswith(")"):
                continue

            invocations.append((name, args))
        except Exception:
            continue

    return invocations


def execute_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatch one parsed tool call to the matching Python function.
    """
    if name not in TOOL_REGISTRY:
        return {
            "error": f"Unknown tool: {name}",
            "available_tools": list(TOOL_REGISTRY),
        }

    try:
        if name == "read_file":
            return TOOL_REGISTRY[name](args.get("filename", args.get("path", ".")))
        if name == "list_files":
            return TOOL_REGISTRY[name](args.get("path", "."))

        if name == "edit_file":
            return TOOL_REGISTRY[name](
                args.get("path", ""),
                args.get("old_str", ""),
                args.get("new_str", ""),
            )
        if name == "run_bash":
            return TOOL_REGISTRY[name](
                args.get("command", ""),
                args.get("cwd", "n_queens"),
                args.get("timeout_seconds", 10),
            )

    except Exception as exc:
        return {
            "tool": name,
            "args": args,
            "error": str(exc),
        }

    return {"error": f"No executor branch for tool: {name}"}


def execute_deepseek_call(client: Any, conversation: List[Dict[str, str]]) -> str:
    """
    Send the conversation to DeepSeek and return the assistant text.
    """
    model = os.environ.get("DEEPSEEK_MODEL", DEFAULT_DEEPSEEK_MODEL)
    response = client.chat.completions.create(
        model=model,
        messages=conversation,
        temperature=0,
        max_tokens=2000,
    )
    return response.choices[0].message.content or ""


def run_agent(task: str = DEFAULT_TASK, max_turns: int = 30) -> None:
    """
    TODO: finish the agent loop.

    Only three interaction pieces are missing below:
    3. Add the first user task message to conversation.
    4. Call DeepSeek to get assistant_response.
    5. Add each tool_result(...) message back into conversation.
    """
    client = make_deepseek_client()
    conversation = [
        {"role": "system", "content": get_full_system_prompt()},
        {"role": "user", "content": task.strip()},
    ]

    print(f"{YOU_COLOR}Task:{RESET_COLOR} {task.strip()}\n")

    for turn in range(max_turns):
        assistant_response = execute_deepseek_call(client, conversation)

        print(f"{ASSISTANT_COLOR}Assistant:{RESET_COLOR} {assistant_response}")
        conversation.append({"role": "assistant", "content": assistant_response})

        tool_invocations = extract_tool_invocations(assistant_response)
        if not tool_invocations:
            return

        for name, args in tool_invocations:
            print(f"{TOOL_COLOR}Tool:{RESET_COLOR} {name}({json.dumps(args)})")
            tool_result = execute_tool(name, args)
            result_text = json.dumps(tool_result, ensure_ascii=False)
            print(f"{TOOL_COLOR}Result:{RESET_COLOR} {result_text}\n")

            conversation.append({"role": "user", "content": f"tool_result({result_text})"})

    print(f"{ASSISTANT_COLOR}Assistant:{RESET_COLOR} Reached max_turns={max_turns}.")


if __name__ == "__main__":
    run_agent()
