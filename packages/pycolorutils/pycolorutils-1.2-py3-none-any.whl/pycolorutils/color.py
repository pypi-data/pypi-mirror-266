#PyColorUtils; GNU GPL v3

import sys, os, atexit as ae
from traceback import print_exception

class C:
	Rst='\x1b[0m' #Reset
	Br='\x1b[1m' #Bright
	Di='\x1b[2m' #Dim
	Un='\x1b[4m' #Underscore
	Bl='\x1b[5m' #Blink
	Rv='\x1b[7m' #Reverse

	Blk='\x1b[30m' #Black
	Red='\x1b[31m' #Red
	Grn='\x1b[32m' #Green
	Ylo='\x1b[33m' #Yellow
	Blu='\x1b[34m' #Blue
	Mag='\x1b[35m' #Magenta
	Cya='\x1b[36m' #Cyan
	Whi='\x1b[37m' #White

	BgBlk='\x1b[40m' #BgBlack
	BgRed='\x1b[41m' #BgRed
	BgGrn='\x1b[42m' #BgGreen
	BgYlo='\x1b[43m' #BgYellow
	BgBlu='\x1b[44m' #BgBlue
	BgMag='\x1b[45m' #BgMagenta
	BgCya='\x1b[46m' #BgCyan
	BgWhi='\x1b[47m' #BgWhite
	onErr = onMsg = None #Callback

_Ex = []

def msg(*a):
	a=list(a); n=len(a)-1
	if isinstance(a[n], str): a[n]+=C.Rst+'\n'
	else: a.append(C.Rst+'\n')
	a=' '.join(a)
	sys.stdout.write(a)
	if C.onMsg: C.onMsg(a)

def err(e,ex=0):
	e=C.Rst+C.Red+e+C.Rst+'\n'
	sys.stderr.write(e)
	if C.onErr: C.onErr(e)
	if ex: sys.exit(ex)

def exitClean():
	for f in _Ex: f()
	_Ex.clear()

def atexit(f): _Ex.append(f)
ae.register(exitClean)

def execMain(main):
	try: main()
	except KeyboardInterrupt: pass
	except Exception as er: print_exception(er)
	exitClean()

def eInfo(e: Exception):
	tb=e.__traceback__
	while tb.tb_next: tb=tb.tb_next
	fn = os.path.split(tb.tb_frame.f_code.co_filename)[1]
	return f"{type(e).__name__} @ {fn}:{tb.tb_lineno}: {e}"