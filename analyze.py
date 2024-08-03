#!/QOpenSys/pkgs/bin/python3.9

# to try this out:
# python analyze.py --host MY_IBM_I  --liblist QGPL,QUSRSYS --pgm hello --source QGPL/QRPGLESRC  --out cst.json 
# python analyze.py --host MY_IBM_I  --liblist FAXUDVDB,FAXUDV,FAXUDV2924,AINCLUDE --pgm fax100 --source faxudv/qsrc  --out cst.json 


import argparse, sys, os, subprocess, re, json 


# ------------------------------------------------------------------------
def set_state (text , state ):
		
	text = text.strip()
	#print(text) 	
	if 	text == 'Global Field References:':
		return 'symbols'
	elif text == 'File and Record References:':
		return 'files'
	elif text == 'Indicator References:':
		return 'indicators'
	elif text == 'Statically bound procedures:':
		return 'procs'
	elif text == 'Imported fields:':
		return 'imports'
	elif text == 'Exported fields:':
		return 'exports'
	else: 
		return state 
		

# ------------------------------------------------------------------------
# Just for now, stack symbol_tables as they are
# ------------------------------------------------------------------------
def push_symbol_table (symbol_table , ln):
	#print (ln)
	if ln[0:10].strip() == '' and ln.strip() != 'Field             Attributes         References (D=Defined M=Modified)':
		if ln[0:48].strip() != '':
			symbol  = {
				'name'     : ln[10:28].rstrip(),
				'dataType' : ln[28:44].rstrip(),
				'usage'    : ln[48:999].strip() 
			}
			symbol_table.append(symbol)
		else:
			symbol = symbol_table[-1]
			symbol['usage'] = symbol['usage'] + ' ' + ln[48:999].strip()

# ------------------------------------------------------------------------
# Just for now, stack symbol_tables as they are
# ------------------------------------------------------------------------
def push_code_table (code_table, ln):
	if ln[123:129].strip().isdigit():
		print (ln)
		code  = {
			'line'     : ln[0:7].strip(),
			'code'     : ln[7:110].rstrip()
		}
		if ln[123:124].strip().isdigit():
			code['segment'] = ln[123:124].strip()

		code_table.append(code)

# ------------------------------------------------------------------------
# Execute the compound script againt the IBM i
# ------------------------------------------------------------------------
def run_script(host, out, cmd ):
	shell = "ssh -T " + host + " '/QOpenSys/usr/bin/qsh -c \"\n" + cmd  + "\"'"
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
	state = 'code'
	symbol_table= []
	code_table= []

	f = open("postlist.txt", "w")
	for ln in proc.stdout:
		ln = ln.rstrip()
		print (ln, file=f)
		state = set_state ( ln , state)

		if 	 state =='code':
			push_code_table (code_table , ln)
		elif state == 'symbols':
			push_symbol_table (symbol_table , ln)
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

	f.close()

	# produce output:
	with open(out, "w") as outfile: 
		cst  = {
			'code'        : code_table,
			'symbolTable' : symbol_table,
		}
		json.dump(cst, outfile)

	# Format messages
	for ln in proc.stderr:
		ln = ln.rstrip()
		print (ln)

	return True if proc.wait() == 0 else False

# ------------------------------------------------------------------------
# Build compile comand on the IBM i 
# using qsh to run system form bash ( to set library list) 
# ------------------------------------------------------------------------
def run_cmd (cmd):
	wrkcmd = cmd.replace("'", "'\\''") .replace("\"" , "\\\"")
	wrkcmd = "system -vK \\\"" + wrkcmd  + "\\\""
	return wrkcmd

# ------------------------------------------------------------------------
# only qsh on older system allow setting the library list ( bash now does)
# ------------------------------------------------------------------------
def set_library_list ( liblist):
	libs = liblist.split(",")
	retval = ''
	for lib in libs :
		retval += "liblist -af " + lib + ";\n"
	# retval += "liblist > /tmp/libllist.txt;\n"
	return retval

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

run_script ( host, out, 
	set_library_list ( liblist) + 
	run_cmd ("CRTBNDRPG PGM(QTEMP/" + pgm + ") SRCFILE(" + source + ") SRCMBR(" +pgm +") REPLACE(*yes) OPTION(*XREF *NOGEN *SHOWCPY *EXPDDS *NOSHOWSKP *NOUNREF)")
)


ok = True
sys.exit ( 0 if ok else 1)
