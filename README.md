# MOOV-DL
Tool written in Python to download streamable tracks from moov.hk.   
**People have been seen selling my tools. DO NOT buy them. My tools are free and always will be.**   
[Windows binaries](https://github.com/Sorrow446/MOOV-DL/releases)
![](https://i.imgur.com/cC5D1Mh.png)

```
 _____ _____ _____ _____     ____  __
|     |     |     |  |  |___|    \|  |
| | | |  |  |  |  |  |  |___|  |  |  |__
|_|_|_|_____|_____|\___/    |____/|_____|

usage: moov-dl.py [-h] -u URLS [URLS ...] [-q {1,2}] [-t TEMPLATE]
                  [-o OUTPUT_DIR] [-k] [-c COMMENT] [-l] [-m {1,2}]

optional arguments:
  -h, --help            show this help message and exit
  -u URLS [URLS ...], --urls URLS [URLS ...]
                        Multiple links or a text file filename / path.
  -q {1,2}, --quality {1,2}
                        1 = 16-bit FLAC, 2 = 24-bit FLAC.
  -t TEMPLATE, --template TEMPLATE
                        Naming template for track filenames.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Abs output directory. Double up backslashes or use
                        single forward slashes for Windows. Default: \MOOV-DL
                        downloads
  -k, --keep-cover      Leave cover in album folder.
  -c COMMENT, --comment COMMENT
                        Write specified text to comment tag. Wrap in quotes.
  -l, --lyrics          Write track lyric files when available.
  -m {1,2}, --meta-language {1,2}
                        Metadata language. 1 = English, 2 = Chinese.
```
# Setup
### Binary
1. Put [FFmpeg binary (win64, gpl)](https://github.com/BtbN/FFmpeg-Builds/releases) in MOOV-DL's folder.
2. Fill in `config.json` (any specified CLI arguments will override these).
3. Call it with your args via Command Prompt. `moov-dl_x86.exe -u <album url>`

### Source
1. Win: Put [FFmpeg binary (win64, gpl)](https://github.com/BtbN/FFmpeg-Builds/releases) in MOOV-DL's folder / Lin: Install FFmpeg. `sudo apt install ffmpeg`.
2. Install requirements. `pip3 install -r requirements.txt`
3. Fill in `config.json` (any of the same specified CLI arguments will override these).
4. Call it with your args. `python/python3 moov-dl.py -u <album url>`

### Termux
1. Unpack `MOOV-DL-main.zip`. This guide will be using the downloads folder.
2. Install Python 3. `pkg install python`
3. Install FFmpeg. `pkg install ffmpeg`
3. CD into MOOV-DL's dir. `cd /storage/emulated/0/download/MOOV-DL-main/`
6. Install requirements. `pip3 install -r requirements.txt`
7. Fill in `config.json` (any specified CLI arguments will override these).
8. Call it with your args. `python/python3 moov-dl.py -u <album url>`

Downloaded albums will be written to `<script dir>\MOOV-DL downloads` unless you specify otherwise. CD'ing will be handled for you.      
MOOV-DL will add itself as a device to your account upon logging in. It will appear as "Google+PIXEL+2XL". [Remove devices here](http://www.dereferer.org/?https%3A%2F%2Fmoov%2Ehk%2F%23%2Fuser%2FdeviceMapping).

# Account Info
- Usable in any country. No VPN needed or any payment region restrictions.
- 14-day free trials are being offered at the time of typing this.
- [Subscription plans](http://www.dereferer.org/?https%3A%2F%2Fmoov%2Ehk%2Freg%2Fpaynow%2Ehtml%3Flang%3Den%5Fus) (prices are in HKD). The easiest payment method is through the Android app via Google Pay.
