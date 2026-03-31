# Prompt 96

import markdown
from markdown.extensions.toc import TocExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from weasyprint import HTML

# Convert Markdown to HTML with extensions
def markdown_to_html(md_content):
    extensions = [
        TocExtension(permalink=True),
        CodeHiliteExtension(),
        ExtraExtension()
    ]
    html_content = markdown.markdown(md_content, extensions=extensions)
    return html_content

# Convert HTML to PDF
def html_to_pdf(html_content, output_pdf):
    html = HTML(string=html_content)
    html.write_pdf(output_pdf)

# Read Markdown file
def read_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        md_content = file.read()
    return md_content

# Main function
def main():
    md_file_path = 'documentation.md'
    output_pdf_path = 'documentation.pdf'

    md_content = read_markdown_file(md_file_path)
    html_content = markdown_to_html(md_content)
    html_to_pdf(html_content, output_pdf_path)

    print(f"PDF generated successfully: {output_pdf_path}")

if __name__ == "__main__":
    main()