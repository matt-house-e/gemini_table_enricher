import logging
from .scraper import get_text_content, get_unique_page_list

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.CRITICAL

def scrape_url_content(external_data, urls):
    """
    Scrape content from the URL(s) provided and add it to the external data dictionary.
    Handles both single URL and list of URLs.

    Parameters:
        external_data (dict): Dictionary to store external data.
        urls (str or list): The URL(s) to fetch content from.
    """
    try:
        if isinstance(urls, list):
            content_list = []
            for url in urls:
                try:
                    content = get_text_content(url)
                    content_list.append(content)
                except Exception as e:
                    logging.error(f"Error scraping URL content for URL {url}: {e}")
                    content_list.append('')  # Append empty string on error
            external_data['URL Content'] = content_list
        
        else:
            content = get_text_content(urls)
            external_data['URL Content'] = content
    
    except Exception as e:
        logging.error(f"Error scraping URL content for URLs {urls}: {e}")
        external_data['URL Content'] = ''  # Default to empty string on error


def find_sub_pages(external_data, base_url):
    """
    Find sub-pages from the given base URL and add the list to the external data dictionary.

    Parameters:
        external_data (dict): Dictionary to store external data.
        base_url (str): The base URL to find sub-pages from.
    """
    try:
        pages = get_unique_page_list(base_url)
        external_data['Sub Pages'] = pages
    except Exception as e:
        logging.error(f"Error finding sub-pages for domain {base_url}: {e}")
        external_data['Sub Pages'] = []  # Default to empty list on error
