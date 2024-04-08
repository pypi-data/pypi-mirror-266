import json
import re
import tempfile
from pathlib import Path

import html2text
import magic
import textract
from bs4 import BeautifulSoup, Comment, NavigableString
from ftfy import ftfy
from unidecode import unidecode
from urlextract import URLExtract


def extract_text_from_path(path):
    path = str(path) if isinstance(path, Path) else path
    m = magic.from_file(path, mime=True)
    print(f"Extracting text from {path} (mime: {m})")

    if m.startswith('inode/empty') or m.startswith('inode/x-empty'):
        return ""
    elif m.startswith('text/html'):
        return extract_text_from_html_path(path)
    elif m.startswith('text'):
        return extract_text_from_text_path(path)
    elif m.startswith('application/pdf') or path.endswith('.pdf'):
        return extract_text_from_pdf(path)
    elif path.endswith('.docx'):
        return extract_text_from_docx(path)
    elif path.endswith('.pptx'):
        return extract_text_from_pptx(path)
    elif path.endswith('.xlsx'):
        return extract_text_from_xlsx(path)
    elif path.endswith('.doc'):
        return extract_text_from_doc(path)
    elif path.endswith('.xls'):
        return extract_text_from_xls(path)
    else:
        print(f"File type is not supported: {m}")
        return ""


def extract_text_from_content(path, payload, content_type):
    if content_type == 'text/html':
        html = payload.decode().strip()
        text = extract_text_from_html_bs4(html)
        return to_clean_text(text)
    else:
        return extract_text_from_pdf(path)


def extract_text_from_html_path(path):
    with open(path, 'rb') as file:
        payload = file.read()
        html = payload.decode().strip()
        text = extract_text_from_html_bs4(html)
        return to_clean_text(text)


def extract_text_from_text_path(path):
    import chardet
    with open(path, 'rb') as file:
        raw_data = file.read()

    # Detect the encoding
    result = chardet.detect(raw_data)
    encoding = result['encoding']

    # Now that you know the encoding, you can decode the content
    with open(path, 'rb') as file:
        content = file.read().decode(encoding).strip()

    print(f"Detected encoding: {encoding}")
    return content


def extract_text_from_pdf(path):
    try:
        return extract_text_from_pdf_textract(path)
    except Exception as e:
        print("Error extracting text using textract: ", e, " (trying pypdf instead)")
        return extract_text_from_pdf_pypdf(path)


def extract_text_from_pdf_textract(path):
    text = textract.process(path).decode().strip()
    return text


def extract_text_from_pdf_pypdf(path):
    import pypdf
    pdf = pypdf.PdfReader(open(path, 'rb'))
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text


def extract_text_from_docx(path):
    text = textract.process(path).decode().strip()
    return text


def extract_text_from_pptx(path):
    text = textract.process(path).decode().strip()
    return text


def extract_text_from_xlsx(path):
    return ""


def extract_text_from_doc(path):
    return ""


def extract_text_from_xls(path):
    return ""


def extract_urls(text):
    extractor = URLExtract(cache_dir=tempfile.gettempdir())
    return list(filter(lambda x: x.startswith('http'), list(set(extractor.find_urls(text)))))


def extract_urls_from_pdf(path):
    import PyPDF2
    PDFFile = open(path, 'rb')

    PDF = PyPDF2.PdfReader(PDFFile)
    pages = len(PDF.pages)
    key = '/Annots'
    uri = '/URI'
    ank = '/A'

    urls = []

    for page in range(pages):
        # print("Current Page: {}".format(page))
        pageSliced = PDF.pages[page]
        pageObject = pageSliced.get_object()
        if key in pageObject.keys():
            ann = pageObject[key]
            for a in ann:
                u = a.get_object()
                if uri in u[ank].keys():
                    # print(u[ank][uri])
                    urls.append(u[ank][uri])

    return urls


def extract_text_from_html(html):
    return html2text.html2text(html).strip()


def extract_text_from_html_bs4(html):
    soup = BeautifulSoup(html, 'html.parser')
    # append the text to the link
    for a in soup.select('a[href]'):
        a.contents.append(soup.new_string(' ({})'.format(a['href'])))

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    # unwrap() all tags
    for tag in soup.select('*'):
        tag.unwrap()

    return soup.text.strip()


def extract_text_from_html5lib_bs4(html):
    soup = BeautifulSoup(html, features='html5lib')
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    text = soup.get_text("\n")
    return "".join([s for s in text.strip().splitlines(True) if s.strip()])


def is_tag_empty(tag):
    if isinstance(tag, Comment):
        return True  # Consider comments as "

    if isinstance(tag, NavigableString):
        return not tag.strip()

    text = tag.get_text(strip=True)

    if not text:
        for child in tag.children:
            if isinstance(child, NavigableString) and child.strip():
                return False
            if not is_tag_empty(child):
                return False
        return True
    return False


def remove_empty_tags(soup):
    for tag in soup.find_all():
        if is_tag_empty(tag):
            tag.decompose()


def extract_text_from_html_bs4_1(html):
    soup = BeautifulSoup(html, 'html.parser')
    # append the text to the link
    for a in soup.select('a[href]'):
        a.contents.append(soup.new_string(' ({})'.format(a['href'])))

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    for tag in soup.find_all(True):
        tag.attrs = {}

    tags_to_remove = ['script', 'style', 'meta', 'link', 'nav', 'header', 'footer', 'form', 'input', 'button', 'iframe',
                      'noscript', 'aside']

    for tag_name in tags_to_remove:
        for tag in soup.find_all(tag_name):
            tag.decompose()  # Or tag.extract() to remove the tag and its content completely

    for span in soup.find_all('span'):
        span.unwrap()

    remove_empty_tags(soup)

    pretty_html = soup.prettify()

    return " ".join(remove_extra_space(pretty_html).split('\n'))


def remove_extra_space(text):
    # First, replace multiple newlines with a single newline,
    # so you don't get empty paragraphs
    text = re.sub(r'\n\s*\n', '\n', text)

    # Split the text into lines
    lines = text.split('\n')

    # Wrap each line in a <p> tag and join them
    return '\n'.join(line.strip() for line in lines)


def replace_quoted_printable(text):
    try:
        import quopri
        decoded_text = quopri.decodestring(text).decode('utf-8')
        return unidecode(decoded_text)
    except ValueError as e:
        print("Warning: could not decode quoted printable text (not a big issue): ", e)
        return text


def to_clean_text(payload):
    if payload is None:
        return ''
    if isinstance(payload, bytes):
        payload = payload.decode('ascii', 'ignore')
    else:
        payload = payload.encode('ascii', 'ignore').decode('ascii', 'ignore')
    return replace_quoted_printable(remove_extra_space(ftfy(payload)))


def extract_text_between_ticks(text, tick='```', tag='json'):
    # Regular expression pattern to match text between ```json and ```
    pattern = rf'{tick}{tag}(.*?){tick}'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        json_str = match.group(1).strip()  # Strip to remove any leading/trailing whitespace
        return to_clean_text(json_str)
    else:
        return to_clean_text(text)


def extract_json(text, tick='```'):
    text = extract_text_between_ticks(text, tick=tick, tag='json')
    if text is not None:
        try:
            text = json.dumps(json.loads(text))
        except:
            pass
    return to_clean_text(text)


if __name__ == '__main__':
    text = '''
    ```json
    {
      "personal_info": {
        "name": "JEFFREY S. LEVIN", 
        "address": "607 Sunnyhill Terrace\nRiver Vale, NJ 07675",
        "phone": "201.446.6158",
        "email": "jeffreylevin98@yahoo.com",
        "years_of_experience": null,
        "gender": null
      }
    }
    ```
    stuff here
    '''

    extracted_json = extract_text_between_ticks(text, tag='json')
    if extracted_json is not None:
        print(json.loads(json.dumps(extracted_json, indent=4, separators=(',', ': '))))
