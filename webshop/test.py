import re 
def idx_parser(text):
    pattern = r"\d\s\w*"  # Matches a word boundary, followed by a digit, and then any word characters

    match = re.search(pattern, text)
    if match:
        return int(match.group(0))
    else:
        return None
    
text = "5\n\nAction: Buy Now"
idx = idx_parser(text)
print(idx)