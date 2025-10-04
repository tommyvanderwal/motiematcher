## Command line rules 
- NOOIT python scripts maken die user input vragen. Altijd proberen alles zelf te doen als LLM.
- **No multiline command-line execution**: Never use `python -c` or `py -c` or similar for multiline Python code. Always write the code to a temporary `.py` file (e.g., `temp_script.py`), execute it with `py temp_script.py`
- For testing: Create the script in a `temp/` folder if possible, run it, and include error handling with try/except.
- NEVER run py or python with inline code that requires user input or interactive sessions. Github copilot cannot auto-approve such code.
- Never stop executing the plan just to "acknowledge" something I said. keep executing the plan, unless there is a very important question to ask me and you cannot investigate yourself.
- Always try and find the answer yourself first, in multiple ways, before asking me.
- make sure to never just start python. You always need to pass a script to it. Otherwise the interpreter will wait for user input, which stalls the entire process.
- after 50 commands without a summary, always give a summary of what you have done so far, and what the next steps are.
- the same moment after 50 commands is also a good moment to reflect if you learned anything that is useful to change in any of the .MD files and do that.
