import base64
import hashlib
import json

# always default guid lengths to 8 for consistency and readability, can change if needed
GUID_LEN = 8


def get_guid_short(n=GUID_LEN):
    return get_guid_full()[:n]


def get_guid_full():
    import uuid
    return str(uuid.uuid4())


def get_file_digest_short(filename, n=GUID_LEN):
    return get_file_digest_full(filename)[:n]


def get_file_digest(filename):
    return get_file_digest_short(filename)


def get_file_digest_full(filename):
    try:
        with open(filename, "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        return file_hash.hexdigest()
    except FileNotFoundError:
        return None


def get_text_digest_short(text, n=GUID_LEN):
    return get_text_digest_full(text)[:n]


def get_text_digest(text):
    return get_text_digest_short(text)


def get_text_digest_full(text):
    return hashlib.md5(text.encode()).hexdigest()


def get_shortcode_with_path(shortcode, path, n=GUID_LEN):
    stem = path.stem
    hash = get_text_digest_short(str(path), n)
    return shortcode + "_" + stem + "_" + hash


def convert_to_base64(contents) -> str:
    if type(contents) is bytes:
        return base64.b64encode(contents).decode('utf-8')

    if type(contents) is dict or type(contents) is list:
        v = json.dumps(contents, default=str)
        return base64.b64encode(v.encode('utf-8')).decode('utf-8')

    return base64.b64encode(str(contents).encode('utf-8')).decode('utf-8')


def get_num_tokens(text, encoding_name: str = 'cl100k_base') -> int:
    import tiktoken
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(text))
    return num_tokens


if __name__ == "__main__":
    print(get_file_digest_short(__file__))
    print(get_text_digest_short("hello"))
    print(get_guid_short())
    print(get_guid_full())
    print(get_text_digest("hello"))
    print(get_text_digest_full("hello"))
    print(convert_to_base64("hello"))
    print(get_num_tokens("hello"))
