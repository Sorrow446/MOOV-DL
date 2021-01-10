# MOOV-DL
Tool written in Python to download streamable tracks from [moov.hk](https://moov.hk/).   
**People have been seen selling my tools. DO NOT buy them. My tools are free and always will be.**
![](https://orion.feralhosting.com/sorrow/share/moov-dl.png)
[Windows binaries](https://github.com/Sorrow446/MOOV-DL/releases)

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
1. Put FFmpeg binary in MOOV-DL's folder ([Windows](https://github.com/BtbN/FFmpeg-Builds/releases) | [Linux](https://johnvansickle.com/ffmpeg/)). It is needed for segment concatenation.
2. Fill in config.json (any specified CLI arguments will override these).

MOOV-DL will add itself as a device to your account upon logging in. It will appear as "Google+PIXEL+2XL". [Remove devices here](https://moov.hk/#/user/deviceMapping).

# Account Info
- Usable in any country. No VPN needed or any payment region restrictions.
- 14-day free trials are being offered at the time of typing this.
- [Subscription plans](https://moov.hk/reg/paynow.html?lang=en_us) (prices are in HKD). The easiest payment method is through the Android app via Google Pay.
