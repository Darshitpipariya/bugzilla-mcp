from dotenv import load_dotenv
from fastmcp import FastMCP
from bugzilla_mcp.middleware import ValidateHeaders
from bugzilla_mcp.tools.bugzilla import (
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
    analyze_bugs_statistics,
)

# Load environment variables from .env file
load_dotenv()

mcp = FastMCP("Bugzilla")

mcp.add_middleware(ValidateHeaders())

# Register tools from bugzilla_mcp module
mcp.tool()(bug_info)
mcp.tool()(bug_comments)
mcp.tool()(add_comment)
mcp.tool()(bugs_quicksearch)
mcp.tool()(learn_quicksearch_syntax)
mcp.tool()(server_url)
mcp.tool()(bug_url)
mcp.tool()(download_attachments)
mcp.tool()(download_attachment)
mcp.tool()(bugs_info)
mcp.tool()(bugs_comments)
mcp.tool()(bugs_analysis_context)
mcp.tool()(classify_bugs_heuristics)
mcp.tool()(analyze_bugs_statistics)



# start the MCP server (only when run directly, not during import/inspection)
if __name__ == "__main__":
    mcp.run(transport="http")
