import subprocess
import sys
import os
import platform

def execute_command(command, log_file):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        log_file.write(f"Command: {command}\n")
        if result.stdout:
            log_file.write(f"Output: {result.stdout}\n")
        if result.stderr:
            log_file.write(f"Error: {result.stderr}\n")
        log_file.write("-" * 40 + "\n")
    except Exception as e:
        log_file.write(f"Failed to execute command: {command}\n")
        log_file.write(f"Error: {str(e)}\n")
        log_file.write("-" * 40 + "\n")

def main(input_file, log_file_path):
    with open(input_file, 'r') as file:
        commands = file.readlines()

    with open(log_file_path, 'w') as log_file:
        for command in commands:
            command = command.strip()
            if command:
                execute_command(command, log_file)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python execute_commands.py <input_file> <log_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    log_file_path = sys.argv[2]

    main(input_file, log_file_path)