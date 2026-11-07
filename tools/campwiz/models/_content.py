import re
import wikitextparser as wtp

REFERENCE = re.compile("<ref.*?(?:>.*?</ref>|/>)")

MULTIPLE_NEWLINE = re.compile("\n+\s*", re.MULTILINE)

WHITESPACE = re.compile("[\t –]+")

SECTION_PATTERN = re.compile("==+.+?==+", re.MULTILINE)

SPACE_WHITESPACE = re.compile("[ \n]+")

BULLET_LIST = re.compile(r"^\s*[\*#]+", re.MULTILINE)

def _remove_reference(content: str) -> str:
    """
    This will remove the reference from the content
    """
    return REFERENCE.sub(" ", content)

def _remove_whitespace(content: str) -> str:
    """
    This will remove the whitespace from the content
    """
    content = content.strip()
    content = WHITESPACE.sub(" ", content)
    
    return content

def _replace_sections(content: str) -> str:
    """
    This will replace the sections with the section name
    """
    return SECTION_PATTERN.sub("", content)

def _preprocess(content: str) -> str:
    """
    This will:
    1. Remove the references like <ref>...</ref>, <ref name="..."/>
    2. Replace the multiple whitespace with single whitespace
    3. Remove the markup and templates
    """
    content = re.sub("[\?\*\'\"\.\,\(\)]", "", content)
    content = _remove_reference(content)
    content = _remove_whitespace(content)
    content = wtp.remove_markup(content, )#replace_tables=lambda x : '')
    content = _replace_sections(content)
    content = _remove_whitespace(content)
    content = MULTIPLE_NEWLINE.sub("\n", content)
    content = BULLET_LIST.sub("", content)
    return content

def calculate_word(content : str) -> int:
    """
    Calculate the word count of the content
    """
    content = _preprocess(content)
    count = len(SPACE_WHITESPACE.split(content))
    return count

