"""
IconArchive Harvester Engine
Extracts direct native Windows .ico binaries with header validation (00 00 01 00).
"""

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
ICO_HEADER = b"\x00\x00\x01\x00"


def fetch_html(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def download_iconarchive_ico(ico_url: str, out_path: Path) -> bool:
    try:
        req = urllib.request.Request(ico_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()

        if len(data) < 4 or data[:4] != ICO_HEADER:
            return False

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)
        return True
    except Exception:
        return False


def harvest_iconarchive_tag(tag: str, out_dir: Path, max_pages: int = 1, page_limit: int = 40) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    base_url = f"https://www.iconarchive.com/tag/{urllib.parse.quote(tag)}"

    for page in range(1, max_pages + 1):
        page_url = base_url if page == 1 else f"{base_url}?page={page}"
        print(f"[*] Scraping IconArchive: {page_url}")
        try:
            html = fetch_html(page_url)
            hrefs = re.findall(r'href=(?:["\']([^"\']+)["\']|([^\s>]+))', html)
            flat_hrefs = [h[0] or h[1] for h in hrefs]
            show_links = list(dict.fromkeys([h for h in flat_hrefs if "/show/" in h and h.endswith(".html")]))

            for show_path in show_links[:page_limit]:
                show_url = show_path if show_path.startswith("http") else "https://www.iconarchive.com" + show_path
                try:
                    show_html = fetch_html(show_url)
                    ico_matches = re.findall(
                        r'href=(?:["\']([^"\']+/download/[^"\']+\.ico)["\']|([^\s>]+/download/[^\s>]+\.ico))',
                        show_html
                    )
                    flat_ico = [m[0] or m[1] for m in ico_matches]
                    if not flat_ico:
                        continue

                    ico_url = flat_ico[0]
                    if not ico_url.startswith("http"):
                        ico_url = "https://www.iconarchive.com" + ico_url

                    file_name = ico_url.split("/")[-1]
                    out_file = out_dir / file_name

                    if download_iconarchive_ico(ico_url, out_file):
                        manifest.append({
                            "title": file_name.replace(".ico", "").replace("-", " "),
                            "file": str(out_file),
                            "source_url": ico_url,
                        })
                        print(f"    [+] Saved native ICO: {file_name}")

                    time.sleep(0.1)
                except Exception:
                    continue
        except Exception as e:
            print(f"[-] Error harvesting page {page}: {e}")

    # Write manifest
    manifest_file = out_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def search_iconarchive(title: str) -> str | None:
    """Search IconArchive for an icon title and return the best direct ICO URL."""
    clean_q = re.sub(r'\s+', ' ', title).strip()
    queries = [f"{clean_q} folder", clean_q]

    for q in queries:
        search_url = f"https://www.iconarchive.com/search?q={urllib.parse.quote(q)}"
        try:
            html = fetch_html(search_url)
            hrefs = re.findall(r'href=(?:["\']([^"\']+)["\']|([^\s>]+))', html)
            flat_hrefs = [h[0] or h[1] for h in hrefs]
            show_links = [h for h in flat_hrefs if "/show/" in h and h.endswith(".html")]

            for show_path in show_links[:4]:
                show_url = show_path if show_path.startswith("http") else "https://www.iconarchive.com" + show_path
                show_html = fetch_html(show_url)
                
                # Check show title matches cleanly
                show_title_m = re.search(r'<div[^>]*style=[^>]*font-size:18px[^>]*>"([^"]+)"</div>', show_html)
                show_title = show_title_m.group(1).lower() if show_title_m else show_url.lower()

                if clean_q.lower() in show_title:
                    ico_matches = re.findall(
                        r'href=(?:["\']([^"\']+/download/[^"\']+\.ico)["\']|([^\s>]+/download/[^\s>]+\.ico))',
                        show_html
                    )
                    flat_ico = [m[0] or m[1] for m in ico_matches]
                    if flat_ico:
                        url = flat_ico[0]
                        return url if url.startswith("http") else "https://www.iconarchive.com" + url
        except Exception:
            continue
    return None
