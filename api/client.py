import requests


class Client():

	def __init__(self):	
		self.s = requests.Session()
		self.base = "https://mtg.now.com/moov/api/"

	def make_call(self, method, epoint, headers, params=None, data=None):
		r = self.s.request(method, self.base + epoint, headers=headers, params=params, data=data)
		r.raise_for_status()
		if epoint == "user/loginstatuscheck":
			return r
		else:
			return r.json()

	def auth(self, email, pwd):
		data={
			'deviceid': 'fgq7hzlFQE-Gsf7sj9RiC5',
			'devicetype': 'Android',
			'clientver': '3.0.7',
			'brand': 'Android',
			'model': 'PIXEL+2XL',
			'os': 'Android',
			'osver': '10.0.0',
			'devicename': 'Google+PIXEL+2XL',
			'connect': 'WiFi',
			'lang': 'en_US',
			'loginid': email,
			'notifyid': '',
			'password': pwd,
			'autologin': 'true'
		}
		headers={
			'User-Agent': 'Mozilla/5.0 (Linux; Android 10.0.0; PIXEL 2XL Build/NOF26V; wv)'
						  'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.'
						  '3729.136 Mobile Safari/537.36/Moov'
		}
		r = self.make_call(
			'POST', 'user/loginstatuscheck', headers, data=data
		)
		return r.headers['Content-Type'] == "application/xml;charset=UTF-8"

	def get_album_meta(self, alb_id):
		headers={
			'User-Agent': 'Mozilla/5.0 (Linux; Android 10.0.0; PIXEL 2XL Build/NOF26V; wv)'
						  'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.'
						  '3729.136 Mobile Safari/537.36/Moov'
		}
		params={
			'profileId': alb_id,
			'features': '24bit',
			'deviceType': 'phones3',
			'refType': 'PAB',
			'checksum': ''
		}
		return self.make_call(
			'GET', 'profile/getProfile', headers, params=params
		)['dataObject']

	def get_file_meta(self, tra_id, quality):
		headers={
			'User-Agent': 'okhttp/4.8.0'
		}
		params={
			'clientver': '3.0.7',
			'action': 'stream',
			'streamtype': 'stdhls',
			'preview': 'F',
			'cat': 'playlist',
			'pid': tra_id,
			'isUpSample': 'false',
			'osver': '10.0.0',
			'refid': '',
			'quality': quality,
			'devicetype': 'Android',
			'connect': 'WiFi',
			'reftype': '',
			'deviceid': 'fgq7hzlFQE-Gsf7sj9RiC5',
			'application': 'moovnext',
			'isStudioMaster': 'true'
		}
		return self.make_call(
			'GET', 'content/checkout', headers, params=params
		)['result']['dataObject']
	
	def get_lyrics(self, tra_id):
		headers={
			'User-Agent': 'Mozilla/5.0 (Linux; Android 10.0.0; PIXEL 2XL Build/NOF26V; wv)'
						  'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.'
						  '3729.136 Mobile Safari/537.36/Moov'
		}
		params={
			'pid': tra_id
		}
		return self.make_call(
			'GET', 'lyric/getLyric', headers, params=params
		)['dataObject']