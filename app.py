import streamlit as st
import os

from PIL import Image
from PyPDF2 import PdfFileReader
import pdfplumber
from haystack.preprocessor import PreProcessor
from haystack.file_converter import PDFToTextConverter
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.retriever.sparse import ElasticsearchRetriever
from haystack.reader import TransformersReader
from haystack.pipeline import ExtractiveQAPipeline
from annotated_text import annotated_text


def annotate_answer(answers, question):
    st.write("Question: ", question)
    for answer in answers:
        answer_str = answer.get("answer")
        context = answer.get("context")
        if context:
            start_idx = context.find(answer_str)
            end_idx = start_idx + len(answer_str)
            # calculate dynamic height depending on context length
            annotated_text(
                context[:start_idx],
                (answer_str, "ANSWER", "#8ef"),
                context[end_idx:],
            )


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


st.title("EasyESG")
st.subheader("PDF")
docx_file = st.file_uploader("Upload File", type=["txt", "docx", "pdf"])
if docx_file:
    file_details = {
        "Filename": docx_file.name,
        "FileType": docx_file.type,
        "FileSize": f"{round(docx_file.size / 1e6,2)}Mb",
    }
    st.write(file_details)
    # Check File Type
    pdf_path = os.path.abspath(docx_file.name)
    converter = PDFToTextConverter(remove_numeric_tables=True, valid_languages=["en"])
    doc = converter.convert(file_path=pdf_path, meta=None)
    processor = PreProcessor(
        clean_empty_lines=True,
        clean_whitespace=True,
        clean_header_footer=True,
        split_length=100,
        split_respect_sentence_boundary=True,
        split_overlap=0,
    )
    docs = processor.process(doc)
    document_store = ElasticsearchDocumentStore(
        host="localhost",
        username="",
        password="",
        index="document",
    )
    document_store.write_documents(docs)
    retriever = ElasticsearchRetriever(document_store=document_store)
    reader = TransformersReader(
        model_name_or_path="distilbert-base-uncased-distilled-squad",
        tokenizer="distilbert-base-uncased",
        use_gpu=-1,
    )
    pipe = ExtractiveQAPipeline(reader, retriever)
    question = st.text_input("Please provide your query:", value="")
    run_query = st.button("Run")
    if run_query and question:
        result = pipe.run(
            query=question,
            top_k_retriever=10,
            top_k_reader=5,
        )
        if result["answers"]:
            annotate_answer(result["answers"], question)
