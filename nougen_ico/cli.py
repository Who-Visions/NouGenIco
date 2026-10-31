"""
NouGenIco Command Line Interface
Unified CLI for harvesting, converting, and skinning Windows folders.
"""

import argparse
import sys
from pathlib import Path
from .normalizer import clean_series_name, sanitize_filename
from .skinner import apply_portable_skin, is_folder_skinned
from .engines.iconarchive import harvest_iconarchive_tag, search_iconarchive, download_iconarchive_ico
from .engines.deviantart import fetch_deviantart_deviation, harvest_deviantart_gallery

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser(
        prog="nougen-ico",
        description="NouGenIco — Autonomous, zero-bloat Windows folder icon pipeline and media skinner."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: skin
    skin_parser = subparsers.add_parser("skin", help="Apply an ICO file to a target folder using portable desktop.ini")
    skin_parser.add_argument("folder", type=str, help="Path to target directory")
    skin_parser.add_argument("ico", type=str, help="Path to .ico file")

    # Command: get-da
    da_parser = subparsers.add_parser("get-da", help="Fetch a single DeviantArt artwork URL and convert to Windows ICO")
    da_parser.add_argument("url", type=str, help="DeviantArt deviation URL")
    da_parser.add_argument("--out", type=str, default="icons", help="Output directory")
    da_parser.add_argument("--apply", type=str, help="Optional directory to immediately skin with the fetched ICO")

    # Command: harvest-ia
    ia_parser = subparsers.add_parser("harvest-ia", help="Harvest native ICOs from IconArchive by tag or search")
    ia_parser.add_argument("tag", type=str, help="Tag or query to harvest (e.g. 'purple-folder')")
    ia_parser.add_argument("--out", type=str, default="icons/iconarchive", help="Output directory")
    ia_parser.add_argument("--limit", type=int, default=30, help="Max items to download")

    # Command: batch-media
    batch_parser = subparsers.add_parser("batch-media", help="Scan a media library drive/folder and skin all series")
    batch_parser.add_argument("dir", type=str, help="Path to media library (e.g. 'E:\\T.V')")
    batch_parser.add_argument("--cache", type=str, default="icons/cache", help="Icon cache directory")
    batch_parser.add_argument("--force", action="store_true", help="Overwrite already skinned folders")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "skin":
        folder = Path(args.folder)
        ico = Path(args.ico)
        if not folder.is_dir():
            print(f"[-] Target folder does not exist: {folder}")
            sys.exit(1)
        if not ico.is_file():
            print(f"[-] Icon file does not exist: {ico}")
            sys.exit(1)
        if apply_portable_skin(folder, ico):
            print(f"[+] Successfully applied portable folder skin to {folder}")
        else:
            print(f"[-] Failed applying folder skin to {folder}")

    elif args.command == "get-da":
        out = Path(args.out)
        res = fetch_deviantart_deviation(args.url, out)
        if not res:
            print(f"[-] Failed fetching deviation: {args.url}")
            sys.exit(1)
        print(f"[+] Successfully generated Windows ICO: {res['ico_file']}")
        if args.apply:
            target = Path(args.apply)
            if target.is_dir():
                apply_portable_skin(target, Path(res['ico_file']))
                print(f"[+] Bound to folder: {target}")

    elif args.command == "harvest-ia":
        out = Path(args.out)
        manifest = harvest_iconarchive_tag(args.tag, out, page_limit=args.limit)
        print(f"[+] Harvested {len(manifest)} native Windows ICOs to {out}")

    elif args.command == "batch-media":
        media_dir = Path(args.dir)
        cache_dir = Path(args.cache)
        if not media_dir.is_dir():
            print(f"[-] Directory does not exist: {media_dir}")
            sys.exit(1)

        cache_dir.mkdir(parents=True, exist_ok=True)
        folders = sorted([f for f in media_dir.iterdir() if f.is_dir()])
        print(f"[*] Processing {len(folders)} folders in {media_dir}...")

        skinned = 0
        skipped = 0
        for f in folders:
            if not args.force and is_folder_skinned(f):
                skipped += 1
                continue

            clean = clean_series_name(f.name)
            if not clean:
                continue

            safe = sanitize_filename(clean)
            cached_ico = cache_dir / f"{safe}.ico"

            if not cached_ico.exists():
                url = search_iconarchive(clean)
                if url:
                    download_iconarchive_ico(url, cached_ico)

            if cached_ico.exists():
                if apply_portable_skin(f, cached_ico):
                    print(f"[+] Skinned: {f.name}")
                    skinned += 1

        print(f"\n[*] Finished. Skinned: {skinned}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
