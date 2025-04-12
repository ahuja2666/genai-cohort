import json
import subprocess
import threading
from dotenv import load_dotenv
from openai import OpenAI
import os
load_dotenv()

client = OpenAI()

running_processes = {}

def is_background_command(command: str) -> bool:
    background_keywords = [
        # JavaScript/Node.js
        "serve", "start", "dev", "watch", "nodemon", "webpack-dev-server", "vite",
        
        # Python
        "manage.py runserver", "flask run", "uvicorn", "gunicorn", "fastapi", 
        
        # General
        "tail -f"
    ]
    
    return any(keyword in command for keyword in background_keywords)

def run_command(command: str):
    try:
        background = is_background_command(command)

        if background:
            # Background long-running process
            def stream_output(process, cmd_id):
                for line in iter(process.stdout.readline, ''):
                    print(f"[{cmd_id}] {line.strip()}")
                process.stdout.close()

            process = subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            cmd_id = len(running_processes) + 1
            running_processes[cmd_id] = process

            thread = threading.Thread(target=stream_output, args=(process, cmd_id))
            thread.daemon = True
            thread.start()

            # Write password and y/n input if prompted
            process.stdin.write("Coder_boy@69\ny\n")
            process.stdin.flush()

            return f"Command is running in the background with ID: {cmd_id}"
        
        else:
            # Blocking command (finite)
            process = subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output, error = process.communicate(input="Coder_boy@69\ny\n")

            if process.returncode == 0:
                return output
            else:
                return error

    except Exception as e:
        return str(e)


def get_system_info():
    system_info = os.uname().sysname if hasattr(os, 'uname') else os.name
    if system_info == "posix":
        if os.path.exists("/System/Library"):
            return "MacOS"
        else:
            return "Linux"
    elif system_info == "nt":
        return "Windows"
    else:
        return "Unknown"


avaiable_tools = {
    "run_command": {
        "fn": run_command,
        "description": "Takes a command as input to execute on system and returns ouput"
    },
    "get_system_info": {
        "fn": get_system_info,
        "description": "Returns the operating system type (Windows, MacOS, Linux, or Unknown)"
    }
}

system_prompt = f"""
    You are a helpful AI Assistant who is specialized in building full stack applications using JavaScript and Python.
    You work on start, plan, action, observe mode.
    For the given user query and available tools, plan the step-by-step execution. Based on the planning,
    select the relevant tool from the available tools, and based on the tool selection, you perform an action to call the tool.
    Wait for the observation and based on the observation from the tool call, resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for the next input.
    - Carefully analyze the user query.
    - Don't run any command which can harm the system.
    - Don't run any command which is not necessary.
    - Make sure to cd into the directory where the command needs to be run.
    - if some command is asking for y/n then just give y and proceed
    - if there is sudo command and it's not harmful then just run it.
    - after sudo command, if it is asking for password then just give password Coder_boy@69 and proceed
    - make sure to run command in the seprate terminal and swtich terminals if you need user input
    - skip steps if they are not necessary.
    - output step is necessary to show the final output.


    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of the function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    {json.dumps({tool: details["description"] for tool, details in avaiable_tools.items()}, indent=4)}

    Example:
    User Query: Can you build a react application?
    Output: {{ "step": "plan", "content": "The user wants you to create a React application using Vite." }}
    Output: {{ "step": "plan", "content": "Gather information on what you need to do to create a React application on that system." }}
    Output: {{ "step": "plan", "content": "If you want some more info, ask for it, like whether the user wants it to be in JavaScript or TypeScript." }}
    Output: {{ "step": "plan", "content": "Analyze what command you need to run." }}
    Output: {{ "step": "action", "function": "run_command", "input": "command" }}
    Output: {{ "step": "observe", "output": "See the output of the command. If the output is an error, like 'node not found,' then find the command to install Node on the user's system. basically if there is error try to resolve them." }}
    Output: {{ "step": "plan", "content": "check if you need system info" }}
    Output: {{ "step": "get_system", "function": "get_system_info" }}
    Output: {{ "step": "action", "function": "run_command", "input": "command", "content": "use the system info, so run the command to install Node on system." }}
    Output: {{ "step": "output", "content": "React project create in this folder start it using npm start or somthing view on this port http://localhost:3000" }}
"""

messages = [
    { "role": "system", "content": system_prompt }
]

while True:
    user_query = input('> ')
    messages.append({ "role": "user", "content": user_query })

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=messages
        )

        parsed_output = json.loads(response.choices[0].message.content)
        messages.append({ "role": "assistant", "content": json.dumps(parsed_output) })

        if parsed_output.get("step") == "plan" or parsed_output.get("step") == "observe":
            print(f"🧠: {parsed_output.get("content")}")
            continue
        
        if parsed_output.get("step") == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")
            print(f"🧠: running {tool_name}: {tool_input}")

            if avaiable_tools.get(tool_name, False) != False:
                output = avaiable_tools[tool_name].get("fn")(tool_input)
                print(f"🧠: output {tool_name}: {output}")
                messages.append({ "role": "assistant", "content": json.dumps({ "step": "observe", "output":  output}) })
                continue

        if parsed_output.get("step") == "get_system":
            tool_name = parsed_output.get("function")
            print(f"🧠: tool_name {tool_name}")

            if avaiable_tools.get(tool_name, False) != False:
                output = avaiable_tools[tool_name].get("fn")()
                print(f"🧠: output {output}")
                messages.append({ "role": "assistant", "content": json.dumps({ "step": "observe", "output":  output}) })
                continue
        
        if parsed_output.get("step") == "output":
            print(f"🤖: {parsed_output.get("content")}")
            break