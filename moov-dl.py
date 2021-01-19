import os
import re
import sys
import json
import time
import hashlib
import argparse
import platform
import traceback
import subprocess

import requests
from tqdm import tqdm
from Cryptodome.Cipher import AES
from mutagen.flac import FLAC, Picture
from requests.exceptions import ConnectionError, HTTPError

from api import client


def err(msg):
	print(msg)
	traceback.print_exc()

def check_url(url):
	match = re.match(r'https?://moov.hk/#/album/([A-Z\d]{13})', url)
	return match.group(1)

def parse_cfg():
	with open('config.json') as f:
		return json.load(f)

def read_txt(txt_path):
	with open(txt_path) as f:
		return [l.strip() for l in f.readlines()]

def parse_prefs():
	cfg = parse_cfg()
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'-u', '--urls', 
		nargs='+', required=True,
		help='Multiple links or a text file filename / path.'
	)
	parser.add_argument(
		'-q', '--quality',
		choices=[1, 2], default=cfg['quality'], type=int,
		help='1 = 16-bit FLAC, 2 = 24-bit FLAC.'
	)
	parser.add_argument(
		'-t', '--template', 
		default=cfg['template'],
		help='Naming template for track filenames.'
	)
	parser.add_argument(
		'-o', '--output-dir', 
		default=cfg['output_dir'],
		help='Abs output directory. Double up backslashes or use single '
			 'forward slashes for Windows. Default: \MOOV-DL downloads'
	)
	parser.add_argument(
		'-k', '--keep-cover',	
		action='store_true', default=cfg['keep_cover'],
		help='Leave cover in album folder.'
	)
	parser.add_argument(
		'-c', '--comment',
		default=cfg['comment'],
		help='Write specified text to comment tag. Wrap in quotes.'
	)
	parser.add_argument(
		'-l', '--lyrics',
		action='store_true', default=cfg['lyrics'],
		help='Write track lyric files when available.'
	)
	parser.add_argument(
		'-m', '--meta-language',
		choices=[1, 2], default=cfg['meta_language'], type=int,
		help='Metadata language. 1 = English, 2 = Chinese.'
	)
	args = vars(parser.parse_args())
	cfg.update(args)
	if not cfg['output_dir']:
		cfg['output_dir'] = "MOOV-DL downloads"
	if not cfg['template']:
		cfg['template'] = "{track_padded}. {title}"
	cfg['quality'] = {1: 'HD', 2: 'HR'}[cfg['quality']]
	cfg['meta_language'] = {1: 'engTitle', 2: 'chiTitle'}[cfg['meta_language']]
	if cfg['urls'][0].endswith('.txt'):
		cfg['urls'] = read_txt(cfg['urls'][0])
	return cfg

def sanitize(fname):
	if is_win:
		return re.sub(r'[\/:*?"><|]', '_', fname)
	else:
		return re.sub('/', '_', fname)	

def parse_template(meta):
	try:
		return cfg['template'].format(**meta)
	except KeyError:
		print("Failed to parse filename template. Default one will be used instead.")
		return "{track_padded}. {title}".format(**meta)

def auth():
	if not client.auth(cfg['email'], cfg['password']):
		raise Exception('Failed to login.')
	print("Signed in successfully.")

def dir_setup(path):
	if not os.path.isdir(path):
		os.makedirs(path)

def parse_meta(src, meta=None, num=None, total=None, url=None):
	# Set tracktotal / num manually in case of disked albums.
	if meta:
		meta['artist'] = ", ".join(a.get('name') for a in src['artists'])
		meta['title'] =  src.get('productTitle')
		meta['track'] = num
		meta['track_padded'] = str(num).zfill(2)
	else:
		comment = cfg['comment']
		if not comment:
			comment = url	
		try:
			year = src[cfg['meta_language']][2].split('-')[0]
		except IndexError:
			year = None
		# Do alb title version.
		meta={
			'album': src[cfg['meta_language']][0],
			'albumartist': ", ".join(a.get('name') for a in src['artists']),
			'comment': comment,
			'copyright': src.get('cnote'),
			'label': src.get('albumLabel'),
			'tracktotal': total,
			'year': year
		}
	return meta

def query_quals(qualities):
	qualities = qualities.split(',')
	if cfg['quality'] == "HR" and "HR" in qualities:
		return "HR"
	elif "LL" in qualities:
		print("Unavailable in \"HR\". \"LL\" will be used instead.")
		return "LL"
	raise Exception('Unavailable in FLAC.')

def write_cov(cov_abs, url):
	r = client.s.get(url)
	r.raise_for_status()
	with open(cov_abs, 'wb') as f:
		f.write(r.content)

def decrypt(segment, content_key):
	sec = "F4:8E:09:CE:54:F7SeCrEtKkK"
	m = hashlib.md5()
	m.update((content_key + sec).encode('UTF-8'))
	key = bytes.fromhex(m.hexdigest())
	iv = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
	cipher = AES.new(key, AES.MODE_CBC, iv)
	return cipher.decrypt(segment)

def concat(paths, pre_path):
	concat_path = os.path.join('moov-dl_tmp', 'concat.txt')
	with open(concat_path, 'w') as f:
		for path in paths:
			f.write("file '{}'\n".format(path))
	subprocess.run(['ffmpeg', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 
										   concat_path, '-y', '-c', 'flac', pre_path])

# Clean up.
def download(file_meta, meta, pre_path):
	paths = []
	specs = "{bitDepth}-bit / {sampleRate} kHz FLAC".format(**file_meta)
	print("Downloading track {} of {}: {} - {}".format(meta['track'], meta['tracktotal'], 
																	  meta['title'], specs))						   
	r = client.s.get(file_meta['playUrl'], headers={'User-Agent': 'Moov-Android/1.0/hls-hr'})
	urls = [l for l in r.text.strip().split('\r\n') if not l.startswith('#')]
	total = len(urls)
	bar = tqdm(total=total, 
			   bar_format='{l_bar}{bar}{n_fmt}/{total_fmt} segments [{elapsed}<{remaining}]')
	try:
		for num, url in enumerate(urls, 1):
			for attempt in range(10):
				try:
					r = client.s.get(url)
					r.raise_for_status()
				except (HTTPError, ConnectionError):
					if attempt == 9:
						raise Exception('Failed to get segment after 10 attempts.')
					time.sleep(1)
					continue
				break
			path = os.path.join(cwd, 'moov-dl_tmp', str(num)) + ".flac"
			with open(path, 'wb') as f:
				f.write(decrypt(r.content, file_meta['contentKey']))
				bar.update(1)
			paths.append(path)
	finally:
		bar.close()
	concat(paths, pre_path)

def write_tags(pre_path, meta, cov_path):
	del meta['track_padded']
	audio = FLAC(pre_path)
	audio.delete()
	for k, v in meta.items():
		if v:
			audio[k] = str(v)
	if cov_path:
		image = Picture()
		with open(cov_path, 'rb') as f:
			image.data = f.read()
		image.type = 3
		image.mime = "image/jpeg"
		audio.add_picture(image)
	audio.save(pre_path)

def write_lyrics(tra_id, post_path):
	lyrics = client.get_lyrics(tra_id)
	if not lyrics:
		return
	with open(post_path[0:-4] + "lrc", 'w', encoding='UTF-8') as f:
		f.write(lyrics['lyric'])
	print("Wrote lyrics.")

def clean_up():
	for fname in os.listdir('moov-dl_tmp'):
		os.remove(os.path.join('moov-dl_tmp', fname))

def main(alb_id, url):
	alb_meta = client.get_album_meta(alb_id)
	total = len(alb_meta['modules'][0]['products'])
	parsed_alb_meta = parse_meta(alb_meta, total=total, url=url)
	alb_fol = "{} - {}".format(parsed_alb_meta['albumartist'], parsed_alb_meta['album'])
	alb_path = os.path.join(cfg['output_dir'], sanitize(alb_fol))
	cov_path = os.path.join(alb_path, 'cover.jpg')
	dir_setup(alb_path)
	print(alb_fol)
	for num, track in enumerate(alb_meta['modules'][0]['products'], 1):
		try:
			parsed_meta = parse_meta(track, meta=parsed_alb_meta, num=num)
			post_path = os.path.join(alb_path, sanitize(parse_template(parsed_meta)) + ".flac")
			if os.path.isfile(post_path):
				print("Track already exists locally.")
				continue
			pre_path = os.path.join(alb_path, str(num) + ".flac")
			quality = query_quals(track['qualities'])
			file_meta = client.get_file_meta(track['productId'], quality)
			download(file_meta, parsed_meta, pre_path)
			try:
				write_cov(cov_path, alb_meta['images'][0]['path'])
			except HTTPError:
				err('Failed to get cover.')
				cov_path = None
			except OSError:
				err('Failed to write cover.')
				cov_path = None
			write_tags(pre_path, parsed_meta, cov_path)
			try:
				os.rename(pre_path, post_path)
			except OSError:
				err('Failed to rename track.')
			if cfg['lyrics']:
				try:
					write_lyrics(track['productId'], post_path)
				except Exception:
					err('Failed to write lyrics.')
		except Exception:
			err('Failed to rip track.')
	if cov_path and not cfg['keep_cover']:
		if os.path.isfile(cov_path):
			os.remove(cov_path)

if __name__ == '__main__':
	print("""
 _____ _____ _____ _____     ____  __    
|     |     |     |  |  |___|    \|  |   
| | | |  |  |  |  |  |  |___|  |  |  |__ 
|_|_|_|_____|_____|\___/    |____/|_____|
	""")
	is_win = platform.system() == "Windows"
	client = client.Client()
	try:
		if hasattr(sys, 'frozen'):
			os.chdir(os.path.dirname(sys.executable))
		else:
			os.chdir(os.path.dirname(__file__))
	except OSError:
		pass
	cwd = os.getcwd()
	cfg = parse_prefs()
	dir_setup('moov-dl_tmp')
	auth()
	total = len(cfg['urls'])
	for num, url in enumerate(cfg['urls'], 1):
		print("\nAlbum {} of {}:".format(num, total))
		try:
			alb_id = check_url(url)
		except AttributeError:
			print("Invalid url:", url)
			continue
		try:
			main(alb_id, url)
		except KeyboardInterrupt:
			pass
		except Exception:
			err('Failed to rip album.')
		finally:
			clean_up()