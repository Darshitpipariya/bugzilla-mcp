"""Bugzilla tools for MCP server"""

import httpx
from typing import Any
from fastmcp.exceptions import ToolError, PromptError
import bugzilla_mcp.utils as utils


async def bug_info(id: int) -> dict[str, Any]:
    """Returns the entire information about a given bugzilla bug id"""

    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")

    try:
        return await utils.bz.bug_info(id)

    except Exception as e:
        raise ToolError(f"Failed to fetch bug info\nReason: {e}")


async def bug_comments(id: int, include_private_comments: bool = False):
    """Returns the comments of given bug id
    Private comments are not included by default
    but can be explicitely requested
    """

    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")

    try:
        all_comments = await utils.bz.bug_comments(id)

        if include_private_comments:
            return all_comments

        public_comments = []

        for comment in all_comments:
            if not comment["is_private"]:
                public_comments.append(comment)

        return public_comments

    except Exception as e:
        raise ToolError(f"Failed to fetch bug comments\nReason: {e}")


async def add_comment(bug_id: int, comment: str, is_private: bool = False) -> dict[str, int]:
    """Add a comment to a bug. It can optionally be private. If success, returns the created comment id."""
    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")
    
    try:
        return await utils.bz.add_comment(bug_id, comment, is_private)
    except Exception as e:
        raise ToolError(f"Failed to create a comment\n{e}")


async def bugs_quicksearch(query: str, limit: int = 50, offset: int = 0) -> list[Any]:
    """Search bugs using bugzilla's quicksearch syntax

    To reduce the token limit & response time, only returns a subset of fields for each bug

    The user can query full details of each bug using the bug_info tool
    """

    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")

    tool_params = utils.bz.params.copy()
    tool_params["quicksearch"] = query
    tool_params["limit"] = limit
    tool_params["offset"] = offset

    r = await utils.bz.client.get(f"{utils.bz.api_url}/bug", params=tool_params)

    if r.status_code != 200:
        raise ToolError(f"Search failed with status code {r.status_code}")

    all_bugs = r.json()["bugs"]

    bugs_with_essential_fields = []

    for bug in all_bugs:
        b = {
            "bug_id": bug["id"],
            "product": bug["product"],
            "component": bug["component"],
            "assigned_to": bug["assigned_to"],
            "status": bug["status"],
            "resolution": bug["resolution"],
            "summary": bug["summary"],
            "last_updated": bug["last_change_time"],
        }

        bugs_with_essential_fields.append(b)

    return bugs_with_essential_fields


async def learn_quicksearch_syntax() -> str:
    """Access the documentation of the bugzilla quicksearch syntax.
    LLM can learn using this tool. Response is in HTML"""

    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{utils.bz.base_url}/page.cgi?id=quicksearch.html")

        if r.status_code != 200:
            raise PromptError(
                f"Failed to fetch bugzilla quicksearch_syntax with status code {r.status_code}"
            )

        return r.text


async def server_url() -> str:
    """bugzilla server's base url"""
    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")
    return utils.bz.base_url


async def bug_url(bug_id: int) -> str:
    """returns the bug url"""
    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")
    return f"{utils.bz.base_url}/show_bug.cgi?id={bug_id}"


async def download_attachments(bug_id: int, dest_dir: str | None = None) -> list[dict[str, Any]]:
    """Download all attachments for a specific bug to a temporary directory.

    If dest_dir is not provided, a local 'tmp' directory in the project root is used.
    """
    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")
    try:
        return await utils.bz.download_attachments(bug_id, dest_dir)
    except Exception as e:
        raise ToolError(f"Failed to download attachments\nReason: {e}")


async def download_attachment(attachment_id: int, dest_dir: str | None = None) -> dict[str, Any]:
    """Download a specific attachment by its ID.

    If dest_dir is not provided, a local 'tmp' directory in the project root is used.
    """
    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")
    try:
        return await utils.bz.download_attachment(attachment_id, dest_dir)
    except Exception as e:
        raise ToolError(f"Failed to download attachment\nReason: {e}")


async def bugs_info(ids: list[int]) -> list[dict[str, Any]]:
    """Get information about multiple bugs in a single request."""
    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")
    try:
        return await utils.bz.bugs_info(ids)
    except Exception as e:
        raise ToolError(f"Failed to fetch batch bug info\nReason: {e}")


async def bugs_comments(ids: list[int]) -> dict[str, list[dict[str, Any]]]:
    """Fetch comments for multiple bugs in parallel."""
    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")
    try:
        return await utils.bz.bugs_comments(ids)
    except Exception as e:
        raise ToolError(f"Failed to fetch batch comments\nReason: {e}")


async def bugs_analysis_context(ids: list[int]) -> dict[str, Any]:
    """Get consolidated prompt-friendly context (info + comments preview) for multiple bugs in parallel."""
    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")
    try:
        return await utils.bz.bugs_analysis_context(ids)
    except Exception as e:
        raise ToolError(f"Failed to fetch bugs analysis context\nReason: {e}")


async def classify_bugs_heuristics(ids: list[int]) -> dict[str, Any]:
    """Automatically classify a list of bugs into TO_FIX, INVALID, or REVIEW_NEEDED based on server-side heuristics.

    Analyzes status, resolution, summaries, and activity in parallel to deliver instant automated triage.
    """
    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")
    try:
        info_list = await utils.bz.bugs_info(ids)

        to_fix = []
        invalid = []
        review_needed = []

        for info in info_list:
            bid = info.get("id")
            status = info.get("status", "")
            resolution = info.get("resolution", "")
            product = info.get("product", "")
            component = info.get("component", "")

            # Heuristics classification
            is_closed_invalid = (
                status in ["RESOLVED", "VERIFIED", "CLOSED"]
                and resolution
                in [
                    "INVALID",
                    "WONTFIX",
                    "DUPLICATE",
                    "WORKSFORME",
                    "NOTABUG",
                ]
            )

            is_active_valid = status in [
                "NEW",
                "ASSIGNED",
                "REOPENED",
                "UNCONFIRMED",
            ]

            bug_summary = {
                "id": bid,
                "summary": info.get("summary"),
                "product": product,
                "component": component,
                "status": status,
                "resolution": resolution,
            }

            if is_closed_invalid:
                invalid.append(bug_summary)
            elif is_active_valid:
                to_fix.append(bug_summary)
            else:
                review_needed.append(bug_summary)

        return {
            "to_fix": to_fix,
            "invalid": invalid,
            "review_needed": review_needed,
        }
    except Exception as e:
        raise ToolError(
            f"Failed to perform heuristics classification\nReason: {e}"
        )


async def analyze_bugs_statistics(ids: list[int]) -> dict[str, Any]:
    """Perform server-side statistical analysis on a batch of bug IDs based on triage classifications.

    Returns breakdown of classifications, product distribution, component distribution,
    severity, priority workload, and assignee distribution with both counts and percentages.
    """
    if utils.bz is None:
        raise ToolError("Bugzilla client not initialized. Please ensure api_key and bugzilla_url headers are provided.")
    try:
        return await utils.bz.bugs_stats_analysis(ids)
    except Exception as e:
        raise ToolError(f"Failed to perform statistical analysis\nReason: {e}")


