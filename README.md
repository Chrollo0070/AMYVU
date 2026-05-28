# AMYVU

A Python toolkit for discovering YouTube channels and extracting random video clips.

## Features

- **Channel Discovery** — Search and find YouTube channels based on criteria
- **Random Clip Extraction** — Pull random clips from videos for sampling or previewing content

## Files

| File | Description |
|---|---|
| `find_channels.py` | Search and retrieve YouTube channels |
| `extract_random_clip.py` | Extract a random clip from a given video |

## Requirements

```bash
pip install -r requirements.txt
```

> Make sure you have [FFmpeg](https://ffmpeg.org/) installed for video processing.

## Usage

### Find Channels

```bash
python find_channels.py --query "your search term"
```

### Extract a Random Clip

```bash
python extract_random_clip.py --url "https://youtube.com/watch?v=..." --duration 30
```

## Setup

1. Clone the repository
```bash
   git clone https://github.com/Chrollo0070/AMYVU.git
   cd AMYVU
```

2. Install dependencies
```bash
   pip install -r requirements.txt
```

3. Add your API key (if required) to a `.env` file
YOUTUBE_API_KEY=your_key_here

## License

MIT
