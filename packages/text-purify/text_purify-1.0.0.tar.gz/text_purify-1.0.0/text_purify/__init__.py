import re


def remove_special_characters(text):
    return re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)


def remove_html_tags(text):
    return re.sub(r'<.*?>', '', text)


def remove_double_spaces(text):
    return re.sub(r'\s+', ' ', text).strip()
