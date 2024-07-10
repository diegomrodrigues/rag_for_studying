import asyncio
import logging
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup
import markdown
import re
import json

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO
)

class AsyncCrawler:
    def __init__(self, name, urls=[], max_depth=2, ignore_domains=[], collect_domains=[], url_patterns={}, timeout=10):
        self.name = name
        self.urls = urls
        self.visited_urls = set()
        self.urls_to_visit = [(url, 0) for url in urls]  # Tuplas de (url, depth)
        self.max_depth = max_depth
        self.ignore_domains = set(ignore_domains)  # Set of domains to ignore for crawling
        self.collect_domains = set(collect_domains)  # Set of domains to collect URLs from
        self.collected_urls = {}  # Dictionary to store collected URLs by domain
        self.url_patterns = url_patterns  # Dictionary of URL patterns and their corresponding transformations
        self.timeout = timeout  # Timeout in seconds

    async def download_url(self, session, url):
        try:
            async with session.get(url, timeout=self.timeout) as response:
                return await response.text()
        except asyncio.TimeoutError:
            logging.warning(f'Timeout occurred while downloading: {url}')
            return None

    def is_markdown(self, url):
        return url.lower().endswith('.md')

    def is_pdf(self, url):
        return "pdf" in url
    
    def is_mail_to(self, url):
        return url.lower().startswith('mailto:')

    def should_crawl(self, url):
        if any(fn(url) for fn in [self.is_pdf, self.is_mail_to]):
            return False
        
        for domain in self.ignore_domains:
            if domain in url:
                return False

        return True

    def should_collect(self, url):
        # TODO: fix this
        if not "pdf" in url:
            return False

        parsed_url = urlparse(url)
        return any(domain in parsed_url.netloc for domain in self.collect_domains)

    def transform_url(self, url):
        for pattern, transform in self.url_patterns.items():
            if re.match(pattern, url):
                return transform(url)
        return url

    def parse_html(self, content):
        return BeautifulSoup(content, 'html.parser')

    def parse_markdown(self, content):
        html_content = markdown.markdown(content)
        return BeautifulSoup(html_content, 'html.parser')

    def process_links(self, url, links):
        for path in links:
            if path and not path.startswith('#'):
                if path.startswith('/'):
                    path = urljoin(url, path)
                
                transformed_path = self.transform_url(path)
                
                if self.should_collect(transformed_path):
                    self.collect_url(transformed_path)
                
                if self.should_crawl(transformed_path):
                    yield transformed_path

    def get_linked_urls(self, url, html):
        soup = self.parse_html(html)
        return self.process_links(url, (link.get('href') for link in soup.find_all('a')))

    def get_markdown_links(self, url, md_content):
        soup = self.parse_markdown(md_content)
        return self.process_links(url, (link.get('href') for link in soup.find_all('a')))

    def add_url_to_visit(self, url, depth):
        if url not in self.visited_urls and url not in [u[0] for u in self.urls_to_visit]:
            self.urls_to_visit.append((url, depth))

    def collect_url(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain not in self.collected_urls:
            self.collected_urls[domain] = set()
        self.collected_urls[domain].add(url)
        logging.info(f'Collected URL: {url}')

    async def crawl(self, session, url, depth):
        if depth > self.max_depth:
            return
        try:
            content = await self.download_url(session, url)
            if content is None:
                return
            
            if self.is_markdown(url):
                for link in self.get_markdown_links(url, content):
                    self.add_url_to_visit(link, depth + 1)
            else:
                for link in self.get_linked_urls(url, content):
                    self.add_url_to_visit(link, depth + 1)
        except Exception as e:
            logging.exception(f'Failed to crawl: {url}')
        finally:
            self.visited_urls.add(url)

    async def run(self):
        async with aiohttp.ClientSession() as session:
            while self.urls_to_visit:
                tasks = []
                for _ in range(min(10, len(self.urls_to_visit))):  # Process up to 10 URLs concurrently
                    if not self.urls_to_visit:
                        break
                    url, depth = self.urls_to_visit.pop(0)
                    if url not in self.visited_urls and self.should_crawl(url):
                        logging.info(f'Crawling: {url} at depth: {depth}')
                        task = asyncio.create_task(self.crawl(session, url, depth))
                        tasks.append(task)
                await asyncio.gather(*tasks)
        
        logging.info(f'Crawling complete.')

        logging.info(f'Collected URLs from specified domains:')
        for domain, urls in self.collected_urls.items():
            logging.info(f'{domain}: {len(urls)} URLs')
            for url in urls:
                logging.info(f'  {url}')

    def generate_json_output(self):
        output = {
            "name": self.name,
            "initial_urls": self.urls,
            "collected_urls": {}
        }

        for domain, urls in self.collected_urls.items():
            output["collected_urls"][domain] = list(urls)

        return json.dumps(output, indent=2)

if __name__ == "__main__":
    urls = [
        "https://raw.githubusercontent.com/synbol/Awesome-Parameter-Efficient-Transfer-Learning/main/README.md"        
    ]
    ignore_domains = [
        "twitter.com",
        "linkedin.com",
        "facebook.com",
        "github.com",
        "huggingface.co",
        "youtube.com",
        "blog.google"
        # Add more domains to ignore as needed
    ]
    collect_domains = [
        "arxiv.org"
        # Add more domains to collect URLs from as needed
    ]
    
    # Define URL patterns and their transformations
    def arxiv_to_pdf(url):
        match = re.search(r'arxiv.org/abs/(\d+\.\d+)', url)
        if match:
            return f"https://arxiv.org/pdf/{match.group(1)}.pdf"
        return url

    # URL pattern for arXiv links in the format 'https://arxiv.org/abs/1234.5678'
    url_patterns = {
        r'https?://arxiv.org/abs/\d+\.\d+': arxiv_to_pdf,
        # Add more patterns and transformations as needed
    }

    crawler = AsyncCrawler(
        name="parameter-efficient-fine-tunning",
        urls=urls, 
        max_depth=1, 
        ignore_domains=ignore_domains, 
        collect_domains=collect_domains, 
        url_patterns=url_patterns
    )
    asyncio.run(crawler.run())

    # Generate and save JSON output
    json_output = crawler.generate_json_output()
    with open(f"assets/results/crawler_{crawler.name}.json", "w") as f:
        f.write(json_output)

    logging.info("Results saved to crawler.json")