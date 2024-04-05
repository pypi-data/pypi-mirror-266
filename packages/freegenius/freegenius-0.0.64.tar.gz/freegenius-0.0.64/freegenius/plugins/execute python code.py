"""
FreeGenius AI Plugin - execute python code

execute python code

[FUNCTION_CALL]
"""

from freegenius import config, fineTunePythonCode, showRisk, confirmExecution, getPygmentsStyle
from freegenius import print1, print2, print3
from freegenius.utils.shared_utils import SharedUtil
from freegenius.utils.single_prompt import SinglePrompt
import pygments
from pygments.lexers.python import PythonLexer
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import print_formatted_text
from prompt_toolkit.styles import Style

def execute_python_code(function_args):
    # retrieve argument values from a dictionary
    risk = function_args.get("risk") # required
    title = function_args.get("title") # required
    python_code = function_args.get("code") # required
    refinedCode = fineTunePythonCode(python_code)

    promptStyle = Style.from_dict({
        # User input (default text).
        "": config.terminalCommandEntryColor2,
        # Prompt.
        "indicator": config.terminalPromptIndicatorColor2,
    })

    # show pyton code for developer
    print1(config.divider)
    print1(f"Python: {title}")
    showRisk(risk)
    if config.developer or config.codeDisplay:
        print1("```")
        #print(python_code)
        # pygments python style
        tokens = list(pygments.lex(python_code, lexer=PythonLexer()))
        print_formatted_text(PygmentsTokens(tokens), style=getPygmentsStyle())
        print1("```")
    print1(config.divider)

    config.stopSpinning()
    if not config.runPython:
        return "[INVALID]"
    elif confirmExecution(risk):
        print1("Do you want to execute it? [y]es / [N]o")
        confirmation = SinglePrompt.run(style=promptStyle, default="y")
        if not confirmation.lower() in ("y", "yes"):
            config.runPython = False
            return "[INVALID]"
    return SharedUtil.executePythonCode(refinedCode)

functionSignature = {
    "examples": [
        "Run python code",
        "Run system command",
        "Execute python code",
        "Execute system command",
        "Execute computing task",
    ],
    "name": "execute_python_code",
    "description": "Execute python code to execute a computing task or access device information",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code that integrates any relevant packages to resolve my request",
            },
            "title": {
                "type": "string",
                "description": "title for the python code",
            },
            "risk": {
                "type": "string",
                "description": "Assess the risk level of damaging my device upon executing the task. e.g. file deletions or similar significant impacts are regarded as 'high' level.",
                "enum": ["high", "medium", "low"],
            },
        },
        "required": ["code", "title", "risk"],
    },
}

config.addFunctionCall(signature=functionSignature, method=execute_python_code)


### A dummy function to redirect q&a task about python, otherwise, it may be mistaken by execute_python_code
def python_qa(_):
    return "[INVALID]"
functionSignature = {
    "examples": [
        "How in python",
    ],
    "name": "python_qa",
    "description": f'''Answer questions or provide information about python''',
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "my query",
            },
        },
    },
}
config.addFunctionCall(signature=functionSignature, method=python_qa)