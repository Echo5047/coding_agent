# N-Queens Agent Homework

This directory contains the coding-agent part of the homework. Your job is to complete the missing logic in `deepseek_n_queens_agent.py`. After that, run your agent and let it autonomously inspect, edit, and test the N-Queens files under `n_queens/`.

## What you should do

1. Read `deepseek_n_queens_agent.py`.
2. Complete the TODO sections in the agent scaffold.
3. Set your DeepSeek API key in the shell.
4. Run `deepseek_n_queens_agent.py`.
5. Let the agent use its tools to inspect and complete:
   - `n_queens/backtracking.py`
   - `n_queens/local_search.py`
6. Keep the terminal log showing that the agent read files, edited code, ran the scripts, and reached successful outputs.

## Files

- `deepseek_n_queens_agent.py`: the main scaffold you need to complete.
- `n_queens/backtracking.py`: backtracking version of N-Queens.
- `n_queens/local_search.py`: local-search version of N-Queens.
- `requirements.txt`: Python dependencies for the agent script.

## Agent behavior

The agent is designed to:

1. send a system prompt and user task to the model,
2. parse model outputs of the form `tool: NAME({...})`,
3. execute the requested tool,
4. append `tool_result(...)` back into the conversation,
5. continue until the task is finished.

The available tools are:

- `list_files`
- `read_file`
- `edit_file`
- `run_bash`

## Install dependencies

From this directory, install the required packages:

```bash
pip install -r requirements.txt
```

## Set the DeepSeek API key

You must set `DEEPSEEK_API_KEY` before running the agent.

```bash
export DEEPSEEK_API_KEY="your_api_key_here"
```

在`deepseek_n_queens_agent.py`中，我们更改了`base_url`为本课程的服务器地址，请大家控制请求量不要过大。大家可以通过`python check_usage.py`来查看自己的API用量。如果用量不足请联系助教。
请大家检查`python check_usage.py`中返回的student ID是否和自己学号相符，如果有问题请联系助教

## Run the scaffold

After setting the API key, run:

```bash
python deepseek_n_queens_agent.py
```

Once your code is complete, the agent should be able to inspect `n_queens/`, edit the homework files, and run bounded test commands.

Your submitted report should include a terminal log or screenshot showing the completed agent using tools to finish and run the N-Queens task.
