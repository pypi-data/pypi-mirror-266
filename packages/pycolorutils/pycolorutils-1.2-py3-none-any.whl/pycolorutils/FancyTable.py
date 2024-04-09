#PyColorUtils - Fancy Table Printing; GNU GPL v3

import re
from .color import *

def _contains(arr, itm):
	if not arr: return
	try: arr.index(itm)
	except ValueError: return False
	return True

_ANSI_REX = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
def _slen(s: str):
	return len(_ANSI_REX.sub('',s))

#Draw Separator, ex +------+
def _sep(width: int, div: list=None, sep: str='-', clr=''):
	n = width-1
	print(clr, end='')
	for i in range(width):
		print('+' if not i or i==n or _contains(div, i) else sep, end='')
	print(C.Rst)

#Draw Centered Text, ex | text |
def _center(s: str, width: int, end: bool=True, clr=''):
	vs = clr+'|'+C.Rst
	sl = _slen(s)
	if sl > width-2: s=s[:width-2+len(s)-sl]; sl=width-2
	width -= sl+2
	w2=width//2; n=w2+1 if width%2 else w2
	print(vs+(' '*n)+s+(' '*w2), end='') #Start + Spacer + Text + Spacer
	if end: print(vs) #End

#Render Fancy Table
def table(title: str, width: int, colNames: list[str], data: list[list[str]], color: str=None):
	#Calc Col Width
	cNum = len(colNames); cSum=0; cnS1 = cNum-1
	for c in colNames: cSum += _slen(c)
	cPad = ((width-cSum)//cNum)+1 #Padding for each col
	cEnd = width-cSum-(cPad-1)*cnS1 #Padding offset for last col

	#Col Pos Array (to add extra '+'s for a lil extra flare)
	cPos=[]; cSum=0
	for i in range(cnS1):
		cSum += _slen(colNames[i])+cPad-1
		cPos.append(cSum)

	#Draw Title
	_sep(width, clr=color)
	_center(title, width, clr=color)
	_sep(width, cPos, clr=color)

	#Draw Col Headings
	for i, c in enumerate(colNames):
		c = C.Br+c
		if i==cnS1: _center(c, _slen(c)+cEnd, clr=color)
		else: _center(c, _slen(c)+cPad, False, color)
	_sep(width, cPos, '=', color)

	#Draw Data Rows
	for row in data:
		for i, s in enumerate(row):
			c = colNames[i]
			if i==cnS1: _center(s, _slen(c)+cEnd, clr=color)
			else: _center(s, _slen(c)+cPad, False, color)
	_sep(width, cPos, clr=color)