def fetch_webpage(url: str) -> str:
    """
    Fetch a webpage and convert it to markdown/text format using Jina AI reader.

    Args:
        url: The URL of the webpage to fetch and convert

    Returns:
        String containing the webpage content in markdown/text format
    """
    import requests
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Construct the Jina AI reader URL
        jina_url = f"https://r.jina.ai/{url}"

        # Make the request to Jina AI
        response = requests.get(jina_url, timeout=30)
        response.raise_for_status()

        logger.info(f"Successfully fetched webpage: {url}")
        return response.text

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching webpage {url}: {e}")
        raise Exception(f"Error fetching webpage: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching webpage {url}: {e}")
        raise Exception(f"Unexpected error: {str(e)}")