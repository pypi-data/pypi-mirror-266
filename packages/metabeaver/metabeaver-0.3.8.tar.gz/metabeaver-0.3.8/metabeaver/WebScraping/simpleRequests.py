import requests
from bs4 import BeautifulSoup


# This function will use requests and BeautifulSoup to return the html of a target web page.
def scrape_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Your scraping logic here - print the title of the page
        title = soup.title.string.strip()
        print(f'Title: {title}')

        # You can extract more data from the page using BeautifulSoup methods

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# Example usage:
url_to_scrape = 'https://www.google.com'
scrape_page(url_to_scrape)


### Errata ###

"""

Note that we do break a metabeaver design philosophy here - we're abstracting functionality away to bs4 and requests.

Web scraping is a complex task; a full implementation of HTML parsing and HTTP requests.

In the interests of keeping transparency for what is happening "under the hood", please see the following:
    https://requests.readthedocs.io/en/latest/
    https://www.crummy.com/software/BeautifulSoup/bs4/doc/

"""

### End of Errata - GNU Terry Pratchett ###