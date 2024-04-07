import subprocess

def run_command(command, premessage="", postmessage=""):
    # run the command
    result = subprocess.run(command, 
                            shell=True, 
                            capture_output=True, 
                            text=True)   
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(result.stderr)
        print("Failed to execute command. Exiting...")
        return False


