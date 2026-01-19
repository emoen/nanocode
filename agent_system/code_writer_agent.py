#!/usr/bin/env python3
"""Code Writer Agent - Uses AI to read feedback and write code"""

import glob as globlib, json, os, re, subprocess, urllib.request, time

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
API_URL = "https://openrouter.ai/api/v1/messages"
MODEL = "xiaomi/mimo-v2-flash:free"

FILE = "/home/endrem/prosjekt/nanocode/hello_world.py"
FEEDBACK_FILE = "/home/endrem/prosjekt/nanocode/agent_system/agent_feedback.md"

# ANSI colors
RESET, BOLD, DIM = "\033[0m", "\033[1m", "\033[2m"
BLUE, CYAN, GREEN, YELLOW, RED = (
    "\033[34m",
    "\033[36m",
    "\033[32m",
    "\033[33m",
    "\033[31m",
)


# --- Tools ---

def read(args):
    lines = open(args["path"]).readlines()
    offset = args.get("offset", 0)
    limit = args.get("limit", len(lines))
    selected = lines[offset : offset + limit]
    return "".join(f"{offset + idx + 1:4}| {line}" for idx, line in enumerate(selected))


def write(args):
    with open(args["path"], "w") as f:
        f.write(args["content"])
    return "ok"


def edit(args):
    text = open(args["path"]).read()
    old, new = args["old"], args["new"]
    if old not in text:
        return "error: old_string not found"
    count = text.count(old)
    if not args.get("all") and count > 1:
        return f"error: old_string appears {count} times, must be unique (use all=true)"
    replacement = (
        text.replace(old, new) if args.get("all") else text.replace(old, new, 1)
    )
    with open(args["path"], "w") as f:
        f.write(replacement)
    return "ok"


def bash(args):
    proc = subprocess.Popen(
        args["cmd"], shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True
    )
    output_lines = []
    try:
        while True:
            line = proc.stdout.readline()
            if not line and proc.poll() is not None:
                break
            if line:
                output_lines.append(line)
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        output_lines.append("\n(timed out after 30s)")
    return "".join(output_lines).strip() or "(empty)"


# --- Tool definitions ---

TOOLS = {
    "read": (
        "Read file with line numbers (file path, not directory)",
        {"path": "string", "offset": "number?", "limit": "number?"},
        read,
    ),
    "write": (
        "Write content to file",
        {"path": "string", "content": "string"},
        write,
    ),
    "edit": (
        "Replace old with new in file (old must be unique unless all=true)",
        {"path": "string", "old": "string", "new": "string", "all": "boolean?"},
        edit,
    ),
    "bash": (
        "Run shell command",
        {"cmd": "string"},
        bash,
    ),
}


def run_tool(name, args):
    try:
        return TOOLS[name][2](args)
    except Exception as err:
        return f"error: {err}"


def make_schema():
    result = []
    for name, (description, params, _fn) in TOOLS.items():
        properties = {}
        required = []
        for param_name, param_type in params.items():
            is_optional = param_type.endswith("?")
            base_type = param_type.rstrip("?")
            properties[param_name] = {
                "type": "integer" if base_type == "number" else base_type
            }
            if not is_optional:
                required.append(param_name)
        result.append(
            {
                "name": name,
                "description": description,
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
        )
    return result


def call_api(messages, system_prompt):
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(
            {
                "model": MODEL,
                "max_tokens": 8192,
                "system": system_prompt,
                "messages": messages,
                "tools": make_schema(),
            }
        ).encode(),
        headers={
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            **({"Authorization": f"Bearer {OPENROUTER_KEY}"} if OPENROUTER_KEY else {"x-api-key": os.environ.get("ANTHROPIC_API_KEY", "")}),
        },
    )
    response = urllib.request.urlopen(request)
    return json.loads(response.read())


def separator():
    return f"{DIM}{'─' * min(os.get_terminal_size().columns, 80)}{RESET}"


def init_feedback():
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w") as f:
            f.write("# Agent Feedback Log\n\n---\n\n")


def get_new_feedback():
    """Read only new feedback since last read"""
    with open(FEEDBACK_FILE, "r") as f:
        content = f.read()
    
    # Extract content after "---" separator (actual reviews)
    if "---" in content:
        parts = content.split("---", 1)
        if len(parts) > 1:
            return parts[1].strip()
    return content


def clear_feedback():
    with open(FEEDBACK_FILE, "w") as f:
        f.write("# Agent Feedback Log\n\n---\n\n")


def agent_process_feedback():
    """Use AI agent to read feedback and write code"""
    print(f"\n{CYAN}{BOLD}🤖 AGENT: Reading feedback and writing code...{RESET}")
    print(separator())
    
    feedback = get_new_feedback()
    if not feedback or feedback == "# Agent Feedback Log":
        print(f"{YELLOW}No new feedback found.{RESET}")
        return False
    
    print(f"\n{DIM}📋 Feedback received:{RESET}\n")
    print(f"{DIM}{feedback}{RESET}\n")
    
    # Read current code
    code = read({"path": FILE})
    
    system_prompt = f"""Concise coding assistant. cwd: {os.path.dirname(FILE)}
    
You are an automated code writer. Your task is to:
1. Read the feedback from the monitor/agent
2. Read the current code
3. Apply the requested changes to fix issues or add features
4. Verify the changes work

Be precise and only make necessary changes."""
    
    messages = [
        {
            "role": "user",
            "content": f"""Read the feedback below and update the code in {FILE}.

FEEDBACK:
{feedback}

CURRENT CODE:
{code}

Please read the code, analyze the feedback, and apply the necessary changes to fix the issues or add the requested features."""
        }
    ]
    
    # Agentic loop
    iteration = 0
    while True:
        iteration += 1
        if iteration > 20:  # Safety limit
            print(f"{RED}Too many iterations, stopping.{RESET}")
            break
        
        response = call_api(messages, system_prompt)
        content_blocks = response.get("content", [])
        tool_results = []
        
        for block in content_blocks:
            if block["type"] == "text":
                print(f"\n{CYAN}⏺{RESET} {block['text']}")
            
            if block["type"] == "tool_use":
                tool_name = block["name"]
                tool_args = block["input"]
                arg_preview = str(list(tool_args.values())[0])[:50]
                print(f"\n{GREEN}⏺ {tool_name.capitalize()}{RESET}({DIM}{arg_preview}{RESET})")
                
                result = run_tool(tool_name, tool_args)
                result_lines = result.split("\n")
                preview = result_lines[0][:60]
                if len(result_lines) > 1:
                    preview += f" ... +{len(result_lines) - 1} lines"
                elif len(result_lines[0]) > 60:
                    preview += "..."
                print(f"  {DIM}⎿  {preview}{RESET}")
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": result,
                })
        
        messages.append({"role": "assistant", "content": content_blocks})
        
        if not tool_results:
            # No more tool calls, check if agent is done
            print(f"\n{GREEN}{BOLD}✓ Agent has completed the code changes.{RESET}")
            break
        messages.append({"role": "user", "content": tool_results})
    
    # Clear feedback for next cycle
    clear_feedback()
    print(f"\n{DIM}Feedback cleared for next cycle.{RESET}")
    return True


def main_loop():
    print(f"\n{BOLD}{GREEN}🚀 Starting Agent-Based Code Writer{RESET}")
    print(f"{DIM}Model: {MODEL} | Code: {FILE} | Feedback: {FEEDBACK_FILE}{RESET}")
    print(separator())
    
    init_feedback()
    iteration = 1
    
    while True:
        print(f"\n{BOLD}{BLUE}═══ Iteration {iteration} ═══{RESET}")
        print(f"\n{DIM}Current code:{RESET}\n")
        print(read({"path": FILE}))
        print(separator())
        
        # Process feedback if available
        agent_process_feedback()
        
        print(f"\n{DIM}Waiting for new feedback...{RESET}")
        
        # Wait for new feedback (polling)
        last_size = os.path.getsize(FEEDBACK_FILE)
        timeout = 0
        while timeout < 60:
            if os.path.exists(FEEDBACK_FILE):
                current_size = os.path.getsize(FEEDBACK_FILE)
                if current_size > last_size:
                    # Check if actually has new content (not just header)
                    with open(FEEDBACK_FILE, "r") as f:
                        content = f.read()
                    if "---" in content:
                        new_part = content.split("---", 1)[1].strip()
                        if new_part:
                            break
            time.sleep(2)
            timeout += 1
        
        if timeout >= 60:
            print(f"{YELLOW}Timeout waiting for feedback (60s){RESET}")
            continue
        
        print(f"\n{GREEN}New feedback detected!{RESET}")
        time.sleep(1)
        iteration += 1


if __name__ == "__main__":
    main_loop()
