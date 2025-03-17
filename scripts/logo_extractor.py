import os
import csv
import requests
import json
import cairosvg

from tqdm import tqdm
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO


class LogoExtractor:
    def __init__(self, output_dir = "..logos"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/123.0.0.0 Safari/537.36')
        }

    def _get_base_url(self, url):
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _is_logo_candidate(self, img_tag):
        keywords = ['logo', 'brand', 'company', 'site', 'header', 'main-logo']
        attributes = [
            img_tag.get('alt', ''),
            img_tag.get('id', ''),
            ' '.join(img_tag.get('class', [])),
            img_tag.get('src', '')
        ]
        for attr in attributes:
            attr_lower = attr.lower()
            if any(keyword in attr_lower for keyword in keywords):
                return True
        return False

    def _extract_logo_from_json_ld(self, soup, base_url):
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                logo_url = data.get('logo', {}).get('url')
                if logo_url:
                    return urljoin(base_url, logo_url)
            except:
                continue
        return None

    def _extract_logo_from_html(self, soup, base_url):
        possible_classes = ['logo', 'main-logo', 'site-logo', 'header-logo', 'brand-logo']
        possible_ids = ['logo', 'site-logo', 'header-logo']

        for class_name in possible_classes:
            img_tag = soup.find('img', class_=class_name)
            if img_tag and img_tag.get('src'):
                return urljoin(base_url, img_tag['src'])

        for id_name in possible_ids:
            img_tag = soup.find('img', id=id_name)
            if img_tag and img_tag.get('src'):
                return urljoin(base_url, img_tag['src'])

        logo_containers = soup.find_all(['div', 'header'], class_=lambda x: x and 'logo' in x.lower())
        for container in logo_containers:
            img_tag = container.find('img')
            if img_tag and img_tag.get('src'):
                return urljoin(base_url, img_tag['src'])

        img_tags = soup.find_all('img')
        if img_tags:
            return urljoin(base_url, img_tags[0]['src'])

        return None

    def extract_logo(self, domain):
        url = f"https://{domain}" if not domain.startswith(('http://', 'https://')) else domain

        try:
            response = requests.get(url, headers=self.headers,timeout=25)
            soup = BeautifulSoup(response.text, "html.parser")
            base_url = self._get_base_url(url)

            logo_url = (
                    self._extract_logo_from_json_ld(soup, base_url) or
                    self._extract_logo_from_html(soup, base_url)
            )

            if not logo_url:
                logo_candidates = [img for img in soup.find_all('img') if self._is_logo_candidate(img)]
                logo_url = urljoin(base_url, logo_candidates[0]['src']) if logo_candidates else None


            # svg logo fix
            head_response = requests.head(logo_url, headers=self.headers, timeout=5)
            content_type = head_response.headers.get("Content-Type", "")

            if "image/svg+xml" in content_type:
                svg_response = requests.get(logo_url, headers=self.headers, timeout=10)
                if svg_response.status_code == 200:
                    logo_svg_path = os.path.join(self.output_dir, f"{domain}.svg")
                    logo_png_path = os.path.join(self.output_dir, f"{domain}.png")

                    # save svg file
                    with open(logo_svg_path, "wb") as f:
                        f.write(svg_response.content)

                    # convert SVG → PNG
                    cairosvg.svg2png(url=logo_svg_path, write_to=logo_png_path)
                    print(f"Converted SVG to PNG for {domain}")
                    return logo_png_path
                else:
                    print(f"Failed to download SVG for {domain}")
                    return None

            # normal case png jpeg
            img_response = requests.get(logo_url, headers=self.headers, timeout=10)
            if img_response.status_code == 200:
                logo_path = os.path.join(self.output_dir, f"{domain}.png")
                Image.open(BytesIO(img_response.content)).convert("RGBA").save(logo_path)
                print(f"Logo saved for {domain}")
                return logo_path
        except Exception as e:
            print(f"Error at {url}: {e}\n")

        print(f"No logo found for {domain}\n")
        return None

    def extract_from_csv(self, csv_file_path, domain_column="domain", thread_number=20):
        with open(csv_file_path, 'r') as csv_file:
            domains = [row[domain_column] for row in csv.DictReader(csv_file)]

        # print(domains)

        #
        results = {}  # mapping between domain (key) and logo (value as path or None)

        with ThreadPoolExecutor(max_workers=thread_number) as executor:
            futures = {executor.submit(self.extract_logo, domain): domain for domain in domains}

            with tqdm(total=len(futures), desc="Processing sites") as progress_bar:
                processed = 0

                for future in as_completed(futures):
                    domain = futures[future]
                    results[domain] = future.result()
                    processed += 1
                    progress_bar.set_description(f"Processed {processed}/{len(futures)} sites")
                    progress_bar.update(1)
        return results