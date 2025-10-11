import re

def markdown_to_telegram_html(text: str) -> str:
    # -------------------
    # 1. Headings
    # -------------------
    text = re.sub(r'###\s*(.*)', r'<b><u>\1</u></b>', text)  # H3 → bold+underline
    text = re.sub(r'##\s*(.*)', r'<b>\1</b>', text)          # H2 → bold

    # -------------------
    # 2. Bold, Italic, Strikethrough
    # -------------------
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.*?)_', r'<i>\1</i>', text)
    text = re.sub(r'~~(.*?)~~', r'<s>\1</s>', text)

    # -------------------
    # 3. Inline / Multiline code
    # -------------------
    text = re.sub(r'```(.*?)```', r'<pre>\1</pre>', text, flags=re.DOTALL)
    text = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', text)

    # -------------------
    # 4. Links
    # -------------------
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)

    # -------------------
    # 5. Lists
    # -------------------
    text = re.sub(r'^[\*\-]\s+', '• ', text, flags=re.MULTILINE)

    # -------------------
    # 6. Markdown tables → bullets
    # -------------------
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        if '|' in line:
            # skip separator line (---)
            if re.match(r'^\s*\|[-\s|]+\|\s*$', line):
                continue
            # convert row to bullet
            row = [cell.strip() for cell in line.strip('|').split('|')]
            if len(row) == 2:
                new_lines.append(f'• {row[0]}: {row[1]}')
            else:
                new_lines.append(' '.join(row))
        else:
            new_lines.append(line)
    text = '\n'.join(new_lines)

    # -------------------
    # 7. Horizontal lines
    # -------------------
    text = re.sub(r'(\-{3,}|\*{3,})', '\n', text)

    # -------------------
    # 8. Collapse multiple blank lines
    # -------------------
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()
