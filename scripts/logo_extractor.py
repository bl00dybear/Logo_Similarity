import os
import csv
import requests
import json
import cairosvg
import re
import base64

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

        def normalize_url(img_tag):
            if img_tag and img_tag.get('src'):
                return urljoin(base_url, img_tag['src'].strip())
            return None

        possible_classes = [
            'logo', 'site-logo', 'header-logo', 'brand-logo', 'main-logo', 'company-logo',
            'navbar-logo', 'nav-logo', 'site-header-logo', 'corporate-logo', 'primary-logo',
            'header-site-logo', 'masthead-logo', 'home-logo', 'brand-image', 'top-logo'
        ]
        possible_ids = possible_classes
        possible_alt = possible_classes

        for class_name in possible_classes:
            img_tag = soup.find('img', class_=lambda x: x and class_name in x.lower())
            logo_url = normalize_url(img_tag)
            if logo_url:
                return logo_url

        for id_name in possible_ids:
            img_tag = soup.find('img', id=lambda x: x and id_name in x.lower())
            logo_url = normalize_url(img_tag)
            if logo_url:
                return logo_url

        for alt_name in possible_alt:
            img_tag = soup.find('img', alt=lambda x: x and alt_name in x.lower())
            logo_url = normalize_url(img_tag)
            if logo_url:
                return logo_url

        logo_containers = soup.find_all(['div', 'header', 'a', 'span', 'nav'],
                                        class_=lambda x: x and 'logo' in x.lower())

        for container in logo_containers:
            img_tag = container.find('img')
            logo_url = normalize_url(img_tag)
            if logo_url:
                return logo_url

            style = container.get('style', '')
            background_match = re.search(r'background(?:-image)?:\s*url\([\'"]?(.*?)[\'"]?\)', style)
            if background_match:
                return urljoin(base_url, background_match.group(1))

        for img in soup.find_all('img'):
            alt_text = img.get('alt', '').lower()
            title_text = img.get('title', '').lower()

            if 'logo' in alt_text or 'logo' in title_text:
                logo_url = normalize_url(img)
                if logo_url:
                    return logo_url

        for svg in soup.find_all('svg'):
            if (svg.get('id') and 'logo' in svg.get('id').lower()) or \
                    (svg.get('class') and any('logo' in c.lower() for c in svg.get('class'))):
                svg_id = svg.get('id')
                if svg_id:
                    return f"{base_url}#{svg_id}"

            use_tag = svg.find('use')
            if use_tag and use_tag.get('href'):
                return urljoin(base_url, use_tag['href'])

        meta_tags = [
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            'link[rel="apple-touch-icon"]',
            'link[rel="icon"]'
        ]
        for tag in meta_tags:
            element = soup.select_one(tag)
            if element:
                return urljoin(base_url, element.get('content') or element.get('href'))

        for link in soup.find_all(['a', 'link'], href=True):
            img_tag = link.find('img')
            logo_url = normalize_url(img_tag)
            if logo_url:
                return logo_url

        header = soup.find(['header', 'nav', 'div'],
                           class_=lambda x: x and ('header' in x.lower() or 'nav' in x.lower()))
        if header:
            img_tag = header.find('img')
            logo_url = normalize_url(img_tag)
            if logo_url:
                return logo_url

        small_images = [img for img in soup.find_all('img') if img.get('src') and
                        (img.get('width') and int(img.get('width')) < 300 or
                         img.get('height') and int(img.get('height')) < 150)]

        if small_images:
            return normalize_url(small_images[0])

        img_tags = soup.find_all('img', src=True)
        if img_tags:
            return normalize_url(img_tags[0])

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
            if logo_url.startswith("data:image/gif"):
                try:
                    print(f"Converting base64 GIF to PNG for {domain}...")

                    encoded_data = logo_url.split(",", 1)[1]
                    image_data = base64.b64decode(encoded_data)

                    with Image.open(BytesIO(image_data)) as img:
                        logo_png_path = os.path.join(self.output_dir, f"{domain}.png")
                        img.convert("RGBA").save(logo_png_path)

                    print(f"Saved GIF as PNG: {logo_png_path}")
                    return logo_png_path
                except Exception as e:
                    print(f"Error processing GIF for {domain}: {e}")
                    return None

            if logo_url.startswith("data:image/svg+xml"):
                svg_data = logo_url.split(",", 1)[1]
                svg_data = requests.utils.unquote(svg_data)

                logo_svg_path = os.path.join(self.output_dir, f"{domain}.svg")
                logo_png_path = os.path.join(self.output_dir, f"{domain}.png")

                with open(logo_svg_path, "w", encoding="utf-8") as f:
                    f.write(svg_data)

                # Convert SVG → PNG
                cairosvg.svg2png(url=logo_svg_path, write_to=logo_png_path)
                os.remove(logo_svg_path)

                print(f"Converted inline SVG to PNG for {domain}")
                return logo_png_path

            try:
                head_response = requests.head(logo_url, headers=self.headers, timeout=5)
                content_type = head_response.headers.get("Content-Type", "")

                if "image/svg+xml" in content_type:
                    svg_response = requests.get(logo_url, headers=self.headers, timeout=10)
                    if svg_response.status_code == 200:
                        logo_svg_path = os.path.join(self.output_dir, f"{domain}.svg")
                        logo_png_path = os.path.join(self.output_dir, f"{domain}.png")

                        with open(logo_svg_path, "wb") as f:
                            f.write(svg_response.content)

                        # convert SVG → PNG
                        cairosvg.svg2png(url=logo_svg_path, write_to=logo_png_path)
                        os.remove(logo_svg_path)
                        print(f"Converted SVG to PNG for {domain}")
                        return logo_png_path
                    else:
                        print(f"Failed to download SVG for {domain}")
                        return None
            except Exception as e:
                print(f"Error handling external SVG for {domain}: {e}")


            try:
                img_response = requests.get(logo_url, headers=self.headers, timeout=10)
                if img_response.status_code == 200:
                    logo_path = os.path.join(self.output_dir, f"{domain}.png")
                    Image.open(BytesIO(img_response.content)).convert("RGBA").save(logo_path)
                    print(f"Logo saved for {domain}")
                    return logo_path
            except Exception as e:
                print(f"Error processing PNG/JPEG for {domain}: {e}")
        except Exception as e:
            print(f"Error at {url}: {e}\n")

        print(f"No logo found for {domain}\n")
        return None

    def extract_from_csv(self, csv_file_path, domain_column="domain", thread_number=20):
        with open(csv_file_path, 'r') as csv_file:
            domains = [row[domain_column] for row in csv.DictReader(csv_file)]

        # print(domains)

        results = {}

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