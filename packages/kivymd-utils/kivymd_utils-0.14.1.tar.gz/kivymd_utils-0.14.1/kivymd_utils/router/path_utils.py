import re

PARAMRE = re.compile(r":(\w+)")

def patternToRe(pattern: str):
    buffer = "^"
    param_buffer = []
    start = 0
    for match in PARAMRE.finditer(pattern):
        if match.start() > start:
            buffer += re.escape(pattern[start:match.start()])
        
        name = match[1]
        param_buffer.append(name)
        regex = f"(?P<{name}>[^/]+)"
        buffer += regex
        start = match.end()
    
    if start < len(pattern):
        buffer += re.escape(pattern[start:])


    print(buffer)

    return (re.compile(buffer), param_buffer)