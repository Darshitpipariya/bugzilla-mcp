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
    create_bug,
    update_bug,
    bug_history,
    bugs_advanced_search,
    bug_dependencies,
    duplicate_chain,
    get_user,
    search_users,
    list_products,
    get_product_components,
    upload_attachment,
    tag_comment,
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
mcp.tool()(create_bug)
mcp.tool()(update_bug)
mcp.tool()(bug_history)
mcp.tool()(bugs_advanced_search)
mcp.tool()(bug_dependencies)
mcp.tool()(duplicate_chain)
mcp.tool()(get_user)
mcp.tool()(search_users)
mcp.tool()(list_products)
mcp.tool()(get_product_components)
mcp.tool()(upload_attachment)
mcp.tool()(tag_comment)


# start the MCP server (only when run directly, not during import/inspection)
if __name__ == "__main__":
    mcp.run(transport="http")
