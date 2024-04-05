import requests, justext, pickle, traceback
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from langdetect import detect_langs
import pkg_resources

language_mapping = pickle.load(open(pkg_resources.resource_filename('webtextcrawler', 'resources/language_mapping.pkl'), 'rb'))

def detect_raw_language(text):
    try:
        langs = detect_langs(text)
        if len(langs) > 0:
            return str(langs[0]).split(':')[0]
    except Exception:
        traceback.print_exc()

    return 'en'

def get_justext_stopword_list(text):
    raw_lang = detect_raw_language(text)
    raw_lang = raw_lang.replace('__label__', '')
    return language_mapping.get(raw_lang, '')

def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def fetch_all_website_links(url, visited):
    try:
        urls = set()
        domain_name = urlparse(url).netloc
        soup = BeautifulSoup(requests.get(url, timeout=60).content, "html.parser")

        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                continue
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not is_valid(href):
                continue
            if href in visited:
                continue
            if domain_name not in href:
                continue
            urls.add(href)
        
        urls = [url for url in urls if 'mailto:' not in url and 'tel:' not in url]
        urls = [url.rstrip('/') for url in urls]
        return urls
    except Exception:
        return []

def extract_text_from_website(url):
    try:
        response = requests.get(url)
        paragraphs = justext.justext(
            html_text = response.content,
            stoplist = '',
            no_headings=False
        )

        temp_text = ' '.join([ p.text for p in paragraphs ])

        detected_justext_lang = get_justext_stopword_list(temp_text)

        paragraphs = justext.justext(
            html_text = response.content,
            stoplist = justext.get_stoplist(detected_justext_lang),
            no_headings=False
        )

        final_paragraphs = []

        for paragraph in paragraphs:
            if paragraph.class_type == 'good' or detected_justext_lang == '':
                final_paragraphs.append(paragraph.text)
        
        return ' '.join(final_paragraphs)
    
    except Exception:
        traceback.print_exc()
    
    return ''

def crawl(url, visited=None, max_depth=1, get_links_only=False):
    try:
        max_depth -= 1
        if max_depth < 0:
            max_depth = 0

        if visited is None:
            visited = {}

        stack = [(url, 0)] # each item in stack is a tuple (url, depth)
        sentences = []

        while stack:
            url, depth = stack.pop()
            
            if get_links_only and len(visited) >= max_depth:

                # Add back the current url to the stack
                stack.append((url, depth))

                # Return the first max_depth links
                # Keeping the "visited" in the return list
                result = {**visited, **{url: depth for url, depth in stack}}

                # Return the first "max_depth" links
                return {"links": [{"url": k, "depth": v} for k, v in list(result.items())]}    

            if len(sentences) > max_depth and not get_links_only:
                break

            if depth > max_depth or url in [ k for k, v in visited.items()]:
                continue

            visited[url] = depth

            if not get_links_only:
                current_sentences = extract_text_from_website(url)

                if current_sentences:
                    sentences.append(current_sentences)

            # call crawl recursively to all the internal links
            links = fetch_all_website_links(url, visited)

            for link in links:
                if f'{url} htt' in link:
                    link = link.replace(f'{url} http', 'http')
                if link not in [ k for k, v in visited.items()]:
                    stack.append((link, depth + 1))

        if get_links_only:
            return {"links": [{"url": k, "depth": v} for k, v in visited.items()]}
        else:
            return ' \n '.join(sentences)
    except Exception:
        traceback.print_exc()

    if get_links_only:
        return {"links": [{
            "url": url,
            "depth": 1
        }]}
    else:
        return ""

def extract_text_from_url(url):
    try:
        return crawl(url, max_depth = 1)
    except Exception:
        pass
    return None
