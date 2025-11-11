import requests
from bs4 import BeautifulSoup

def scrape_herbalife_product(product_name):
    """
    Scrapes Herbalife's website to check if a product exists and retrieves its URL.

    Args:
        product_name (str): The name of the product to search for.

    Returns:
        str: The URL of the product if found, None otherwise.
    """
    base_url = "https://www.herbalife.com"
    search_url = f"{base_url}/search?q={product_name}"

    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Attempt to find product links more flexibly
        product_link = soup.find('a', href=True, text=lambda t: t and product_name.lower() in t.lower())

        if product_link:
            return base_url + product_link['href']
        else:
            return None
    except requests.RequestException as e:
        print(f"Error during scraping: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None