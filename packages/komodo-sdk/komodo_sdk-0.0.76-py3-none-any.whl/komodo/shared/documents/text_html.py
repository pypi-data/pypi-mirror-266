import re

import markdown2
from bs4 import BeautifulSoup


def text_to_html(text, has_markdown=False):
    data = text
    if has_markdown:
        data = markdown2.markdown(data)
    data = text_to_html_paragraphs(data)
    data = HTML_TEMPLATE.replace('HTML_CONTENT', data)
    return data


def text_to_html_paragraphs(text):
    # First, replace multiple newlines with a single newline,
    # so you don't get empty paragraphs
    text = re.sub(r'\n\s*\n', '\n', text)

    # Split the text into lines
    lines = text.split('\n')

    # Wrap each line in a <p> tag and join them
    return ''.join(f'<p>{line.strip()}</p>\n' for line in lines)


def prettify_html_with_html5lib_bs4(html):
    soup = BeautifulSoup(html, features='html5lib')
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out
    return soup.prettify()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Generated Content</title>
<style>
body {
    font-family: Arial, sans-serif;
    font-size: 14px;
    line-height: 1.5;
    color: #333333;
    background-color: #FFFFFF;
}
h1 { font-size: 24px; font-weight: bold; }
h2 { font-size: 20px; font-weight: bold; }
p { margin: 10px 0; }
a { color: #0066CC; }
a:hover { color: #0099FF; }
ul { list-style-type: disc; padding-left: 20px; }
table { border: 1px solid #DDDDDD; }
th { background-color: #F3F3F3; font-weight: bold; }
td { padding: 8px; }
.btn {
    background-color: #0044CC;
    color: #FFFFFF;
    padding: 10px 15px;
    text-align: center;
    border-radius: 4px;
    display: inline-block;
    text-decoration: none;
}
.btn:hover {
    background-color: #0066FF;
}
img { max-width: 100%; height: auto; }
@media only screen and (max-width: 600px) {
    /* Responsive adjustments */
}
</style>
</head>
<body>
HTML_CONTENT
</body>
</html>
"""
