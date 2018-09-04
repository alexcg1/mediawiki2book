#!/usr/bin/env python3

import argparse
from subprocess import call
import os
import shutil
from datetime import date, datetime, time
from babel.dates import format_date
import tempfile
import sys
from pathlib import Path

# I'd like to have automatic language detection. However when it reads a mediawiki file it just says it's "en"
# try:
# 	from langdetect import detect
# 	print("* Language detection enabled")
# except:
# 	print("* To detect file language, please install langdetect python module")

#### These are the main things you may want to edit! ####

buildsystem_dir = os.getcwd()
resources_dir = buildsystem_dir+"/resources"
images_dir = buildsystem_dir+"/images/"

#########################################################

class bcolors:
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

ok_text = bcolors.OKGREEN + "[ DONE ]" + bcolors.ENDC
warning_text = bcolors.WARNING + "[ WARNING ]" + bcolors.ENDC
warnings = []
fail_text = bcolors.FAIL + "[ FAIL ]" + bcolors.ENDC

# Set up arguments
parser = argparse.ArgumentParser(description="Convert MediaWiki files to other formats")
parser.add_argument("filename", help="The MediaWiki file you want to convert")
parser.add_argument("--debug", action='store_true', default=False, help="Keep temporary files for debugging purposes and give verbose output")
parser.add_argument("--veryverbose", action='store_true', default=False, help="Turn on Pandoc's verbose output")
parser.add_argument("-t", "--to", default="pdf", help="Format you want to export to. Accepts any format accepted by pandoc. Default is PDF") # Untested!
parser.add_argument("--type", default="book", choices=["article", "book"], help="What type of document you want. Books are separated and numbered by chapter, and have larger inner margins")
parser.add_argument("--lang", default="en", help="Set language, e.g. zh or en")
args = parser.parse_args()

def cjkcheck():
	global header_date
	if args.lang == "zh":
		# header_cjkfont = "Noto Sans CJK SC Regular"
		header_date = format_date(datetime.today(), locale='zh_CN')
	# elif args.lang == "kr":
	# 	header_cjkfont = "Noto Sans CJK KR Regular"
	# elif args.lang == "jp":
	# 	header_cjkfont = "Noto Sans CJK JP Regular"
	else:
		header_date = format_date(datetime.today(), locale='en_US')

## Define important variables
output_format = args.to
pandoc = "/usr/bin/pandoc"

input_file = args.filename
md_file = input_file.replace("mediawiki", "md")
output_file = input_file.replace("mediawiki", output_format)

if args.type == "article":
	template = "eisvogel" # This is the base eisvogel template
else:
	template = "firevogel" # Default option - suited to books

########## Deal with images (which should already be on your machine)

with tempfile.TemporaryDirectory() as temp_dir:  
	print("* Creating temp directory",temp_dir,"and copying images.....", end="", flush=True)

try:
	shutil.copytree(images_dir, temp_dir)
	print(ok_text)
except:
	print(warning_text)
	print("Failed to copy images. Are you sure you have some?")
	print("Creating temp directory anyway")
	os.mkdir(temp_dir)



########## Deal with the raw mediawiki file

# Remove references section - they're all converted to footnotes anyway, so we don't need the title for an empty section

# # Safely read the input filename using 'with'
# with open(input_file) as f:
# 	s = f.read()
# 	# Get input file language
# 	# try:
# 	# 	lang = detect(s)
# 	# 	print("* Detecting language..............................................", end="", flush=True)
# 	# 	print("[ ",lang, " ]")
# 	# except:
# 	# 	pass
# 
# with open(input_file, 'w') as f:
# 	print("* Removing wiki-only stuff........................................", end="", flush=True)
# 	s = s.replace("= Before Reading =", "")
# 	s = s.replace("= References =", "")
# 	f.write(s)
# 
# f.close()
# 
# print(ok_text)
# 
# ############# Now we can convert to Markdown

print("* Converting to MarkDown for pre-processing.......................", end="", flush=True)
call(["pandoc", "--from=mediawiki", input_file, "-t", "markdown", "-o", temp_dir+"/"+md_file])
print(ok_text)

print("* Changing to temp directory......................................", end="", flush=True)
os.chdir(temp_dir)
print(ok_text)

### Add YAML header

cjkcheck() # Check if CJK or not

header_file = resources_dir+"/header.yaml"

if Path(header_file).is_file():
	print("* Adding metadata header..........................................", end="", flush=True)
	header = open(header_file, "r").read() # header file to string
	header = header.replace("$DATE", header_date)

	if args.lang == "zh":
		header = header.split("---")[1]
		header = "---"+header+"mainfont: Noto Sans Mono CJK SC Regular\n---"

	# Prepend to markdown file
	with open(md_file, 'r') as original: data = original.read()
	with open(md_file, 'w') as modified: modified.write(header + "\n" + data)

	print(ok_text)

else:
	print("* No metadata header found....................................", end="", flush=True)
	print(warning_text)
	warnings.append("No header.yaml\nWe couldn't find header.yaml in your resources directory. This means that a nice cover and title/author info may be missing from your PDF")

# Convert to output (default pdf)
print("* Converting to", output_format, "(this may take a while).......................", end="", flush=True)

pandoc_args = [
	md_file,
	"-o",						# Sets output filename
	buildsystem_dir+"/"+output_file,
	"--toc", 					# Table of contents
	"--template="+template,		# Firevogel by default for books
	"--listings", 				# Make code blocks stay in page and look nice
	"--pdf-engine=xelatex", 	# Works better with CJK
	"--toc-depth=3", 			# Depth of page of contents
	"--data-dir="+resources_dir,# Looks for templates in ./resources
	"-V lang="+args.lang
	]

if args.type == "book":
	pandoc_args.append("--top-level-division=chapter")

if args.veryverbose:
	pandoc_args.append("--verbose")

pandoc_command = [pandoc]
pandoc_command.extend(pandoc_args) # Add arguments to the command

if args.debug:
	print("\n")
	print("-- DEBUG INFORMATION ------------------------------------------\n")
	print("* Working directory: 	",buildsystem_dir)
	print("* Input file: 		",input_file)
	print("* Intermediate file: 	",md_file)
	print("* YAML header: 		",header_file)
	print("* Output file: 		",output_file)
	print("* Language: 			",args.lang)
	print("* Book or article: 	",args.type)
	print("* Pandoc command:  	 pandoc",' '.join(pandoc_args))
	print("\n---------------------------------------------------------------")

try:
	call(pandoc_command)
	print(ok_text)

	# Clean up temp files (unless debug argument is passed)
	if args.debug == False:
		print("* Cleaning up temp directory......................................", end="", flush=True)
		try:
			shutil.rmtree(temp_dir)
			print(ok_text)
		except:
			print(fail_text)
			exit()
	else:
		print("* Leaving temp files at", temp_dir, "..................................", end="", flush=True)
		print(ok_text)

	print("\nYour", output_format, "file has been created at", output_file, ". ", end="", flush=True)

	reply = str(input("View "+output_file+" now? (y/n): ")).lower().strip()
	if reply[0] == 'y':
		os.system('/usr/bin/xdg-open'+' '+buildsystem_dir+'/'+output_file)
	elif reply[0] == 'n':
		exit()

except:
	print(fail_text)
	print("\nSomething went wrong. We're keeping your temp files at", temp_dir)
	exit()
