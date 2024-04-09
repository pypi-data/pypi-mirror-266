#PyColorUtils; GNU GPL v3

from threading import Thread, Lock
from time import sleep
from .color import *

WIN=True; _Attr=None
try: import msvcrt #Windows
except ImportError: #Linux
	import termios, os
	WIN=False
	_Attr = termios.tcgetattr(sys.stdin); _na = _Attr.copy()
	_na[3] = _na[3] & ~(termios.ECHO | termios.ICANON)
	_na[6][termios.VMIN] = _na[6][termios.VTIME] = 0
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, _na)

_Run = True
_Sub = _Read = None
_Prev = []
SP=' '; CR='\r'; LF='\n'
DELAY=.05

def flushStdin():
	if WIN: #Windows
		while msvcrt.kbhit(): msvcrt.getch()
	else: #Linux
		termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def echo(s):
	print(s, end='', flush=True)

def _getKey(f=False):
	if WIN: #Windows
		if f or msvcrt.kbhit(): return msvcrt.getwche()
	else: return os.read(sys.stdin.fileno(), 1).decode() #Linux

class InputReader:
	def __init__(self, pStr):
		echo(pStr)
		self.lock = Lock(); self._ps = pStr
		self.msg = self._st = self._sm = None

	def _run(self):
		global _Read
		with self.lock:
			self._input()
			if self.msg and not self._sm:
				_Prev.append(self.msg)
			_Read = None

	def _draw(self, ln, pos, rl=None):
		if rl is not None: rs = CR+SP*(len(self._ps)+rl+1)
		else: rs = '\b'+SP
		echo(rs+CR+self._ps+ln+'\b'*(len(ln)-pos))

	def _input(self):
		ln = ''; pos = 0; hm = len(_Prev); idx = hm
		while _Run and not self._st:
			while True:
				c = _getKey()
				if not c: break
				if c == '\003': raise KeyboardInterrupt
				if c in (CR,LF): #Enter
					print(); self.msg=ln; return
				elif c == '\b' or c == '\x7f': #Back
					if pos > 0: ln = ln[:pos-1]+ln[pos:]; pos -= 1
					self._draw(ln, pos, len(ln))
				elif c == '\xe0' or c == '\x1b': #Special
					if not WIN: _getKey(True)
					if WIN and c == '\x1b': d=None
					else: d= _getKey(True)
					rl=None
					if d == ('K' if WIN else 'D'): #Left
						if pos > 0: pos -= 1
					elif d == ('M' if WIN else 'C'): #Right
						if pos < len(ln): pos += 1
					elif d == ('H' if WIN else 'A') and hm: #Up
						rl=len(ln)
						if idx > 0: idx -= 1
						ln = _Prev[idx]; pos = len(ln)
					elif d == ('P' if WIN else 'B'): #Down
						rl=len(ln)
						if idx < hm: idx += 1
						ln = '' if idx == hm else _Prev[idx]; pos=len(ln)
					elif d == ('G' if WIN else 'H'): pos=0 #Home
					elif d == ('O' if WIN else 'F'): pos=len(ln) #End
					elif WIN and d == 'S' and pos < len(ln): #Del
						rl=len(ln); ln=ln[:pos]+ln[pos+1:]
					elif not d: rl=len(ln)+50; ln=''; pos=0
					self._draw(ln, pos, rl)
				else:
					ln=ln[:pos]+c+ln[pos:]; pos+=1
					self._draw(ln, pos)
			sleep(DELAY)

	def setMsg(self, m: str):
		self.msg = m; self._sm = True
		self.stop()

	def wait(self):
		with self.lock: return self.msg

	def stop(self):
		self._st = True; self.wait()

def _reader():
	while _Run:
		if _Read: _Read._run()
		else: sleep(DELAY)

def read(pStr=""):
	global _Sub, _Read
	if not _Run: raise IOError
	if not _Sub or not _Sub.is_alive():
		_Sub = Thread(target=_reader, name='Reader'); _Sub.start()
	if _Read: _Read.stop()

	flushStdin()
	while True:
		_Read = InputReader(pStr)
		while _Read and not _Read.lock.locked(): sleep(DELAY)
		if _Read: return _Read
		sleep(.5) #Retry

def ex():
	global _Run
	_Run = False
	if _Attr: termios.tcsetattr(sys.stdin, termios.TCSADRAIN, _Attr)

atexit(ex)