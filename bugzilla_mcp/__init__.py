"""MCP package for Bugzilla server"""

from .tools.bugzilla import (
    bug_info,
    bug_comments,
    add_comment,
    bugs_quicksearch,
    learn_quicksearch_syntax,
    server_url,
    bug_url,
    download_attachments,
    download_attachment,
    bugs_info,
    bugs_comments,
    bugs_analysis_context,
    classify_bugs_heuristics,
)

__all__ = [
    "bug_info",
    "bug_comments",
    "add_comment",
    "bugs_quicksearch",
    "learn_quicksearch_syntax",
    "server_url",
    "bug_url",
    "download_attachments",
    "download_attachment",
    "bugs_info",
    "bugs_comments",
    "bugs_analysis_context",
    "classify_bugs_heuristics",
]

