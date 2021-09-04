import streamlit as st
import os
import requests

import docx2txt
from PIL import Image
from PyPDF2 import PdfFileReader
import pdfplumber
from preprocess import extract_text_lxml, process_text


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
