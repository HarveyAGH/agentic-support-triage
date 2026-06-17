from pathlib import Path

from ddgs import DDGS
from langchain_core.tools import tool


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FAQ_PATH = (PROJECT_ROOT / "FAQ.md").resolve()
DOCS_DIR = (PROJECT_ROOT / "docs").resolve()
TICKETS_DIR = (PROJECT_ROOT / "tickets").resolve()


@tool
def search_web(query: str) -> str:
    """Search the web for current or factual information on a given topic.

    Use this tool when:
    - A request involves billing policy lookup
    - A request involves known solutions for technical questions
    - You need facts or data you do not already know or that may have changed recently
    - The user explicitly asks you to search the web

    Do NOT use this tool when:
    - You can already answer confidently from your own knowledge
    - The task involves math, logic, or reasoning only
    - The user asks you to read a local file or use data already in context
    - The query is about historical facts well within your training data

    Args:
        query: The search query string to look up on the web.

    Returns:
        A plain text summary of the top search results, or an error message string.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=1))

        if not results:
            return f"No results found for query: '{query}'"

        lines = []
        total_words = 0
        word_limit = 500

        for i, result in enumerate(results, start=1):
            title = result.get("title", "No title")
            body = result.get("body", "")
            url = result.get("href", "")

            snippet = f"[{i}] {title}\n{body}\nSource: {url}"
            snippet_words = len(snippet.split())

            if total_words + snippet_words > word_limit:
                break

            lines.append(snippet)
            total_words += snippet_words

        return "\n\n".join(lines)

    except Exception as e:
        return f"Search failed for query '{query}': {str(e)}"


@tool
def read_file(path: str) -> str:
    """Read approved support documentation only.

    Use this tool when:
    - The FAQ agent needs to answer from approved local documentation
    - The requested file is FAQ.md or a file inside docs/

    Do NOT use this tool when:
    - The content is already present in the conversation history
    - The task requires searching the web or querying a database
    - The user asks to read secrets, source code, env files, or arbitrary local files

    Args:
        path: The approved documentation path to read, such as FAQ.md or docs/refunds.md.

    Returns:
        The full plain text content of the file, or an informative error string.
    """
    try:
        requested = (PROJECT_ROOT / path).resolve()

        is_faq = requested == FAQ_PATH
        is_docs_file = requested.is_relative_to(DOCS_DIR)

        if not is_faq and not is_docs_file:
            return "Error: read_file can only access FAQ.md or files inside docs/."

        if not requested.exists():
            return f"Error: File not found at path '{path}'"

        if not requested.is_file():
            return f"Error: Path '{path}' exists but is not a file"

        return requested.read_text(encoding="utf-8")

    except PermissionError:
        return f"Error: Permission denied when reading '{path}'"
    except Exception as e:
        return f"Error reading approved documentation file '{path}': {str(e)}"


@tool
def write_file(content: str, filename: str) -> str:
    """Write support ticket artifacts only inside the tickets/ folder.

    Creates tickets/ if it does not exist. Writes Markdown ticket notes only.

    Use this tool when:
    - The agent needs to save an escalation note
    - The agent needs to save a billing review note or support ticket summary

    Do NOT use this tool when:
    - The user asks to modify source code, config files, env files, or arbitrary paths
    - The task involves reading files, web operations, or database writes

    Args:
        content: The full text content to write to the file.
        filename: The ticket filename. Directory paths are ignored for safety.

    Returns:
        A confirmation string with the ticket filename, or an informative error string.
    """
    try:
        TICKETS_DIR.mkdir(parents=True, exist_ok=True)

        safe_name = Path(filename).name
        if not safe_name:
            return "Error: filename is required."

        if not safe_name.endswith(".md"):
            safe_name = f"{safe_name}.md"

        target = (TICKETS_DIR / safe_name).resolve()

        if not target.is_relative_to(TICKETS_DIR):
            return "Error: write_file can only write inside tickets/."

        target.write_text(content, encoding="utf-8")
        return f"Successfully wrote ticket file: tickets/{target.name}"

    except PermissionError:
        return f"Error: Permission denied when writing ticket '{filename}'"
    except Exception as e:
        return f"Error writing ticket file '{filename}': {str(e)}"


BILLING_TOOLS = [search_web, write_file]
TECHNICAL_TOOLS = [search_web, write_file]
FAQ_TOOLS = [read_file]
ESCALATION_TOOLS = [write_file]
