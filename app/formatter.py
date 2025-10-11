import re

def markdown_to_telegram_html(text: str) -> str:
    # Convert bold (**text**)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # Convert italic (*text* or _text_)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.*?)_', r'<i>\1</i>', text)
    
    # Convert strikethrough (~~text~~)
    text = re.sub(r'~~(.*?)~~', r'<s>\1</s>', text)
    
    # Convert inline code (`code`)
    text = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', text)
    
    # Convert multiline code blocks (```code```)
    text = re.sub(r'```(.*?)```', r'<pre>\1</pre>', text, flags=re.DOTALL)
    
    # Convert markdown-style links [text](url)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    
    # Replace list markers (- or *) with bullet points
    text = re.sub(r'^[\*\-]\s+', '• ', text, flags=re.MULTILINE)
    
    # Replace --- or *** with a line break (Telegram doesn’t support horizontal lines)
    text = re.sub(r'(\-{3,}|\*{3,})', '\n', text)
    
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


# 🧪 Example
sample = """
**Air India CSR Strategy**
---
* Focus on aviation safety
* Support families of victims
* Strengthen mental health support
[Learn more](https://airindia.com)
"""

converted = markdown_to_telegram_html(sample)
print(converted)
