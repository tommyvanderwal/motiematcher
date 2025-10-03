import os
import sys
from pathlib import Path

print("Current working directory:", os.getcwd())
print("Python executable:", sys.executable)
print("Python path:", sys.path[:3])

# Test different path approaches
test_paths = [
    "bronmateriaal-onbewerkt",
    "./bronmateriaal-onbewerkt",
    "C:\\motiematcher\\bronnateriaal-onbewerkt",
    Path("bronnateriaal-onbewerkt"),
    Path("./bronnateriaal-onbewerkt"),
    Path("C:\\motiematcher\\bronnateriaal-onbewerkt")
]

for path in test_paths:
    exists = os.path.exists(path) if isinstance(path, str) else path.exists()
    print(f"Path '{path}' exists: {exists}")

# Try to list directory contents
try:
    contents = os.listdir("bronnateriaal-onbewerkt")
    print(f"Directory contents: {contents[:5]}...")
except Exception as e:
    print(f"Error listing directory: {e}")

# Try absolute path
abs_path = os.path.abspath("bronnateriaal-onbewerkt")
print(f"Absolute path: {abs_path}")
print(f"Absolute path exists: {os.path.exists(abs_path)}")