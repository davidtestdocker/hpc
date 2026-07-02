import subprocess

result = subprocess.run(
    ["ps", "-eo", "pid,comm"],
    capture_output=True,
    text=True
)

print(result.stdout)
