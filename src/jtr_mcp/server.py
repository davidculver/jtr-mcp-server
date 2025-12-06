"""MCP Server for John the Ripper"""
import asyncio
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .tools.crack import crack_passwords_tool
from .jtr_wrapper import JohnTheRipperWrapper
from .config import HASH_FORMATS

# Log to stderr so it shows up immediately
def log(msg):
    print(msg, file=sys.stderr, flush=True)

log("="*50)
log("JTR MCP Server Starting...")
log("="*50)

# Create server instance
app = Server("jtr-mcp-server")

# Initialize JTR wrapper
jtr = JohnTheRipperWrapper()
log(f"JTR wrapper initialized")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    log("list_tools() called")
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
                            f"Hash format (optional, auto-detects if not specified). "
                            f"Common formats: md5crypt, sha256crypt, sha512crypt, bcrypt, descrypt"
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
    log(f"call_tool() called: {name}")
    log(f"Arguments: {arguments}")
    
    if name == "crack_passwords":
        log("Calling crack_passwords_tool...")
        result = await crack_passwords_tool(
            hash_file_content=arguments.get("hash_file_content"),
            wordlist=arguments.get("wordlist", "small"),
            hash_format=arguments.get("hash_format"),
            use_rules=arguments.get("use_rules", False)
        )
        
        log(f"Result: {result}")
        
        # Format response
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
        
        log(f"Returning response: {response[:100]}...")
        return [TextContent(type="text", text=response)]
    
    elif name == "list_hash_formats":
        log("Getting formats...")
        formats = jtr.get_formats()
        
        response = f"📋 Supported Hash Formats ({len(formats)} total)\n\n"
        response += "Common Linux formats:\n"
        for fmt, desc in HASH_FORMATS.items():
            response += f"  • {fmt}: {desc}\n"
        
        response += f"\nTotal formats available: {len(formats)}\n"
        response += "Use 'john --list=formats' for complete list."
        
        return [TextContent(type="text", text=response)]
    
    elif name == "get_jtr_info":
        log("Getting JTR info...")
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
    log("Starting main() server loop...")
    async with stdio_server() as (read_stream, write_stream):
        log("STDIO server started, running app...")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
