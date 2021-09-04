from bs4 import BeautifulSoup
import streamlit as st
import os
import requests
import re
import string

import docx2txt
from PIL import Image
from PyPDF2 import PdfFileReader
import pdfplumber


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


def read_pdf(file):
    pdfReader = PdfFileReader(file)
    count = pdfReader.numPages
    all_page_text = ""
    for i in range(count):
        page = pdfReader.getPage(i)
        all_page_text += page.extractText()

    return all_page_text


def read_pdf_with_pdfplumber(file):
    with pdfplumber.open(file) as pdf:
        page = pdf.pages[0]
        return page.extract_text()


@st.cache
def load_image(image_file):
    img = Image.open(image_file)
    return img


def main():
    st.title("EasyESG")

    menu = ["PDF"]
    choice = st.sidebar.selectbox("Menu", menu)
    if choice == "PDF":
        st.subheader("PDF")
        docx_file = st.file_uploader("Upload File", type=["txt", "docx", "pdf"])
        if st.button("Process"):
            if docx_file:
                file_details = {
                    "Filename": docx_file.name,
                    "FileType": docx_file.type,
                    "FileSize": f"{round(docx_file.size / 1e6,2)}Mb",
                }
                st.write(file_details)
                # Check File Type
                if docx_file.type == "text/plain":
                    # raw_text = docx_file.read() # read as bytes
                    # st.write(raw_text)
                    # st.text(raw_text) # fails
                    st.text(str(docx_file.read(), "utf-8"))  # empty
                    raw_text = str(
                        docx_file.read(), "utf-8"
                    )  # works with st.text and st.write,used for futher processing
                    # st.text(raw_text) # Works
                    st.write(raw_text)  # works
                elif docx_file.type == "application/pdf":
                    # raw_text = read_pdf(docx_file)
                    # st.write(raw_text)
                    with st.spinner("Processing..."):
                        try:
                            pdf_path = os.path.abspath(docx_file.name)
                            GROBID_URL = (
                                "http://localhost:8070/api/processFulltextDocument"
                            )
                            response = requests.post(
                                GROBID_URL,
                                files={"input": open(pdf_path, "rb")},
                            )

                            if response.status_code == 200:
                                st.success("File process successful")
                                response_text = response.text
                                all_text = extract_text_lxml(
                                    response_text=response_text
                                )
                                str_html = process_text(all_text=all_text)
                                print(str_html)
                                st.text(str_html)

                            else:
                                st.error("Error processing file!")

                        except Exception as e:
                            print(f"{e!r}")
                            st.error("Error processing file!")

                elif (
                    docx_file.type
                    == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ):
                    # Use the right file processor ( Docx,Docx2Text,etc)
                    raw_text = docx2txt.process(
                        docx_file
                    )  # Parse in the uploadFile Class directory
                    st.write(raw_text)


if __name__ == "__main__":
    main()
