"""
Release name normalizer and string sanitizers.
"""

import re

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "in", "from", "for", "to", "at",
    "by", "on", "with", "is", "s", "season", "complete", "series", "folder",
    "icon", "icons", "v1", "v2", "v3", "pack", "collection", "tv", "movie",
    "720p", "1080p", "2160p", "480p", "576p", "dvd", "bluray", "webrip", "hd"
}


def clean_series_name(raw: str) -> str | None:
    """Extract clean show title from dirty release folder name."""
    if re.search(r'\b(vpn|crack|keygen|setup|patch|unregistered)\b', raw, re.I):
        return None

    name = re.sub(r'\[.*?\]|\(.*?(?:x264|x265|hevc|10bit|bluray|dvd|web-dl|webrip|720p|1080p|mp4|mkv).*?\)|\{.*?\}', ' ', raw, flags=re.I)

    # Prefer explicit title in parenthesis if present
    eng_m = re.search(r'\((Mobile Suit Gundam[^\)]*|Spider-Man[^\)]*|The Batman[^\)]*)\)', raw)
    if eng_m:
        name = eng_m.group(1)

    name = name.replace('.', ' ').replace('_', ' ')

    cutoff = re.search(
        r'\b(?:S\d{1,2}(?:-S?\d{1,2})?(?:E\d{1,2})?|Season\s*\d+|COMPLETE|720p|1080p|2160p|480p|576p|WEBRip|WEB-DL|BluRay|HDTV|DVD|x264|x265|HEVC|AV1|AAC|DDP\d|AC3|AMZN|NF|ATVP|DSNP|HMAX|GalaxyTV|NeoNoir|ELiTE|HODL|PSA|MeGusta|Silence|Ghost|BONE)\b',
        name,
        re.I,
    )
    if cutoff:
        name = name[:cutoff.start()]

    name = re.sub(r'[\(\[]?\b(19\d\d|20\d\d)\b(?: Series)?[\)\]]?', ' ', name)
    name = re.sub(r'\b(Complete|FIRST|Season|Series|TV Series|and \d+ Movies)\b', ' ', name, flags=re.I)
    name = re.sub(r'[\-\:\,\/]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name if len(name) >= 2 else None


def sanitize_filename(name: str) -> str:
    """Sanitize title into safe Windows filename."""
    clean = re.sub(r'[\(\)\[\]\{\}\<\>:"/\\|?*]', '_', name)
    clean = re.sub(r'\s+', '_', clean).strip('_')
    return clean[:60] if len(clean) > 60 else clean
