#!/QOpenSys/pkgs/bin/python3.9

# to try this out:
# python analyze.py --host dksrv206  --pgm hello --source NLI/QSRC --out cst.json

import argparse, sys, os, subprocess, re, json 


# ------------------------------------------------------------------------
def setState (text , state ):
		
	if 	text == '       Global Field References:':
		state = 'globals'
	elif text == '       File and Record References:':
		state = 'files'
	elif text == '       Indicator References:':
		state = 'indicators'
	elif text == '       Statically bound procedures:':
		state = 'procs'
	elif text == '       Imported fields:':
		state = 'imports'
	elif text == '       Exported fields:':
		state = 'exports'
		
	return state

def pushGlobals (globalVar , ln):
	if ln[0:10] == '          ' and ln != '          Field             Attributes         References (D=Defined M=Modified)':
		var  = {
			'name'     : ln[10:28].rstrip(),
			'dataType' :  ln[28:44].rstrip(),
			'usage'    : ln[52:999].rstrip() 
		}
		globalVar.append(var)
		

# ------------------------------------------------------------------------
# Execute the compound script againt the IBM i
# ------------------------------------------------------------------------
def runscript(host, out, cmd ):
	shell = "ssh -t " + host + " '/QOpenSys/usr/bin/qsh -c \"" + cmd  + "\"'"
	print (shell)
	proc = subprocess.Popen(shell,
		shell=True,
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		universal_newlines=True,
		encoding='latin-1'
	)

	# Format messages
	for ln in proc.stderr:
		ln = ln.rstrip()
		print (ln)

	# Format messages
	state = 'code'
	globalVar= []
	for ln in proc.stdout:
		ln = ln.rstrip()
		state = setState ( ln , state)

		if 	 state =='code':
			pass
		elif state == 'globals':
			pushGlobals (globalVar , ln)
		elif state == 'files':
			pass
		elif state == 'indicators':
			pass
		elif state == 'procs':
			pass
		elif state == 'imports':
			pass
		elif state == 'exports':
			pass

# produce output:
	with open(out, "w") as outfile: 
		json.dump(globalVar, outfile)


	return True if proc.wait() == 0 else False


# ------------------------------------------------------------------------
# Build compile comand on the IBM i 
# using qsh to run system form bash ( to set library list) 
# ------------------------------------------------------------------------
def runcmd (cmd):
	wrkcmd = cmd.replace("'", "'\\''") .replace("\"" , "\\\"")
	wrkcmd = "system -vK \\\"" + wrkcmd  + "\\\""
	return wrkcmd

# ------------------------------------------------------------------------
# Main line
# ------------------------------------------------------------------------
parser=argparse.ArgumentParser()
parser.add_argument('--host', help='IBM i host to connect to')
parser.add_argument('--pgm', help='Program (member) to compile and anlyse')
parser.add_argument('--stmf', help='Source stream file')
parser.add_argument('--liblist', help='library lists')
parser.add_argument('--source', help='source lib/filename')
parser.add_argument('--out', help='Output JSON ')
args=parser.parse_args()

host = args.host
pgm = args.pgm
stmf = args.stmf
liblist = args.liblist
source = args.source
out = args.out

#print args
#print sys

runscript ( host, out, runcmd ("CRTBNDRPG PGM(QTEMP/" + pgm + ") SRCFILE(" + source + ") SRCMBR(" +pgm +") REPLACE(*yes) OPTION(*XREF *NOGEN *SHOWCPY *EXPDDS *NOSHOWSKP *NOUNREF)"))


ok = True
sys.exit ( 0 if ok else 1)
