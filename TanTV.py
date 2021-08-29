#!/usr/bin/python3
# TanTV

import http.server
from utils import *; logstart('TanTV')

PORT = 7133

channel_rr = Sdict(int)

class TanTVHandler(http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		global channel_rr

		channels = {k: v for k, v in yaml.safe_load(open(channels_fp)).items() if any(v)}

		if (self.path == '/list.m3u'):
			self.send_response(200)
			self.end_headers()
			self.wfile.write(('#EXTM3U\n'+'\n'.join(f"#EXTINF:-1,{i}\nhttp://{socket.gethostbyname(socket.gethostname())}:{self.server.server_port}/{ii+1}" for ii, i in enumerate(channels))+'\n').encode('utf8'))
			return

		ch = self.path.strip('/')

		if (not ch.isdigit() or int(ch) > len(channels)):
			self.send_error(404, explain=f"No such channel: {ch}")
			return

		ch = int(ch)
		urls = channels[tuple(channels.keys())[ch-1]]
		rri = channel_rr[ch-1]
		for i in (urls*2)[rri:rri+len(urls)]:
			try:
				r = requests.get(i, stream=True, timeout=(2, 5))
				if (r.ok and r.raw.read(1)): break
			except (requests.exceptions.RequestException, urllib3.exceptions.ReadTimeoutError): pass
			channel_rr[ch-1] = (rri+1) % len(urls)
		else:
			self.send_error(408)
			channel_rr[ch-1] = 0
			return

		###
		#self.send_response(200)
		#
		#for k, v in r.headers.items():
		#	self.send_header(k, v)
		#self.end_headers()
		#
		#try:
		#	for chunk in r:
		#		self.wfile.write(chunk)
		#except OSError: pass
		###

		self.send_response(302)
		self.send_header('Location', r.url)
		self.end_headers()

@apmain
@aparg('-c', metavar='file.yml', help='Channel list', type=argparse.FileType('r'), default='channels.yml')
def main(cargs):
	global channels_fp
	channels_fp = cargs.c.name
	s = http.server.ThreadingHTTPServer(('', PORT), TanTVHandler)
	try: s.serve_forever()
	except KeyboardInterrupt as ex: exit(ex)

if (__name__ == '__main__'): exit(main())
else: logimported()

# by Sdore, 2021
