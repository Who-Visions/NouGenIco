"""
DeviantArt Harvester Engine
Leverages DeviantArt oEmbed endpoint and gallery RSS feeds to extract high-resolution
transparent folder art and rasterizes multi-resolution Windows .ico pyramids.
"""

import io
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
ICO_SIZES = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
MEDIA_NS = "http://search.yahoo.com/mrss/"


def sanitize_filename(name: str) -> str:
    clean = re.sub(r'[\(\)\[\]\{\}\<\>:"/\\|?*]', '_', name)
    clean = re.sub(r'\s+', '_', clean).strip('_')
    return clean[:60] if len(clean) > 60 else clean


def convert_png_to_ico(png_data: bytes, ico_path: Path, png_path: Path | None = None) -> bool:
    """Save pristine high-res PNG and convert to Windows .ico with multi-resolution hierarchy."""
    try:
        img = Image.open(io.BytesIO(png_data))
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        if png_path:
            png_path.parent.mkdir(parents=True, exist_ok=True)
            png_path.write_bytes(png_data)

        ico_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(ico_path, format="ICO", sizes=ICO_SIZES)
        return True
    except Exception as e:
        print(f"[-] Failed converting to ICO {ico_path}: {e}")
        return False


def fetch_deviantart_deviation(deviation_url: str, out_dir: Path) -> dict | None:
    """Fetch single deviation artwork via DeviantArt oEmbed and build .ico + .png."""
    oembed_url = f"https://backend.deviantart.com/oembed?url={urllib.parse.quote(deviation_url)}"
    req = urllib.request.Request(oembed_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        title = data.get("title", "Untitled")
        author = data.get("author_name", "Unknown")
        image_url = data.get("fullsize_url") or (data.get("url") if data.get("type") == "photo" else None) or data.get("thumbnail_url")
        if not image_url:
            return None

        out_dir.mkdir(parents=True, exist_ok=True)
        base_name = sanitize_filename(title)
        ico_file = out_dir / f"{base_name}.ico"
        png_file = out_dir / f"{base_name}.png"

        req_img = urllib.request.Request(image_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req_img, timeout=15) as resp_img:
            png_data = resp_img.read()

        if convert_png_to_ico(png_data, ico_file, png_file):
            return {
                "title": title,
                "author": author,
                "ico_file": str(ico_file),
                "png_file": str(png_file),
                "source_url": deviation_url,
                "image_url": image_url
            }
        return None
    except Exception as e:
        print(f"[-] DeviantArt oEmbed fetch failed: {e}")
        return None


def harvest_deviantart_gallery(user: str, gallery_id: str | None, out_dir: Path, limit: int = 50) -> list[dict]:
    """Harvest deviations from user gallery via DeviantArt RSS feed."""
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    
    query = f"gallery:{user}/{gallery_id}" if gallery_id else f"by:{user}"
    url = f"https://backend.deviantart.com/rss.xml?q={urllib.parse.quote(query)}&offset=0"
    
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read()

        root = ET.fromstring(data)
        items = []
        for item in root.findall(".//item"):
            title_elem = item.find("title")
            link_elem = item.find("link")
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Untitled"
            link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""

            media_url = None
            for content in item.findall(f".//{{{MEDIA_NS}}}content"):
                url_attr = content.attrib.get("url")
                if url_attr:
                    media_url = url_attr

            if not media_url:
                for thumb in item.findall(f".//{{{MEDIA_NS}}}thumbnail"):
                    url_attr = thumb.attrib.get("url")
                    if url_attr:
                        media_url = url_attr

            author = user
            credit = item.find(f".//{{{MEDIA_NS}}}credit")
            if credit is not None and credit.text:
                author = credit.text.strip()

            if media_url:
                items.append({"title": title, "link": link, "image_url": media_url, "author": author})

        for item in items[:limit]:
            base_name = sanitize_filename(item["title"])
            ico_file = out_dir / f"{base_name}.ico"
            png_file = out_dir / f"{base_name}.png"

            try:
                req_img = urllib.request.Request(item["image_url"], headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req_img, timeout=12) as resp_img:
                    raw_data = resp_img.read()

                if convert_png_to_ico(raw_data, ico_file, png_file):
                    manifest.append({
                        "title": item["title"],
                        "author": item["author"],
                        "ico_file": str(ico_file),
                        "png_file": str(png_file),
                        "source_url": item["link"]
                    })
                    print(f"    [+] Converted: {item['title']} by {item['author']}")
            except Exception:
                continue

        manifest_file = out_dir / "manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest
    except Exception as e:
        print(f"[-] Gallery harvest error: {e}")
        return manifest
