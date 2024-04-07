import os
from pathlib import Path

def generate_object(directory, objectname, type):
    object = Path(directory, objectname)

    if object.exists():
        print("{} already exists..".format(objectname))
        return False
    
    print("Creating {}..".format(objectname))

    if type=="file":
        with open(object, "w") as f:
            f.write("")
    elif type=="folder":
        object.mkdir()

    return True


def update_file_content(file_path, content):

    file = Path(file_path)
    with open(file, 'w') as writer:
        writer.write(content)

    