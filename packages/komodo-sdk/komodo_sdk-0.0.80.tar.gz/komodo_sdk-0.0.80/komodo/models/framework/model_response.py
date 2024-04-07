from datetime import datetime


class ModelResponse:
    model: str
    status: str
    output: None
    text: str
    has_markdown: bool
    has_quotes: bool
    is_json: bool
    run_id: str
    started: int
    completed: int

    def __init__(self, model, status, output, text, has_markdown=False, has_quotes=True, is_json=False, run_id=None):
        self.model = model
        self.status = status
        self.output = output
        self.text = text
        self.has_markdown = has_markdown
        self.has_quotes = has_quotes
        self.is_json = is_json
        self.run_id = run_id if run_id else datetime.now().strftime("%Y%m%d%H%M%S")
