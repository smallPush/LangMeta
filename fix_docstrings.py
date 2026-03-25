import glob
import re

files = glob.glob("tests/test_*.py")

for filepath in files:
    with open(filepath, "r") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if line contains a def
        is_def = False
        stripped = line.strip()
        if stripped.startswith("def ") or stripped.startswith("async def "):
            is_def = True

        if is_def:
            # Accumulate until we hit a colon
            def_block = [line]
            j = i + 1
            while j < len(lines) and not def_block[-1].strip().endswith(":"):
                def_block.append(lines[j])
                j += 1

            new_lines.extend(def_block)

            if j < len(lines):
                next_line = lines[j]
                if '"""' not in next_line and "'''" not in next_line:
                    # Calculate indent based on the 'def' line
                    base_indent = len(line) - len(line.lstrip())
                    indent = " " * (base_indent + 4)
                    new_lines.append(f'{indent}"""Test function docstring."""\n')

            i = j - 1 # Next iteration will be i+1 which is j
        else:
            new_lines.append(line)

        i += 1

    with open(filepath, "w") as f:
        f.writelines(new_lines)
