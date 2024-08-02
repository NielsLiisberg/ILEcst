#!/QOpenSys/pkgs/bin/python3.9

import argparse, sys, os, subprocess, re


# ------------------------------------------------------------------------
# Execute the compound script againt the IBM i
# ------------------------------------------------------------------------

def runscript(host, cmd ):
	##print (shell)
	i=0
	shell = "ssh -t " + host + "/QOpenSys/usr/bin/qsh -c '" + cmd  + "'"
	proc = subprocess.Popen(shell,
		shell=True,
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		universal_newlines=True,
		encoding='latin-1'
	)

	# Format messages
	for ln in proc.stdout:
		ln = ln.rstrip()
			print (ln) '{stmf}:{line}:{col}:{sev}:{msg}'.format(
				stmf  = stmf,
				sev   = 'info',
				msg   = ln,
				line  = 0,
				col   = i
			))

	return True if proc.wait() == 0 else False

# ------------------------------------------------------------------------
# Format the data from the EVENTF
#peek from
#ERROR      1 001 1 000003 000003 005 000003 005 CZM0045 S 30 024 Undeclared identifier i.
#ERROR      0 001 1 000020 000020 000 000020 000 CPD0791 I 00 116 No labels used in program.

def showEventFile (lib , obj):
	shell = oscmd ("/QOpenSys/usr/bin/iconv -f IBM-277 -t ISO8859-1 /QSYS.LIB/" + lib + ".LIB/EVFEVENT.FILE/" + obj + ".MBR  | /QOpenSys/pkgs/bin/sed -E 's/ERROR|FILEEND|EXPANSION/\r&/g'")
	shell = "/QOpenSys/usr/bin/bsh -c '" + shell + "'"
	proc = subprocess.Popen(shell,
		shell=True,
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		universal_newlines=True,
		encoding='latin-1'
	)

	#ln = proc.stdout.read(400)
	#while ln:
	for ln in proc.stdout:
		ln = ln.rstrip()
		msgid = ln[48:55]
		if ln[0:5] == 'ERROR' and msgid not in ['RNF7031', 'RNF7503', 'RNF7534' , 'RNF5409']:
			print ('{stmf}:{line}:{col}:{sev}:{msgid}:{msgtext}'.format(
				stmf  = stmf,
				sev   = ('info' if ln[56:57] in ["I" , "W"] else 'error'),
				msgid = msgid,
				msgtext = ln[65:9999],
				line  = ln[37:43],
				col   = ln[44:47]
			))
		#ln = proc.stdout.read(400)



def runandshow (shell):
	shell = "/QOpenSys/usr/bin/qsh -c '" + shell + "'"
	proc = subprocess.Popen(shell,
		shell=True,
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		universal_newlines=True,
		encoding='latin-1'
	)

	for ln in proc.stdout:
		ln = ln.rstrip()

		# TODO !! Strip the absolute path from the response
		print(re.sub("^" + os.getcwd().lower() + "/" , "", ln))

	for ln in proc.stderr:
		#		ln = ln.rstrip().decode("latin-1", errors="ignore").encode()
		#		print(str.encode(ln.rstrip() , encoding="Windows-1252",errors="ignore"))
		ln = ln.rstrip()

	return True if proc.wait() == 0 else False


def syscmd(cmd):
	wrkcmd = "system -vK \"" + cmd.replace("'", "'\\''") + "\";\n"
	return wrkcmd

def syscmdlist(cmd):
	print (cmd)
	wrkcmd = oscmd("touch postlist.txt")
	wrkcmd += oscmd("setccsid 1208 postlist.txt")
	wrkcmd += "system -vK \"" + cmd.replace("'", "'\\''") + "\" > postlist.txt;\n"
	return wrkcmd

def oscmd (cmd):
	wrkcmd = cmd.replace("'", "'\\''") .replace("\"" , "\\\"")+ ";\n"
	return wrkcmd

def pick_up_flags(stmf):
	f = open(stmf)
	for i in range(5):
		line = f.readline()
		if line.find("CMD:") >= 0:
			break
	f.close()
	# picup parameter if it has a CMD: annotation.two components: the compiler command its parameters
	options = re.search("CMD:([^\s]+)?(?:\s*)(.*\))?", line)
	cmd = "" if options == None or options.group(1) == None else  options.group(1)
	extflags = "" if options == None or options.group(2) == None else  options.group(2)
	return  cmd, extflags

def split_names_with_blanks (inp):
    temp = inp.split (".")
    ext = temp[1].lower() if len(temp) >= 2 else ""
    temp = temp[0].split (" ")
    name = temp[0].upper()
    text  = ' '.join(temp[1::])
    return name , text , ext

def split_names (inp):
    temp = inp.split (".")
    ext = temp[1].lower() if len(temp) >= 2 else ""
    temp = temp[0].split ("-")  ## TODO when git extract changes to - as delimiter
    ##temp = temp[0].split ("_")
    name = temp[0].upper()
    text  = ' '.join(temp[1::])
    return name , text , ext


def object_name_only(inp):
	if inp is None:
		return ""
	objs = inp.split (" ")

	for i in range(len(objs)):
		objs[i] = "(" + objs[i].split('_')[0] + ")"

	result = ' '.join(objs)
	return result

def	copy_from_stmf (stmf, lib , obj, srcf):
	shell  =  oscmd("setccsid 1208 " + stmf)
	shell += syscmd("CRTSRCPF FILE(" + lib + "/" + srcf + ") RCDLEN(200)")
	shell += syscmd("CPYFRMSTMF FROMSTMF('" + stmf + "') TOMBR('/QSYS.lib/" + lib + ".lib/" + srcf + ".file/" + obj + ".mbr') MBROPT(*replace)")
	return shell

def srcfile (lib , file):
	return 	" SRCFILE(" + lib + "/" +  file + ") "

def set_library_list ( liblist):
	libs = liblist.split(" ")
	retval = ''
	for i in range(len(libs)):
		retval += "liblist -af " + libs[-i -1] + ";\n"
	retval += "liblist > /tmp/libllist.txt;\n"
	return retval

def find_source_file_name (stmf , default):
	elem = stmf.split("/")
	if len(elem) < 2:
		return default
	filename = elem[len(elem)-2]
	if filename [0:1].lower() == 'q':
		return filename
	return default

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


if   ext == 'c':
	ok = build_c (stmf , cmd ,lib,  liblist , obj , flags , include, text)
elif ext == 'rpg':
	ok = build_rpg (stmf , cmd ,lib, liblist , obj , flags , include, text)
elif ext == 'rpgle':
	ok = build_rpgle (stmf , cmd ,lib, liblist , obj , flags , include, text)
elif ext == 'sqlrpgle':
	ok = build_sqlrpgle (stmf , cmd ,lib, liblist , obj , flags , include, text)
elif ext == 'clle':
	ok = build_clle (stmf , cmd ,lib , liblist ,obj , flags , include, text)
elif ext == 'clp':
	ok = build_clp (stmf , cmd ,lib , liblist ,obj , flags , include, text)
elif ext == 'cmd':
	ok = build_cmd (stmf , cmd ,lib , liblist ,obj , flags , include, text)
elif ext == 'dspf':
	ok = build_dspf (stmf , cmd ,lib , liblist ,obj , flags , include, text)
elif ext == 'prtf':
	ok = build_prtf (stmf , cmd ,lib , liblist ,obj , flags , include, text)
elif ext == 'pf':
	ok = build_pf (stmf , cmd ,lib , liblist ,obj , flags , include, text)
elif ext == 'lf':
	ok = build_lf (stmf , cmd ,lib , liblist ,obj , flags , include, text)
elif ext == 'menu':
	ok = build_menu (stmf , cmd ,lib , liblist ,obj , flags , include, text)
elif ext == 'pnlgrp':
	ok = build_pnlgrp (stmf , cmd ,lib , liblist ,obj , flags , include, text)
elif ext == 'sql':
	ok = build_sql (stmf , cmd ,lib , liblist ,obj , flags , include, text)
elif ext == 'pgm':
	ok = build_pgm (stmf , cmd ,lib , liblist ,obj , flags , include, text, modules)
elif ext == 'srvpgm':
	ok = build_srvpgm (stmf , cmd ,lib , liblist ,obj , flags , include, text, modules)
elif ext == 'srvsrc':
	ok = build_srvsrc (stmf , cmd ,lib , liblist ,obj , flags , include, text, modules)
else:
	print ("no compiler for " + ext)

sys.exit ( 0 if ok else 1)
