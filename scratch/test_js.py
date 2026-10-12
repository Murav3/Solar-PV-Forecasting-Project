import re

with open("frontend/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find scripts
scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"Total script blocks found: {len(scripts)}")

main_script = ""
for idx, s in enumerate(scripts):
    if len(s.strip()) > 100:
        print(f"Script #{idx+1} length: {len(s)} chars")
        main_script = s

# Check basic brackets matching in main_script
stack = []
open_brackets = {'{': '}', '[': ']', '(': ')'}
close_brackets = {'}': '{', ']': '[', ')': '('}

in_string = False
string_char = ''
in_comment_single = False
in_comment_multi = False
escape = False

line_num = 1
col_num = 0

for i, char in enumerate(main_script):
    if char == '\n':
        line_num += 1
        col_num = 0
        in_comment_single = False
        continue
    col_num += 1

    if in_comment_single:
        continue

    if in_comment_multi:
        if char == '/' and i > 0 and main_script[i-1] == '*':
            in_comment_multi = False
        continue

    if in_string:
        if escape:
            escape = False
        elif char == '\\':
            escape = True
        elif char == string_char:
            in_string = False
        continue

    if char in ('"', "'", '`'):
        in_string = True
        string_char = char
        continue

    if char == '/' and i + 1 < len(main_script):
        nxt = main_script[i+1]
        if nxt == '/':
            in_comment_single = True
            continue
        elif nxt == '*':
            in_comment_multi = True
            continue

    if char in open_brackets:
        stack.append((char, line_num, col_num))
    elif char in close_brackets:
        if not stack:
            print(f"Unmatched closing bracket '{char}' at line {line_num}, col {col_num}")
            break
        last, l_line, l_col = stack.pop()
        if close_brackets[char] != last:
            print(f"Mismatched bracket: expected '{open_brackets[last]}' for '{last}' at line {l_line}, but got '{char}' at line {line_num}, col {col_num}")
            break

if stack:
    last, l_line, l_col = stack[-1]
    print(f"Unclosed '{last}' from line {l_line}, col {l_col}. Remaining unclosed count: {len(stack)}")
else:
    print("All brackets, parentheses, and braces are perfectly balanced!")
