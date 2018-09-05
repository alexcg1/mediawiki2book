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
import yaml

#### These are the main things you may want to edit! ####

working_dir = os.getcwd() # What directory are we in now?
resources_dir = working_dir+"/resources"
images_dir = working_dir+"/images/"

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
parser.add_argument("-f", "--fromformat", default="mediawiki", help="Format you want to export from. Accepts any format accepted by pandoc. Default is MediaWiki") # Untested!
parser.add_argument("-t", "--to", default="pdf", help="Format you want to export to. Accepts any format accepted by pandoc. Default is PDF") # Untested!
parser.add_argument("--type", default="book", choices=["article", "book"], help="What type of document you want. Books are separated and numbered by chapter, and have larger inner margins")
parser.add_argument("--lang", default="en", help="Set language, e.g. zh or en")
args = parser.parse_args()

## Define important variables
input_file = args.filename
input_format = args.fromformat
output_format = args.to
pandoc = "/usr/bin/pandoc"

if input_format == "md":
	md_file = input_file
else:
	md_file = input_file.replace(input_format, "md") # Markdown is universal intermediate format
	
output_file = input_file.replace(input_format, output_format)

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

############# Now we can convert to Markdown

if input_format != "md": # If it's already Markdown we dont need to convert
	print("* Converting to MarkDown for pre-processing.......................", end="", flush=True)
	call(["pandoc", "--from", args.fromformat, input_file, "-t", "markdown", "-o", temp_dir+"/"+md_file])
	print(ok_text)

	print("* Changing to temp directory......................................", end="", flush=True)
	os.chdir(temp_dir)
	print(ok_text)

### Add YAML header

print("* Processing header file................................................."", end="", flush=True)

header_file = resources_dir+"/header.yaml"

if Path(header_file).is_file():
	header_string = open(header_file, "r").read()
	header = yaml.load(header_string)

	header["date"] = format_date(datetime.today(), locale=args.lang) # Insert today's date and format by country

	if args.lang == "zh":
		header["mainfont"] = 'Noto Sans CJK SC Regular'

	header_text = "---\n"+yaml.dump(header)+"---"

	with open(md_file, 'r') as original: data = original.read()
	with open(md_file, 'w') as modified: modified.write(header_text + "\n" + data)

	print(ok_text)

else:
	print("* No metadata header found....................................", end="", flush=True)
	print(warning_text)

# Convert to output (default pdf)
print("* Converting to", output_format, "(this may take a while).......................", end="", flush=True)

pandoc_args = [
	md_file,
	"-o",						# Sets output filename
	working_dir+"/"+output_file,
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
	print("* Working directory: 	",working_dir)
	print("* Resources directory:   ",resources_dir)
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
		os.system('/usr/bin/xdg-open'+' '+working_dir+'/'+output_file)
	elif reply[0] == 'n':
		exit()

except:
	print(fail_text)
	print("\nSomething went wrong with pandoc. We're keeping your temp files at", temp_dir)
	exit()
