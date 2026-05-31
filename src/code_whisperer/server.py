import os

from dotenv import load_dotenv
from groq import AsyncGroq
from mcp.server.fastmcp import FastMCP

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
_MODEL_MAX_TOKENS = os.getenv("GROQ_MAX_TOKENS", "4096")
try:
    MAX_TOKENS = int(_MODEL_MAX_TOKENS)
except ValueError:
    MAX_TOKENS = 4096

_client: AsyncGroq | None = None


def _get_client() -> AsyncGroq:
    global _client
    if _client is None:
        if not API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY not found in environment or .env file. "
                "Get a key at https://console.groq.com/keys"
            )
        _client = AsyncGroq(api_key=API_KEY, timeout=30.0)
    return _client


mcp = FastMCP("code-whisperer", log_level=os.getenv("CODE_WHISPERER_LOG_LEVEL", "ERROR"))

SYSTEM_PROMPTS = {
    "review": """You are an expert code reviewer. Analyze the given code and provide:
1. Potential bugs and runtime errors
2. Security vulnerabilities
3. Style and best practice violations
4. Performance concerns
5. Specific, actionable fixes

Be concise but thorough. Format with clear sections.""",

    "explain": """You are an expert programmer. Explain the given code in plain English.
Cover: what it does, how it works, key logic, input/output, and any notable patterns.
Keep it clear and accessible.""",

    "optimize": """You are a performance expert. Review this code and suggest optimizations for:
1. Speed and algorithmic efficiency
2. Memory usage
3. Code readability and maintainability
4. Recommended alternative implementation

Provide concrete before/after examples where helpful.""",

    "tests": """You are a QA engineer. Generate comprehensive unit tests for the given code.
Use pytest style. Include:
1. Happy path tests
2. Edge cases and boundary conditions
3. Error/failure scenarios
4. Mocking strategy if needed

Output only the test code with minimal explanation.""",

    "ask": "You are an expert programming assistant. Answer the user's question clearly and accurately.",
}


async def _call_groq(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    client = _get_client()
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=MAX_TOKENS,
        )
        if not response.choices:
            return "Error: Groq returned an empty response. Try again or check your input."
        content = response.choices[0].message.content
        if content is None:
            return "Error: Groq returned a null response (content filtered). Try rephrasing your input."
        return content.strip()
    except Exception as e:
        return f"Error calling Groq API: {e}"


@mcp.tool()
async def review_code(code: str, language: str = "") -> str:
    """Review code for bugs, security issues, style problems, and performance concerns.

    Args:
        code: The source code to review.
        language: Programming language (e.g. "python", "javascript"). Auto-detected if empty.
    """
    if not code.strip():
        return "Error: No code provided to review."
    if len(code) > 100000:
        return "Error: Code exceeds 100,000 character limit."
    prompt = f"Language: {language or 'unknown'}\n\n```\n{code}\n```\n\nReview this code thoroughly."
    return await _call_groq(SYSTEM_PROMPTS["review"], prompt)


@mcp.tool()
async def explain_code(code: str, language: str = "") -> str:
    """Explain what a piece of code does in plain English.

    Args:
        code: The source code to explain.
        language: Programming language hint. Auto-detected if empty.
    """
    if not code.strip():
        return "Error: No code provided to explain."
    if len(code) > 100000:
        return "Error: Code exceeds 100,000 character limit."
    prompt = f"Language: {language or 'unknown'}\n\n```\n{code}\n```\n\nExplain what this code does."
    return await _call_groq(SYSTEM_PROMPTS["explain"], prompt, temperature=0.2)


@mcp.tool()
async def optimize_code(code: str, language: str = "") -> str:
    """Suggest performance and readability optimizations for code.

    Args:
        code: The source code to optimize.
        language: Programming language hint. Auto-detected if empty.
    """
    if not code.strip():
        return "Error: No code provided to optimize."
    if len(code) > 100000:
        return "Error: Code exceeds 100,000 character limit."
    prompt = f"Language: {language or 'unknown'}\n\n```\n{code}\n```\n\nSuggest optimizations."
    return await _call_groq(SYSTEM_PROMPTS["optimize"], prompt)


@mcp.tool()
async def generate_tests(code: str, language: str = "python") -> str:
    """Generate unit tests for the given code using pytest.

    Args:
        code: The source code to generate tests for.
        language: Programming language (default: python).
    """
    if not code.strip():
        return "Error: No code provided to generate tests for."
    if len(code) > 100000:
        return "Error: Code exceeds 100,000 character limit."
    prompt = f"Language: {language}\n\n```\n{code}\n```\n\nGenerate comprehensive unit tests."
    return await _call_groq(SYSTEM_PROMPTS["tests"], prompt, temperature=0.4)


@mcp.tool()
async def ask_groq(question: str) -> str:
    """Ask any programming question to the Groq-powered LLM.

    Args:
        question: Your programming question.
    """
    return await _call_groq(SYSTEM_PROMPTS["ask"], question, temperature=0.5)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
