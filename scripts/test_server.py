"""Test the MCP server locally"""
import sys
sys.path.insert(0, 'src')

from jtr_mcp.jtr_wrapper import JohnTheRipperWrapper
from jtr_mcp.tools.crack import crack_passwords_tool
import asyncio


async def test_basic_functionality():
    """Test basic JTR wrapper functionality"""
    print("=== Testing JTR Wrapper ===\n")
    
    jtr = JohnTheRipperWrapper()
    
    # Test 1: Get version
    print("1. Version:")
    version = jtr.get_version()
    print(f"   {version}\n")
    
    # Test 2: Get formats
    print("2. Format count:")
    formats = jtr.get_formats()
    print(f"   {len(formats)} formats available\n")
    
    # Test 3: Crack a test password
    print("3. Testing password cracking:")
    hash_content = "testuser:$1$testsalt$.MVZAPrncnxH7sLr8OqHO."
    
    result = await crack_passwords_tool(
        hash_file_content=hash_content,
        wordlist="small",
        hash_format="md5crypt"
    )
    
    print(f"   Success: {result['success']}")
    print(f"   Cracked: {result['cracked_count']}")
    if result['cracked_passwords']:
        print(f"   Passwords: {result['cracked_passwords']}")
    print()
    
    print("=== All Tests Passed! ===")


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
