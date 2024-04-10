from enum import Enum

from komodo.shared.documents.text_extract import to_clean_text, extract_text_from_path
from komodo.shared.documents.text_html import text_to_html


class TextConvertHelper():
    class Format(Enum):
        TEXT = "text"
        HTML = "html"
        PDF = "pdf"
        MARKDOWN = "markdown"

    def __init__(self, contents, input_format):
        self.contents = contents
        self.input_format = self.Format(input_format)

    def convert_to(self, output_format):
        output_format = self.Format(output_format) if isinstance(output_format, str) else output_format

        result = None
        if self.input_format == output_format:
            result = self.contents

        if self.input_format == self.Format.TEXT:
            if output_format == self.Format.PDF:
                result = convert_text_to_pdf(self.contents)
            if output_format == self.Format.HTML:
                result = convert_text_to_html(self.contents)
            if output_format == self.Format.MARKDOWN:
                result = convert_text_to_markdown(self.contents)

        if self.input_format == self.Format.MARKDOWN:
            if output_format == self.Format.TEXT:
                result = convert_markdown_to_text(self.contents)
            if output_format == self.Format.HTML:
                result = convert_markdown_to_html(self.contents)
            if output_format == self.Format.PDF:
                result = convert_markdown_to_pdf(self.contents)

        if self.input_format == self.Format.HTML:
            if output_format == self.Format.TEXT:
                result = convert_html_to_text(self.contents)
            if output_format == self.Format.MARKDOWN:
                result = convert_html_to_markdown(self.contents)
            if output_format == self.Format.PDF:
                result = convert_html_to_pdf(self.contents)

        if self.input_format == self.Format.PDF:
            if output_format == self.Format.TEXT:
                result = convert_pdf_to_text(self.contents)
            if output_format == self.Format.HTML:
                result = convert_pdf_to_html(self.contents)
            if output_format == self.Format.MARKDOWN:
                result = convert_pdf_to_markdown(self.contents)

        if result:
            return result, self.extension(output_format), self.mode(output_format)

        raise Exception(f"Conversion from {self.input_format} to {output_format} is not supported.")

    def extension(self, format):
        format = self.Format(format) if isinstance(format, str) else format
        if format == self.Format.TEXT:
            return ".txt"
        if format == self.Format.HTML:
            return ".html"
        if format == self.Format.PDF:
            return ".pdf"
        if format == self.Format.MARKDOWN:
            return ".md"
        raise Exception(f"Unsupported format: {format}")

    def mode(self, format):
        format = self.Format(format) if isinstance(format, str) else format
        if format == self.Format.TEXT:
            return "w"
        if format == self.Format.HTML:
            return "w"
        if format == self.Format.PDF:
            return "wb"
        if format == self.Format.MARKDOWN:
            return "w"
        raise Exception(f"Unsupported format: {format}")


## https://gist.github.com/engineervix/2385a54a4019b3f4526e

DEFAULT_EXTRAS = [
    'fenced-code-blocks',
    'footnotes',
    'metadata',
    'cuddled-lists',
    'pyshell',
    'smarty-pants',
    'spoiler',
    'tables'
]
PDF_OPTIONS = {
    'page-size': 'A4',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8"
    # 'no-outline': None
}


def convert_text_to_markdown(text):
    return text


def convert_text_to_html(text):
    return text_to_html(text, has_markdown=False)


def convert_text_to_pdf(text):
    return convert_html_to_pdf(convert_text_to_html(text))


def convert_markdown_to_text(text):
    html = text_to_html(text, has_markdown=True)
    return convert_html_to_text(html)


def convert_markdown_to_html(text):
    return text_to_html(text, has_markdown=True)


def convert_markdown_to_pdf(text):
    return convert_html_to_pdf(convert_markdown_to_html(text))


def convert_html_to_pdf(html):
    import pdfkit
    return pdfkit.from_string(html, options=PDF_OPTIONS)


def convert_html_to_text(html):
    from bs4 import BeautifulSoup
    return to_clean_text(''.join(BeautifulSoup(html, 'html.parser').findAll(text=True)))


def convert_html_to_markdown(html):
    raise Exception("Not implemented")


def convert_pdf_to_text(pdf):
    return extract_text_from_path(pdf)


def convert_pdf_to_html(pdf):
    raise Exception("Not implemented")


def convert_pdf_to_markdown(pdf):
    raise Exception("Not implemented")


if __name__ == "__main__":
    print(convert_text_to_pdf("foo bar"))
    print(convert_markdown_to_html("## Foo\n### Bar"))
    print(convert_markdown_to_text("## Foo\n### Bar"))
    print(convert_markdown_to_pdf("## Foo\n### Bar"))
    print(convert_html_to_text("<h1>Foo</h1><h2>Bar</h2>"))
    print(convert_html_to_pdf("<h1>Foo</h1><h2>Bar</h2>"))

    helper = TextConvertHelper(contents="## Foo\n### Bar", input_format="markdown")
    print(helper.convert_to("html"))
    print(helper.convert_to("text"))
    print(helper.convert_to("pdf"))
    print(helper.convert_to("markdown"))
    print(helper.extension("pdf"))
    print(helper.mode("pdf"))
    print(helper.extension("html"))
    print(helper.mode("html"))
    print(helper.extension("text"))
    print(helper.mode("text"))
    print(helper.extension("markdown"))
    print(helper.mode("markdown"))
