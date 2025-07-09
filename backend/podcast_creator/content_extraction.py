import requests
import PyPDF2
from bs4 import BeautifulSoup
from services import logger, measure_time


# Function to extract text from a URL
@measure_time
def extract_text_from_url(url):
    response = requests.get(url)
    logger.debug("Extracting text from URL begin...")
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])
        return text.strip()
    else:
        logger.exception(f"Failed to retrieve content from URL: {url}")
        raise Exception(f"Failed to retrieve content from URL: {url}")


@measure_time
def extract_text_from_pdf(pdf_path):
    logger.debug("Extracting text from PDF begin...")
    text = ""
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page].extract_text() + "\n"
    return text.strip()
