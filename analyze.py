#!/QOpenSys/pkgs/bin/python3.9

# to try this out:
# python analyze.py --input fax100.extract.json --output fax100.analyze.json


import argparse, sys, os, subprocess, re, json 


# ------------------------------------------------------------------------
# Lookup for kan key value pair
# ------------------------------------------------------------------------
def locate (lists , key , value):
	for i in lists:
		try: 
			print ('>' + i[key] + '<')
			print ('>' + value  + '<')
			if i[key] == value:
				return  i
		except:
			k = 0

	return None

# ------------------------------------------------------------------------
# build the C-spec as dict
#L0N01Factor1+++++++Opcode&ExtFactor2+++++++Result++++++++Len++D+HiLoEq....Comments 
def build_c_spec(source): 	

	c_spec = {}
	
	code = source['code']

	c_spec['line'] = source['line']
	if  code[21:26].strip():
		c_spec[	'opcode'    ] =  code[21:27].strip().lower()   
	if  code[28:30].strip():
		c_spec[	'extension' ] =  code[28:30].strip()   
	if  code[7:20].strip():
		c_spec[	'fac1'      ] =  code[7:20].strip()     
	if  code[31:44].strip():
		c_spec[	'fac2'      ] =  code[31:44].strip()   
	if  code[45:58].strip():
		c_spec[	'result'    ] =  code[45:58].strip()   
	if  code[59:63].strip():
		c_spec[	'length'    ] =  code[59:63].strip()   
	if  code[64:65].strip():
		c_spec[	'pprec'     ] =  code[64:65].strip()   
	if  code[66:68].strip() and code[66:68].strip() != '--':
		c_spec[	'hi'        ] =  code[66:68].strip()   
	if  code[68:70].strip() and code[68:70].strip() != '--':
		c_spec[	'lo'        ] =  code[68:70].strip()   
	if  code[70:72].strip() and code[70:72].strip() != '--':
		c_spec[	'eq'        ] =  code[70:72].strip()   
	if  code[76:89].strip():
		c_spec[	'comments'  ] =  code[76:98].strip()  
	c_spec['source'] = code

	return c_spec

# ------------------------------------------------------------------------
# build - based an the extraction 
# ------------------------------------------------------------------------
def run_analyze (input_file_name , output_file_name ):

	print(output_file_name)

	# Openand load JSON file
	input_file = open(input_file_name)
	extract = json.load(input_file)
	input_file.close()

	c_specs = []
	symbol_table = []

	# Load dicts from graph 
	for source in extract['source']:
		code = source['code']
		if   code[1:2].upper() == 'C' and code[2:3] != '*':
			c_specs.append(build_c_spec(source))

	for symbol in extract['symbolTable']:
		symbol_table.append(symbol)

	produce_cst( c_specs , symbol_table , output_file_name)

# ------------------------------------------------------------------------
def lookup_symbol_table(symbol_table, symbol):
	for i in symbol_table:
		if i['name'] == symbol:
			return  i['dataType']

	return ''


# ------------------------------------------------------------------------
def produce_interface(c_specs , symbol_table):

	interface = []
	step = 1
	for i in c_specs:
		try: 
			if step == 1 and i['fac1'] == '*ENTRY':
				step = 2
			elif step == 2 and i['opcode'] == 'parm':
				name = i['result']
				parm = {
					'name' : name,
					'type' : lookup_symbol_table(symbol_table , name)
				}
				interface.append(parm)
			elif step == 2:
				break
		except:
			k=0 
	return interface
# ------------------------------------------------------------------------
def produce_interfaces(c_specs , symbol_table):

	interfaces = []
	parms = []
	name = ''
	for i in c_specs:
		try: 
			if i['opcode'] == 'parm':
				parm_name = i['result']
				parm = {
					'name' : parm_name,
					'type' : lookup_symbol_table(symbol_table , parm_name)
				}
				parms.append(parm)
			else:
				if name != '':
					interface = {
						'name' : name,
						'parm' : parms
					}
					interfaces.append(interface)
					name = ''
				if i['opcode'] == 'plist':
					name = i['fac1']
				parms = []
		except:
			pass 
	return interfaces
# ------------------------------------------------------------------------
def produce_code(c_specs , symbol_table):

	code = []

	start = 0
	for i in range(len(c_specs)):
		obj = c_specs[i]
		print (obj)
		if obj['opcode'] != 'plist' and obj['opcode'] != 'parm':
			start = i
			break
	print (start)

	return code

# ------------------------------------------------------------------------
def dump (dict):

	with open('dump.json', "w") as outfile: 
		json.dump(dict, outfile)


# ------------------------------------------------------------------------
def produce_cst ( c_specs , symbol_table , output_file_name):

	dump (c_specs)
	cst = {
		'program' : 'TODO directives',
		'interface' : produce_interfaces(c_specs , symbol_table),
		'main' : produce_code (c_specs , symbol_table)
	}

	with open(output_file_name, "w") as outfile: 
		json.dump(cst, outfile)

# ------------------------------------------------------------------------
# Main line
# ------------------------------------------------------------------------
parser=argparse.ArgumentParser()
parser.add_argument('--input', help='Input JSON')
parser.add_argument('--output', help='Output JSON')
args=parser.parse_args()

input_file = args.input
output_file = args.output  

if output_file == None:
	output_file = args.input.replace('.extract.json' , '.analyze.json' )

#print args
#print sys

run_analyze  ( input_file , output_file) 


ok = True
sys.exit ( 0 if ok else 1)
