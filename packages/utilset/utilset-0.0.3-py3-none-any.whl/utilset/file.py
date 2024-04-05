def get_content_line(filepath) -> str:
    with open(filepath, mode="r") as file:
        return file.readline().strip()

def save_content(filepath, content):
    with open(filepath, mode="w") as file:
        file.write(str(content))