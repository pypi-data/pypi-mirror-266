import yaml

from komodo.framework.komodo_context import KomodoContext
from komodo.shared.documents.text_extract import extract_text_from_path
from komodo.shared.utils.term_colors import print_error


def load_contents(file) -> str:
    return extract_text_from_path(file)


def load_context_from_yaml(file) -> KomodoContext:
    loaded = yaml.safe_load(file.read_text()) or {}
    if 'context' not in loaded:
        print_error(f"No context found. Skipping: {file}.")
        return KomodoContext()

    items = loaded['context']
    if not isinstance(items, list):
        raise ValueError(f"Context must be a list in file: {file}, but got {type(items)}")

    context = KomodoContext()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"Context items must be a dict in file: {file}, but got {type(item)}")

        if 'tag' not in item:
            raise ValueError(f"Context item must have a tag in file: {file}, but got {item}")

        if 'content' not in item:
            raise ValueError(f"Context item must have a content in file: {file}, but got {item}")

        tag = item['tag']
        content = item['content']
        context.add(tag, content)

    return context


def load_dictionary_from_yaml(file) -> dict:
    dictionary = yaml.safe_load(file.read_text()) or {}
    if not isinstance(dictionary, dict):
        raise ValueError(f"Dictionary must be a dict in file: {file}, but got {type(dictionary)}")

    return dictionary
