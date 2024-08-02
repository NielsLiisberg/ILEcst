#!/QOpenSys/pkgs/bin/python3.9

import argparse, sys, os, subprocess, re


# ------------------------------------------------------------------------
# Execute the compound script againt the IBM i
# ------------------------------------------------------------------------

def runscript(host, cmd ):
	i=0
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
	for ln in proc.stdout:
		ln = ln.rstrip()
		print (ln)

	return True if proc.wait() == 0 else False


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
parser.add_argument('--lib' , help='Object library')
parser.add_argument('--liblist', help='library lists')
parser.add_argument('--source', help='source lib/filename')
parser.add_argument('--out', help='Output JSON ')
args=parser.parse_args()

host = args.host
pgm = args.pgm
stmf = args.stmf
lib = args.lib
liblist = args.liblist
source = args.source
out = args.out

#print args
#print sys


lib = lib.upper() if lib else ""

runscript ( host, runcmd ("CRTBNDRPG PGM(NLI/HELLO) SRCFILE(NLI/QSRC) SRCMBR(HELLO) REPLACE(*yes) OPTION(*XREF *NOGEN *SHOWCPY *EXPDDS *NOSHOWSKP *NOUNREF)"))


ok = True
sys.exit ( 0 if ok else 1)
