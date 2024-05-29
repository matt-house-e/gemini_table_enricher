import requests
import logging
from bs4 import BeautifulSoup, element
from bs4.element import Comment
from typing import Union
from usp.tree import sitemap_tree_for_homepage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def tag_visible(element):
    """
    Determines if a BeautifulSoup element is visible on the web page.
    
    Tags like 'style', 'script', 'head', 'title', 'meta', and '[document]'
    are generally not visible, so this function returns False for these elements.
    It also returns False for comment elements, which are not visible to users.
    
    Parameters:
        element (bs4.element): A BeautifulSoup element to check for visibility.
        
    Returns:
        bool: True if the element is visible, False otherwise.
    """
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def get_text_from_html(body: str) -> str:
    """
    Extracts visible text from HTML content.
    
    This function uses BeautifulSoup to parse HTML and extracts text that is visible on the page,
    skipping over tags and elements that are typically not visible (like scripts and styles).
    
    Parameters:
        body (str): HTML content as a string.
        
    Returns:
        str: A string containing all visible text from the HTML, concatenated and separated by spaces.
    """
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(string=True)
    visible_texts = filter(tag_visible, texts)  
    return " ".join(t.strip() for t in visible_texts if isinstance(t, str))


def fetch_html(url: str) -> Union[str, None]:
    """
    Fetches the HTML content from a given URL.
    
    Parameters:
        url (str): The URL of the webpage to fetch.
        
    Returns:
        Union[str, None]: The HTML content of the page, or None if an error occurred.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None


def get_text_content(url: str) -> Union[str, None]:
    """
    Fetches and extracts visible text from a webpage URL.
    
    This function sends a GET request to the specified URL, checks for a successful response,
    and then extracts all visible text from the HTML of the page.
    
    Parameters:
        url (str): The URL of the webpage from which to extract text.
        
    Returns:
        Union[str, None]: A string containing all visible text extracted from the webpage, or None if an error occurred.
    """
    html_content = fetch_html(url)
    if html_content is not None:
        return get_text_from_html(html_content)
    return None


def get_pages_from_sitemap(domain_url):
    """
    Retrieve all page URLs from the sitemap of a given domain.

    Parameters:
        domain_url (str): The full URL of the domain to fetch the sitemap from.

    Returns:
        list: A list of all page URLs found in the sitemap.
    """
    raw_page_list = []

    tree = sitemap_tree_for_homepage(domain_url)
    for page in tree.all_pages():
        raw_page_list.append(page.url)

    return raw_page_list


def get_unique_page_list(domain_url):
    """
    Filter a list of page URLs to only include unique URLs.

    Parameters:
        raw_page_list (list): A list of raw page URLs, possibly containing duplicates.

    Returns:
        list: A list of unique page URLs.
    """
    raw_page_list = get_pages_from_sitemap(domain_url)
    unique_pages = list(dict.fromkeys(raw_page_list))
    return unique_pages