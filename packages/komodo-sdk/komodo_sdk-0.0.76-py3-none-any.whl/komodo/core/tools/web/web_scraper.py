import time
from urllib.request import urlopen, Request

from requests import HTTPError

from komodo.framework.komodo_tool import KomodoTool
from komodo.shared.documents.text_extract import extract_text_from_html_bs4, remove_extra_space
from komodo.shared.documents.text_html import prettify_html_with_html5lib_bs4
from komodo.shared.utils.sentry_utils import sentry_trace


class WebScraper(KomodoTool):
    name = "Web Scraper"
    purpose = "Extracts, returns, and optionally summarizes the text or raw HTML of a specified webpage."
    shortcode = "komodo_web_content_extractor"

    definition = {
        "type": "function",
        "function": {
            "name": shortcode,
            "description": purpose,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string",
                            "description": "The URL of the webpage to be scraped."},
                    "raw_html": {"type": "boolean",
                                 "description": "When set to true, returns the raw HTML of the page; otherwise, returns the text."},
                    "max_length": {"type": "integer",
                                   "description": "Defines the maximum length of the text in words to be returned. Defaults to 1000."},
                },
                "required": ["url"]
            }
        }
    }

    def __init__(self):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition,
                         action=self.action)

    @sentry_trace
    def action(self, args):
        attempts = 0
        url = args['url']
        raw = args['raw_html'] if 'raw_html' in args else False

        # UA2 hangs on some sites
        UA1 = 'PostmanRuntime/7.6.0'
        UA2 = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'

        while attempts < 3:
            try:
                req = Request(url)
                req.add_header('user-agent', UA1)

                rawpage = urlopen(req, timeout=30).read()
                html = rawpage.decode('utf-8')
                if raw:
                    text = prettify_html_with_html5lib_bs4(html)
                else:
                    text = extract_text_from_html_bs4(html)

                return remove_extra_space(text)

            except HTTPError as e:
                if e.response.status_code == 429 or e.response.status_code == 502:
                    print("Attempt# " + str(attempts) + " Error: " + str(e))
                    print("Rate limit exceeded. Waiting for 5 seconds...")
                    time.sleep(5)
                    attempts += 1

            except Exception as e:
                print("Error: " + str(e))
                return "Could not retrieve web page. Encountered error: " + str(e)

        return "Could not scrape web page after multiple attempts: " + url
