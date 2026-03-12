from Chatbot.mcp import FSTools
from llama_cpp import Llama
import os
import json
import re


class FSChatbot:

    def __init__(self, fs_tools: FSTools):
        self.fs_tools  = fs_tools          # FSTools instance for execution
        self.tools     = FSTools.TOOLS
        self.llm       = None
        self.load_model()

    def load_model(self):
        self.llm = Llama(
            model_path=os.getenv("qwen2.5-1.5b-instruct-q8_0"),
            n_ctx=8192,
            n_threads=8,
            n_gpu_layers=0,
            verbose=False,
        )

    # ─────────────────────────────────────────────
    # Prompt
    # ─────────────────────────────────────────────
    def build_prompt(self, message: str) -> str:
        tool_names = [t["name"] for t in self.tools]
        tools_json = json.dumps(self.tools, indent=2)

        return f"""<|im_start|>system
You are a filesystem assistant. Your ONLY job is to output a single JSON tool call.

Available tools: {tool_names}

{tools_json}

Rules:
- Output ONLY valid JSON, nothing else.
- No explanation, no markdown, no extra text.
- Format: {{"name":"<tool_name>","arguments":{{...}}}}
- If no tool matches, output: {{"name":"none","arguments":{{}}}}
<|im_end|>
<|im_start|>user
{message}
<|im_end|>
<|im_start|>assistant
"""
    # ─────────────────────────────────────────────
    # Format tool result → markdown via LLM
    # ─────────────────────────────────────────────
    def _build_format_prompt(self, user_message: str, tool_name: str, result) -> str:
        return f"""<|im_start|>system
You are a helpful assistant. Format the tool result below as clean Markdown that directly answers the user's request.

Rules:
- Use headings, bullet lists, code blocks, bold, tables where appropriate.
- Be concise. Do not repeat the user's question.
- Do not mention tool names or internal details.
- If the result is an error, explain it clearly in plain language.
<|im_end|>
<|im_start|>user
User asked: {user_message}
Tool used:  {tool_name}
Result:     {result}
<|im_end|>
<|im_start|>assistant
"""

    def format_result(self, user_message: str, tool_name: str, result) -> str:
        prompt = self._build_format_prompt(user_message, tool_name, result)
        output = self.llm(
            prompt,
            max_tokens=1024,
            temperature=0.3,
            top_p=0.85,
            top_k=40,
            repeat_penalty=1.1,
            stop=["<|im_end|>", "<|im_start|>"],
        )
        return output["choices"][0]["text"].strip()

    # ─────────────────────────────────────────────
    # Public chat entry point  ← updated
    # ─────────────────────────────────────────────
    def chat(self, message: str) -> str:
        tool_call = self.get_tool_call(message)
        print(f"[tool call] {tool_call}")       # debug

        name   = tool_call.get("name", "none")
        result = self._execute(tool_call)

        print(f"[raw result] {result}")         # debug

        # second LLM pass: raw result → clean markdown
        return self.format_result(message, name, result)
    # ─────────────────────────────────────────────
    # Extract JSON robustly from LLM output
    # ─────────────────────────────────────────────
    def _extract_json(self, text: str) -> dict:
        text = text.strip()

        # 1. direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. pull first {...} block
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # 3. fallback
        return {"name": "none", "arguments": {}}

    # ─────────────────────────────────────────────
    # LLM call
    # ─────────────────────────────────────────────
    def get_tool_call(self, message: str) -> dict:
        prompt = self.build_prompt(message)
        output = self.llm(
            prompt,
            max_tokens=256,
            temperature=0.05,
            top_p=0.70,
            top_k=20,
            repeat_penalty=1.12,
            stop=["<|im_end|>", "<|im_start|>"],
        )
        raw = output["choices"][0]["text"].strip()
        print(f"[LLM raw] {raw}")          # debug — remove in production
        return self._extract_json(raw)

    # ─────────────────────────────────────────────
    # Execute tool call on FSTools
    # ─────────────────────────────────────────────
    def _execute(self, tool_call: dict):
        name = tool_call.get("name", "none")
        args = tool_call.get("arguments", {})

        if name == "none":
            return "I couldn't determine which action to take. Please rephrase."

        fn = getattr(self.fs_tools, name, None)
        if fn is None:
            return f"Unknown tool: '{name}'"

        try:
            return fn(**args)
        except TypeError as e:
            return f"Argument error for '{name}': {e}"

    # ─────────────────────────────────────────────
    # Public chat entry point
    # ─────────────────────────────────────────────
    def chat(self, message: str):
        tool_call = self.get_tool_call(message)
        print(f"[tool call] {tool_call}")   # debug — remove in production
        result = self._execute(tool_call)
        return self.format_result(message,tool_call.get('name',''),result)


# ─────────────────────────────────────────────────
# Bootstrap
# ─────────────────────────────────────────────────


# from task import TaskPerformer          # whatever wires up your FS backend
# # task    = TaskPerformer()
# # fs      = FSTools(task)

# bot = FSChatbot(llm, FSTools.TOOLS, [])
# print(bot.chat("i want to create folder"))