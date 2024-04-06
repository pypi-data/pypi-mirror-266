import re


def with_tag(message, tag="debug"):
    return f"<{tag}>{message}</{tag}>" if message else ""


def remove_tag(input_string, tag="debug"):
    # Define regex pattern to match <debug>...</debug> content
    pattern = rf'<{tag}>.*?</{tag}>'
    # Use re.sub to replace matched patterns with an empty string
    output_string = re.sub(pattern, '', input_string)
    output_string = ' '.join(output_string.split())
    return output_string


def remove_triple_quotes(input_string, tag="debug"):
    # Define regex pattern to match <debug>...</debug> content
    pattern = rf'```{tag}.*?```'
    # Use re.sub to replace matched patterns with an empty string
    output_string = re.sub(pattern, '', input_string)
    output_string = ' '.join(output_string.split())
    return output_string


def remove_triple_quotes(input_string, tag="debug"):
    # Define the length of the opening and closing triple quotes
    opening_len = len(f'```{tag}')
    closing_len = 3

    output_string = ""
    inside_quotes = False
    buffer = ""

    # Iterate over each character in the input string
    i = 0
    while i < len(input_string):
        # Check if the current position matches the opening triple quotes
        if input_string[i:i + opening_len] == f'```{tag}':
            inside_quotes = True
            i += opening_len
            continue
        # Check if the current position matches the closing triple quotes
        elif input_string[i:i + closing_len] == '```':
            inside_quotes = False
            buffer = ""  # Reset buffer when exiting triple quotes
            i += closing_len
            continue

        # If not inside triple quotes, append characters to output_string
        if not inside_quotes:
            output_string += input_string[i]
        # If inside triple quotes, append characters to buffer
        else:
            buffer += input_string[i]

        i += 1

    # Return the output string
    return output_string.strip()


if __name__ == "__main__":
    # Test the add_tags function
    message = "This is a test message"
    tagged_message = with_tag(message)
    print(tagged_message)

    # Test the remove_tags function
    input_string = "This is a <debug>debug</debug> string with <debug>some debug content</debug>."
    output_string = remove_tag(input_string)
    print(output_string)

    # Test the remove_quotes function
    input_string = "This is a ```debug string``` with ```debugsome debug content```."
    output_string = remove_triple_quotes(input_string)
    print(output_string)
