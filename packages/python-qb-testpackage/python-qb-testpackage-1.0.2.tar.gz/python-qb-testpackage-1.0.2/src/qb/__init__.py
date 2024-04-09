#FF-Quantum Bridge API; GNU GPL v3

import json, time, secrets, base64, asyncio
from threading import Thread
from typing import Coroutine
from urllib.parse import urlparse
import websockets.sync.client as cli
from websockets import ConnectionClosed, ConnectionClosedError
from pycolorutils.color import *

QB_SRV = "forestfire.net/qb"
HTTP_SEP = '\r\n'

class QB:
	def __init__(self, timeout: int=120, pwd=None, path='/', proto='https', server=QB_SRV, mode=None):
		self.mode = mode; self.path = path; self.proto = proto; self.srv = server
		self.onOpen = self.onClose = self.onCli = self.onReq = self.onSck = None
		self.en = self.ws = self.code = self.hole = self._addr = None
		self.t = timeout; self.st = self.t*2
		self.pwd = pwd or (base64.b64encode(secrets.token_bytes(9))
			.decode('utf-8').replace('/','-'))

	def connect(self, run=True):
		if run and self.en: return
		self.en = True
		self.ws = cli.connect(f"wss://{self.srv}", open_timeout=self.t, close_timeout=self.st, compression=None)
		if self._recv() != "QB1": raise IOError("Bad Ver")
		if self.mode == 'ho': #Open Hole
			self._addr = self.ws.local_address
			self.ws.send(f"IP1,{self.path}")
			self.hole = self._recv()
			self.close()
		elif self.mode == 'ws': #Open WebSocket
			self.ws.send(f"QW1,{self.path},{self.proto}")
			self._addr = self._recv()
		else:
			if self.mode == 'hole':
				self.ws.send(f"QT1,{self.pwd},{self.st},{self.path},{self.proto}")
			else: self.ws.send(f"QB1,{self.pwd},{self.st}")
			self.code = self._recv()[1:]
			if len(self.code) != 11: raise IOError(f"Bad Code '{self.code}'")
			self.ws.send("ok")
			if run: Thread(target=self._run).start()
			msg(C.Di+"[QB Ready]")
			if self.onOpen: self.onOpen(self)

	def getURL(self):
		if self.mode == 'hole': return f"https://{self.srv}/pair?{self.code},{self.pwd}"
		return f"https://{self.srv}/{self.code},{self.pwd}"

	def _run(self):
		LPing = time.monotonic()
		while self.en:
			try:
				try: m = self._recv(.5)
				except TimeoutError:
					tn = time.monotonic()
					if tn-LPing > self.t:
						self.ws.ping(); LPing=tn
				else:
					if m[0] == 'C': #Client
						if not self.onCli: raise NotImplementedError
						qb = QB(mode='ho', path=self.code); qb.connect()
						self.onCli(self, m[1:], qb._addr, qb.hole)
					elif m[0] == 'R': #Request
						if not self.onReq: raise NotImplementedError
						self.onReq(QBRequest(self,m[1:]), QBResponse(self))
					elif m[0] == 'W': #Socket
						if not self.onSck: raise NotImplementedError
						m = m[1:].split(',')
						if len(m) != 2: raise ValueError("Bad WS Req")
						qb = QB(mode='ws', path=self.code, proto=m[1]); qb.connect()
						self.onSck(qb.ws, m[0], qb._addr)
					else: raise IOError("Unknown Cmd "+m[0])
					LPing = time.monotonic()
			except ConnectionClosed as e:
				if isinstance(e,ConnectionClosedError): err("WS "+eInfo(e))
				if self.onClose: self.onClose(self)
				msg(C.Di+f"[Reconnecting to QB]")
				while self.en:
					try: self.connect(False); break
					except Exception as e:
						err("QB "+eInfo(e)); time.sleep(10)
			except Exception as e: err("QB "+eInfo(e))
		self.ws.close()
		if self.onClose: self.onClose(self)

	def _recv(self, t=None, ne=False) -> str | bytes:
		m = self.ws.recv(self.st if t is None else t)
		if not ne and isinstance(m,str) and m.startswith('E'):
			raise IOError(f"Remote Error: {m[1:]}")
		return m

	def close(self):
		self.ws.close_timeout = 10
		self.en = False

#--- HTTP Server ---

class QBRequest:
	def __init__(self, qb, m: str):
		self.qb: QB = qb
		m=m.split(HTTP_SEP); rq=m[0].split(' ')
		if len(rq) != 3: raise IOError("Bad Req")
		self.sender = rq[0]
		self.meth: str = rq[1]
		self.url = urlparse(rq[2])
		self.path = self.url.path
		self.query = self.url.query
		hdr = {}
		for h in m[1:]:
			n = h.index(': '); hdr[h[:n]] = h[n+2:]
		self.headers = hdr

def _genHdr(hdr: dict):
	hl = []
	for h in hdr: hl.append(f"{h}: {hdr[h]}")
	return HTTP_SEP.join(hl)

class QBResponse:
	def __init__(self, qb):
		self.qb: QB = qb
		self.ended = False

	def send(self, res: str | bytes, hdr: dict=None):
		if self.ended: return
		self.ended = True
		if hdr: self.qb.ws.send('H'+_genHdr(hdr))
		if not isinstance(res, bytes): res=bytes(res,'utf-8')
		self.qb.ws.send(res)

	def sendCode(self, code: int, es: str=None):
		if self.ended: return
		self.ended = True
		es = f"E{code}{':'+es if es else ''}"
		err("QB Err "+es); self.qb.ws.send(es)

#--- Socket.IO-like WebSockets ---

MSG_ID_MAX=999999
class QBSocketServer:
	def __init__(self, qb: QB):
		self.cliList = []; self.evl = {}; self.mid = 0
		self.qb = qb; qb.onSck = self._newSck
		self.loop = asyncio.new_event_loop()
		Thread(target=self.loop.run_forever).start()
		self.run = True

	def _newSck(self, ws: cli.ClientConnection, dest, addr):
		sck = QBSocket(self, ws, dest, addr)
		self.cliList.append(sck); self.ev('connect',sck)

	def ev(self, ev, *args):
		ev = self.evl.get(ev)
		if ev: return ev(*args)

	def on(self, ev, func):
		self.evl[ev] = func

	def emit(self, *args):
		for c in self.cliList: c.emit(*args)

	def close(self):
		self.loop.call_soon_threadsafe(self.loop.stop)

class QBSocket:
	def __init__(self, ss: QBSocketServer, ws: cli.ClientConnection, dest, addr):
		self.ss=ss; self.ws=ws; self.dest=dest; self.addr=addr
		Thread(target=self._run).start()

	def _run(self):
		while self.ss.qb.en:
			try:
				ev = json.loads(self.ws.recv(.5))
				if ev[0]!='ACK' and ev[0]!='NACK':
					try:
						r = self.ss.ev(ev[0], self, *ev[2:])
						if isinstance(r, Coroutine):
							asyncio.run_coroutine_threadsafe(self._ioEv(ev,r), self.ss.loop)
						else: self._ack(ev,r)
					except Exception as e: self._ack(ev,None,e)
			except TimeoutError: pass
			except ConnectionClosed:
				self.ss.cliList.remove(self)
				self.ss.ev('disconnect', self)
				return
			except Exception as e: err("IO "+eInfo(e))
		self.ws.close()

	async def _ioEv(self, ev, cr):
		try: self._ack(ev, await cr)
		except Exception as e: self._ack(ev, None, e)

	def _ack(self, ev, r, er=None):
		self.ws.send(json.dumps(['NACK' if er else 'ACK', ev[1], eInfo(er) if er else r]))
		if er: msg(C.Red+eInfo(er))

	def emit(self, ev, *args):
		self.ws.send(json.dumps([ev,self.ss.mid,*args]))
		self.ss.mid += 1
		if self.ss.mid > MSG_ID_MAX: self.ss.mid=0
		#TODO Wait for ack and return asyncio Coroutine, or have a variant of emit that does