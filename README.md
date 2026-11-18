<!-- nougen-readme-compiler: v1 -->

# 🎨 NouGenIco

Autonomous, zero-bloat Windows folder icon pipeline and media skinner.

[![License: MIT](<https://img.shields.io/badge/License-MIT-blue.svg>)](<https://github.com/Who-Visions/NouGenIco/blob/main/LICENSE>) [![Python: 3.10+](<https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg>)](<https://python.org>) [![Platform: Windows](<https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6.svg>)](<https://microsoft.com/windows>)

## 📚 Contents
- [Overview](#overview)
- [Highlights](#highlights)
- [Quick Start](#quick-start)
- [Windows Portable Skinning Spec](#windows-portable-skinning-spec)
- [Repository Layout](#repository-layout)
- [License](#license)

## 🧠 Overview

**Autonomous, zero-bloat Windows folder icon pipeline and media skinner.**

Dual-engine ingestion from **IconArchive** and **DeviantArt** with 100% portable relative `desktop.ini` bindings.

## 📌 Highlights

- **Dual-Engine Ingestion**:
  - **DeviantArt Engine**: Pulls full-resolution transparent artwork via public oEmbed and rasterizes multi-resolution Windows `.ico` pyramids (`256×256` down to `16×16` RGBA) via Pillow.
  - **IconArchive Engine**: Discovers, scrapes, and downloads direct native Windows `.ico` binaries with byte-level magic header verification (`00 00 01 00`).
- **Deterministic Name Normalization**: Automatically strips scene release metadata (`[TGx]`, `WEBRip`, `x265`, `1080p`, `ELiTE`, `NeoNoir`, `HODL`, codec/source tags) to extract canonical series titles.
- **100% Portable Windows Explorer Binding**:
  - Writes `folder.ico` directly inside the media folder (`attrib +h`).
  - Writes `desktop.ini` pointing to relative `IconResource=folder.ico,0` (`attrib +h +s`).
  - Sets the Windows Shell directory Read-Only bit (`attrib +r <folder>`).
  - **Zero hardcoded paths**: The skin survives drive letter reassignments, external drive swaps, and network shares.
- **Batch Media Skinner**: Capable of scanning an entire drive (e.g. `E:\T.V`) with dozens of series and applying authentic poster folder art in minutes.

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/Who-Visions/NouGenIco.git
cd NouGenIco
pip install -e .
```

### Usage

#### 1. Skin Any Folder with an ICO File

```bash
nougen-ico skin "E:\T.V\Shogun" "icons\shogun.ico"
```

#### 2. Fetch DeviantArt Artwork and Auto-Skin

```bash
nougen-ico get-da "https://www.deviantart.com/wake2skate/art/Shogun-1027465653" --apply "E:\T.V\Shogun"
```

#### 3. Harvest Native ICO Packs from IconArchive

```bash
nougen-ico harvest-ia "purple-folder" --out "icons/purple" --limit 50
```

#### 4. Batch-Skin an Entire Media Library Drive

```bash
nougen-ico batch-media "E:\T.V" --cache "icons/tv_cache"
```

## 📌 Windows Portable Skinning Spec

Standard tools (and manual Windows Properties dialogs) bind folder icons using absolute registry or user profile paths (e.g. `C:\Users\name\AppData\...`). When you move an external drive or change its drive letter, every single folder icon breaks.

**NouGenIco enforces the strict Windows Shell Folder specification**:

1. Directory Attribute: `attrib +r <folder>` (Signals Windows Explorer shell to inspect `desktop.ini`).
2. Configuration File: `desktop.ini` with `attrib +h +s`:

   ```ini
   [.ShellClassInfo]
   IconResource=folder.ico,0
   [ViewState]
   Mode=
   Vid=
   FolderType=Generic
   ```

3. Icon Asset: `folder.ico` stored directly in `<folder>` with `attrib +h`.

## 📌 Repository Layout

```
NouGenIco/
├── nougen_ico/
│   ├── __init__.py
│   ├── cli.py             # Unified CLI (skin, get-da, harvest-ia, batch-media)
│   ├── normalizer.py      # Scene release & filename parser
│   ├── skinner.py         # Windows Explorer attribute binder
│   └── engines/
│       ├── __init__.py
│       ├── deviantart.py  # oEmbed extraction & ICO rasterizer
│       └── iconarchive.py # Direct native ICO downloader & scraper
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

## 📄 License

MIT © [Who Visions](https://github.com/Who-Visions) / Dav3 Meralus. See `LICENSE`.

## 🔗 Links

- [NouGenIco on GitHub](<https://github.com/Who-Visions/NouGenIco>)
- [Who Visions](<https://github.com/Who-Visions>)
