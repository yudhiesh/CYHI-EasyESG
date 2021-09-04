from bs4 import BeautifulSoup
import re
import string


def extract_text_lxml(response_text):
    data = BeautifulSoup(response_text, features="lxml")
    text = data.find_all(text=True)
    return text


def process_text(all_text):
    visible_html = " ".join([display_visible_html_using_re(t) for t in all_text])
    str_html = " ".join(visible_html.split())
    pattern1 = 'xml version="1.0"'
    pattern2 = 'encoding="UTF-8"?'
    pattern3 = "GROBID - A machine learning software for extracting information from scholarly documents"
    str_html = (
        str_html.replace(pattern1, "").replace(pattern2, "").replace(pattern3, "")
    )
    str_html = re.sub(r"((http|https):(\S+))", "", str_html)
    str_html = re.sub(r"(RT\s(@\w+))", "", str_html)
    str_html = re.sub(r"[!#?:*%$]", "", str_html)
    str_html = re.sub(r"[^\s\w+]", "", str_html)
    str_html = re.sub(r"[\n]", "", str_html)
    str_html = re.sub(r"[A-Z]+(?![a-z])", "", str_html)
    str_html = remove_punct(str_html)
    str_html = " ".join(str_html.split())
    return str_html


def remove_punct(text):
    text = "".join([char for char in text if char not in string.punctuation])
    text = re.sub("[0-9]+", "", text)
    return text


def display_visible_html_using_re(text):
    return re.sub("(\<.*?\>)", "", text)


def read_tei(tei_file):
    try:
        with open(tei_file, "r") as tei:
            soup = BeautifulSoup(tei, "lxml")
            return soup
    except:
        raise RuntimeError("Cannot generate a soup from the input")
