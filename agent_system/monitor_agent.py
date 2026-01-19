#!/usr/bin/env python3
"""Monitor Agent - Uses AI to review code and provide intelligent feedback"""

import glob as globlib, json, os, re, subprocess, urllib.request, time, datetime

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
API_URL = "https://openrouter.ai/api/v1/messages"
MODEL = "mistralai/devstral-2512:free"

FILE = "/home/endrem/prosjekt/nanocode/hello_world.py"
FEEDBACK_FILE = "/home/endrem/prosjekt/nanocode/agent_system/agent_feedback.md"
MONITOR_LOG = "/home/endrem/prosjekt/nanocode/agent_system/monitor_log.txt"

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
    
    if not os.path.exists(MONITOR_LOG):
        with open(MONITOR_LOG, "w") as f:
            f.write("")


def log_monitor(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(MONITOR_LOG, "a") as f:
        f.write(f"{timestamp} - {message}\n")


def agent_review_code():
    """Use AI agent to review code and provide feedback"""
    print(f"\n{CYAN}{BOLD}🤖 AGENT: Reviewing code...{RESET}")
    print(separator())
    
    # Read current code
    code_content = read({"path": FILE})
    
    system_prompt = f"""Concise coding assistant. cwd: {os.path.dirname(FILE)}

You are a code review agent. Your task is to:
1. Read the current code
2. Analyze it for issues (syntax, missing features, best practices)
3. Provide clear, actionable feedback
4. Suggest improvements and feature additions
5. Be concise but thorough

Focus on:
- Syntax errors
- Missing error handling
- Missing user input
- Missing imports
- Code structure improvements
- Security considerations
- Best practices
- Suggested feature additions
- Missing functionality

Provide specific code snippets when suggesting changes."""

    messages = [
        {
            "role": "user",
            "content": f"""Review the following code in {FILE} and provide detailed feedback about issues, improvements, and suggested features.

CODE:
{code_content}

Please provide:
1. A summary of issues found
2. Specific fixes needed
3. Suggested improvements and features
4. Any security or best practice concerns
5. Code suggestions (with actual code to add)"""
        }
    ]
    
    # Agentic loop
    iteration = 0
    full_review = ""
    
    while True:
        iteration += 1
        if iteration > 10:  # Safety limit
            print(f"{RED}Too many iterations, stopping.{RESET}")
            break
        
        response = call_api(messages, system_prompt)
        content_blocks = response.get("content", [])
        tool_results = []
        
        for block in content_blocks:
            if block["type"] == "text":
                print(f"\n{CYAN}⏺{RESET} {block['text']}")
                full_review += block['text'] + "\n\n"
            
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
            # No more tool calls
            print(f"\n{GREEN}{BOLD}✓ Agent review completed.{RESET}")
            break
        messages.append({"role": "user", "content": tool_results})
    
    # Write feedback to file
    with open(FEEDBACK_FILE, "a") as f:
        f.write(f"\n## Review at {datetime.datetime.now()}\n\n")
        f.write("### Current code:\n")
        f.write("```python\n")
        with open(FILE, "r") as code_file:
            f.write(code_file.read())
        f.write("```\n\n")
        f.write("### Agent Review:\n")
        f.write(full_review)
        f.write("\n---\n\n")
    
    log_monitor(f"Agent review completed - {len(full_review)} chars written to feedback")
    print(f"\n{DIM}Feedback written to {FEEDBACK_FILE}{RESET}")


def agent_add_random_feature():
    """Use AI agent to add a creative random feature"""
    print(f"\n{CYAN}{BOLD}🤖 AGENT: Adding creative feature...{RESET}")
    print(separator())
    
    # Read current code
    code_content = read({"path": FILE})
    
    system_prompt = f"""Concise coding assistant. cwd: {os.path.dirname(FILE)}

You are a creative feature addition agent. Your task is to:
1. Read the current code
2. Identify what features are already present
3. Suggest a creative, useful feature to add
4. Implement the feature in the code
5. Ensure the code still works

Focus on creative features like:
- Additional functionality (time, random, user info, etc.)
- Better error handling
- More user interaction
- Visual enhancements (colors, formatting)
- System information
- Helper functions

Be creative but practical. The feature should make the program more interesting or useful."""

    messages = [
        {
            "role": "user",
            "content": f"""Review the current code in {FILE} and add a creative feature.

CODE:
{code_content}

Please:
1. Identify what's already in the code
2. Suggest a creative feature that would enhance the code
3. Implement it using your tools
4. Make sure it's something that hasn't been added yet

The feature should be:
- Creative and interesting
- Not already present in the code
- Makes the program better
- Works correctly with existing code"""
        }
    ]
    
    # Agentic loop
    iteration = 0
    
    while True:
        iteration += 1
        if iteration > 15:  # Safety limit
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
            # No more tool calls - feature should be added
            print(f"\n{GREEN}{BOLD}✓ Feature addition completed.{RESET}")
            break
        messages.append({"role": "user", "content": tool_results})
    
    # Log to feedback
    with open(FEEDBACK_FILE, "a") as f:
        f.write(f"🤖 **AGENT FEATURE**: Added creative enhancement\n\n")
    
    # Log to monitor
    log_monitor(f"Agent added creative feature")
    print(f"\n{DIM}Feature added and logged{RESET}")


def monitor_loop():
    """Main monitoring loop with file watching"""
    print(f"\n{BOLD}{GREEN}🚀 Starting AI Monitor Agent{RESET}")
    print(f"{DIM}Model: {MODEL} | Code: {FILE} | Feedback: {FEEDBACK_FILE}{RESET}")
    print(separator())
    
    init_feedback()
    log_monitor("=== AI MONITOR STARTED ===")
    
    # Initial review
    print(f"\n{CYAN}📋 Performing initial code review...{RESET}")
    agent_review_code()
    
    # Check if inotifywait is available
    try:
        result = subprocess.run(["which", "inotifywait"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"{RED}ERROR: inotifywait not found. Installing...{RESET}")
            log_monitor("ERROR: inotifywait not found")
            print(f"{YELLOW}Please install inotify-tools package{RESET}")
            return
    except:
        print(f"{YELLOW}Warning: Could not check for inotifywait{RESET}")
    
    print(f"\n{CYAN}📁 Starting file monitoring loop...{RESET}")
    log_monitor("Starting file monitoring loop")
    
    iteration = 1
    while True:
        print(f"\n{BLUE}⏳ Waiting for file changes...{RESET}")
        
        # Use inotifywait to monitor file changes
        try:
            proc = subprocess.Popen(
                ["inotifywait", "-e", "modify,create,move,delete", FILE],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output, error = proc.communicate(timeout=300)
            
            if proc.returncode == 0:
                time.sleep(0.5)  # Let file settle
                print(f"\n{GREEN}📝 Change detected!{RESET}")
                print(separator())
                log_monitor(f"=== FILE CHANGE DETECTED - Iteration {iteration} ===")
                
                # Review the code
                agent_review_code()
                
                # Add creative feature
                agent_add_random_feature()
                
                # Review again
                print(f"\n{CYAN}📋 Re-reviewing after feature addition...{RESET}")
                agent_review_code()
                
                print(f"\n{GREEN}✓ Cycle {iteration} complete. Waiting for next change...{RESET}")
                iteration += 1
            else:
                print(f"{YELLOW}inotifywait exited with code {proc.returncode}{RESET}")
                print(f"{DIM}Error: {error}{RESET}")
                log_monitor(f"inotifywait error: {proc.returncode}")
                time.sleep(2)
                
        except subprocess.TimeoutExpired:
            print(f"{YELLOW}Timeout waiting for changes (5 min){RESET}")
            continue
        except FileNotFoundError:
            print(f"{RED}inotifywait not found. Please install inotify-tools{RESET}")
            print(f"{YELLOW}Falling back to manual review mode...{RESET}")
            # Fallback: wait for manual input
            user_input = input(f"\n{BLUE}Press Enter to re-review, or 'q' to quit: {RESET}")
            if user_input.lower() == 'q':
                break
            agent_review_code()
        except KeyboardInterrupt:
            print(f"\n{RED}⏹ Stopping monitor...{RESET}")
            break


if __name__ == "__main__":
    monitor_loop()
