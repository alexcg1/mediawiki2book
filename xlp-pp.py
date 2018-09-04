#!/usr/bin/env python3

import argparse
import os
import io

# Set up arguments
parser = argparse.ArgumentParser(description="Convert MediaWiki files to other formats")
parser.add_argument("filename", help="The MediaWiki file you want to convert")
args = parser.parse_args()

input_file = args.filename

# Safely read the input filename using 'with'
with open(input_file) as f:
	s = f.read()
	# Get input file language
	# try:
	# 	lang = detect(s)
	# 	print("* Detecting language..............................................", end="", flush=True)
	# 	print("[ ",lang, " ]")
	# except:
	# 	pass

with open(input_file, 'w') as f:
	print("* Removing wiki-only stuff........................................", end="", flush=True)
	s = s.replace("= Before Reading =", "")
	s = s.replace("= References =", "")
	f.write(s)

f.close()
