import pandas as pd
from pprint import pprint
from bs4 import BeautifulSoup


def read_tei(tei_file):
    try:
        with open(tei_file, "r") as tei:
            soup = BeautifulSoup(tei, "lxml")
            return soup
    except:
        raise RuntimeError("Cannot generate a soup from the input")


def extract_div_and_p_tags(soup):
    body = soup.find("body")
    results = []
    for div in body.find_all("div"):
        print(div)
        para = div.find_all("p")
        if para:
            div_text = div.get_text()
            para_text = [text.get_text(separator=" ") for text in para]
            results.append({"div": div_text, "p": para_text})
    return results


if __name__ == "__main__":
    tei_doc = "/Users/yravindranath/Downloads/IOI_2020_SR.pdf.tei.xml"
    soup = read_tei(tei_file=tei_doc)
    results = extract_div_and_p_tags(soup=soup)
    # df = pd.DataFrame.from_dict(results)
    # df.to_csv("./IOI_2020_SR.csv")
