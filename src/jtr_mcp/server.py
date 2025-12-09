"""MCP Server for John the Ripper"""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .tools.crack import crack_passwords_tool
from .tools.unshadow import unshadow_files_tool
from .tools.session import manage_session_tool
from .tools.status import check_status_tool
from .jtr_wrapper import JohnTheRipperWrapper
from .config import HASH_FORMATS, logger

logger.info("="*50)
logger.info("JTR MCP Server Starting...")
logger.info("="*50)

# Create server instance
app = Server("jtr-mcp-server")

# Initialize JTR wrapper
jtr = JohnTheRipperWrapper()
logger.info("JTR wrapper initialized")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    logger.info("list_tools() called")
    return [
        Tool(
            name="crack_passwords",
            description=(
                "Crack password hashes using John the Ripper. "
                "Supports dictionary attacks with optional word mangling rules. "
                "Automatically detects hash format or you can specify it."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "hash_file_content": {
                        "type": "string",
                        "description": (
                            "Content of hash file in john format. "
                            "Examples: 'user:$6$salt$hash' for SHA-512, "
                            "'user:$1$salt$hash' for MD5-crypt"
                        )
                    },
                    "wordlist": {
                        "type": "string",
                        "description": (
                            "Wordlist to use: 'small' (17 words, fast), "
                            "'medium' (10k words), 'large' (rockyou, 14M words), "
                            "or path to custom wordlist file"
                        ),
                        "default": "small"
                    },
                    "hash_format": {
                        "type": "string",
                        "description": (
                            "Hash format (optional, auto-detects if not specified). "
                            "Common formats: md5crypt, sha256crypt, sha512crypt, bcrypt, descrypt"
                        )
                    },
                    "use_rules": {
                        "type": "boolean",
                        "description": "Apply word mangling rules (slower but more thorough)",
                        "default": False
                    }
                },
                "required": ["hash_file_content"]
            }
        ),
        Tool(
            name="unshadow_files",
            description=(
                "Combine /etc/passwd and /etc/shadow files for password cracking. "
                "This is the standard workflow for cracking Linux password files. "
                "Returns combined content to use with crack_passwords tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "passwd_content": {
                        "type": "string",
                        "description": "Content of /etc/passwd file"
                    },
                    "shadow_content": {
                        "type": "string",
                        "description": "Content of /etc/shadow file"
                    }
                },
                "required": ["passwd_content", "shadow_content"]
            }
        ),
        Tool(
            name="manage_session",
            description=(
                "Manage John the Ripper cracking sessions. "
                "List existing sessions, delete sessions, or get session info. "
                "Useful for managing long-running password cracks."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform: 'list', 'delete', or 'info'",
                        "enum": ["list", "delete", "info"]
                    },
                    "session_name": {
                        "type": "string",
                        "description": "Session name (required for delete/info actions)",
                        "default": "default"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="check_status",
            description=(
                "Check John the Ripper status and see recently cracked passwords. "
                "Shows total count of cracked passwords and recent entries from john.pot file."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_hash_formats",
            description="List all supported hash formats in John the Ripper",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_jtr_info",
            description="Get information about John the Ripper installation",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    logger.info(f"call_tool() called: {name}")
    logger.info(f"Arguments: {arguments}")
    
    if name == "crack_passwords":
        result = await crack_passwords_tool(
            hash_file_content=arguments.get("hash_file_content"),
            wordlist=arguments.get("wordlist", "small"),
            hash_format=arguments.get("hash_format"),
            use_rules=arguments.get("use_rules", False)
        )
        
        if result["success"]:
            response = f"✅ Password cracking completed!\n\n"
            response += f"Cracked {result['cracked_count']} password(s)\n"
            response += f"Wordlist: {result['wordlist_used']}\n"
            response += f"Format: {result['format_used']}\n\n"
            
            if result["cracked_passwords"]:
                response += "Cracked passwords:\n"
                for entry in result["cracked_passwords"]:
                    response += f"  {entry}\n"
            else:
                response += "No passwords cracked with this wordlist.\n"
        else:
            response = f"❌ Error: {result.get('error', 'Unknown error')}"
        
        return [TextContent(type="text", text=response)]
    
    elif name == "unshadow_files":
        result = await unshadow_files_tool(
            passwd_content=arguments.get("passwd_content"),
            shadow_content=arguments.get("shadow_content")
        )
        
        if result["success"]:
            response = f"✅ Files combined successfully!\n\n"
            response += f"Combined {result['line_count']} user entries\n\n"
            response += "Combined content (ready for crack_passwords):\n"
            response += "```\n"
            response += result["combined_content"]
            response += "\n```\n\n"
            response += "💡 Tip: Copy the combined content above and use it with the crack_passwords tool."
        else:
            response = f"❌ Error: {result.get('error', 'Unknown error')}"
        
        return [TextContent(type="text", text=response)]
    
    elif name == "manage_session":
        result = await manage_session_tool(
            action=arguments.get("action"),
            session_name=arguments.get("session_name", "default")
        )
        
        if result["success"]:
            if result["action"] == "list":
                response = f"📋 Cracking Sessions ({result['count']} total)\n\n"
                if result["sessions"]:
                    for session in result["sessions"]:
                        response += f"  • {session['name']} ({session['size_bytes']} bytes)\n"
                else:
                    response += "No sessions found.\n"
            elif result["action"] == "delete":
                response = f"✅ {result['message']}"
            elif result["action"] == "info":
                response = f"ℹ️  Session Information\n\n"
                response += f"Name: {result['session_name']}\n"
                response += f"Size: {result['size_bytes']} bytes\n"
                response += f"Last modified: {result['last_modified']}\n"
                response += f"File: {result['file_path']}\n"
        else:
            response = f"❌ Error: {result.get('error', 'Unknown error')}"
        
        return [TextContent(type="text", text=response)]
    
    elif name == "check_status":
        result = await check_status_tool()
        
        if result["success"]:
            response = f"📊 John the Ripper Status\n\n"
            response += f"Total cracked: {result['cracked_count']} passwords\n"
            
            if result['pot_file']:
                response += f"Pot file: {result['pot_file']}\n"
                if result.get('last_updated'):
                    response += f"Last updated: {result['last_updated']}\n"
            
            if result.get('recent_cracks'):
                response += f"\nRecent cracks (last 5):\n"
                for crack in result['recent_cracks']:
                    response += f"  {crack}\n"
            elif result['cracked_count'] == 0:
                response += f"\n{result['message']}\n"
        else:
            response = f"❌ Error: {result.get('error', 'Unknown error')}"
        
        return [TextContent(type="text", text=response)]
    
    elif name == "list_hash_formats":
        formats = jtr.get_formats()
        
        response = f"📋 Supported Hash Formats ({len(formats)} total)\n\n"
        response += "Common Linux formats:\n"
        for fmt, desc in HASH_FORMATS.items():
            response += f"  • {fmt}: {desc}\n"
        
        response += f"\nTotal formats available: {len(formats)}\n"
        response += "Use 'john --list=formats' for complete list."
        
        return [TextContent(type="text", text=response)]
    
    elif name == "get_jtr_info":
        version = jtr.get_version()
        formats = jtr.get_formats()
        
        response = f"ℹ️  John the Ripper Information\n\n"
        response += f"Version: {version}\n"
        response += f"Total formats: {len(formats)}\n"
        response += f"Command: {jtr.john_binary}\n"
        
        return [TextContent(type="text", text=response)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server"""
    logger.info("Starting main() server loop...")
    async with stdio_server() as (read_stream, write_stream):
        logger.info("STDIO server started, running app...")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
