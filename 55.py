# Prompt 55

import re
import markdown
from bs4 import BeautifulSoup

def sanitize_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    for script in soup(["script", "iframe"]):
        script.decompose()

    for a in soup.find_all("a", href=True):
        if not re.match(r"^https?://", a["href"]):
            a.decompose()

    return str(soup)

def markdown_to_safe_html(markdown_content):
    html_content = markdown.markdown(markdown_content)
    safe_html = sanitize_html(html_content)
    return safe_html

if __name__ == "__main__":
    user_markdown = """
    # Sample Markdown

    This is a sample Markdown content.

    - Item 1
    - Item 2

    [Click me](http://example.com)

    <script>alert("Malicious script");</script>
    <iframe src="http://malicious.com"></iframe>
    """

    safe_html = markdown_to_safe_html(user_markdown)
    print(safe_html)