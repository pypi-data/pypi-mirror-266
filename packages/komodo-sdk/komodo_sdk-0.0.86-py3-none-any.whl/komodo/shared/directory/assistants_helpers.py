from os import path

EMPTY_FOOTER = ""
BASIC_FOOTER = """
<br><br>
<i>Response prepared for SENDER by AGENT (Powered by Komodo AI).</i>
<br><br>
"""

WHITE_LABEL_FOOTER = """
<br><br>
<i>Response prepared for SENDER by AGENT.</i>
<br><br>
"""

FOOTER_WITH_MODEL = """
<br><br>
<i>Response prepared for SENDER by AGENT (Powered by Komodo AI, MODEL).</i>
<br><br>
"""

FOOTER_WITH_INSTRUCTIONS = """
<br><br>
Model Instructions: 
INSTRUCTIONS
<br><br>
Actions: ACTIONS
<br><br>
<i>Response prepared for SENDER by AGENT (Powered by Komodo AI).</i>
<br><br>
"""


def instructions(script_path, filename):
    basepath = path.dirname(script_path)
    filepath = path.abspath(path.join(basepath, filename))
    return open(filepath, "r").read()
