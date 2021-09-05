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
    # Replace some patterns
    str_html = (
        str_html.replace(pattern1, "")
        .replace(pattern2, "")
        .replace(pattern3, "")
        .replace("APPENDIX", "")
    )
    # Split the string into sentences
    sentences = str_html.split(".")
    # Remove http/https links
    sentences = [
        re.sub(r"((http|https):(\S+))", "", sentence) for sentence in sentences
    ]
    # Remove new lines
    sentences = [
        re.sub(r"\n|\r', '', '\nx\n\r\n", "", sentence) for sentence in sentences
    ]
    # Remove punctuations
    sentences = [remove_punct(sentence) for sentence in sentences]
    # Remove extra whitespace
    sentences = [" ".join(sentence.split()) for sentence in sentences]
    # Remove " " and short sentences
    sentences = [sentence for sentence in sentences if sentence or len(sentence) > 1]
    # Not sure what this does but it works
    sentences = [re.sub(r"[^\s\w+]", "", sentence) for sentence in sentences]
    return " ".join(sentences)


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
