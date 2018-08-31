#!/usr/bin/env python3

import argparse
import subprocess
from subprocess import call
import os
import shutil
import time
import tempfile
import sys
from pathlib import Path

#### These are the main things you may want to edit! ####

buildsystem_dir = os.getcwd()
resources_dir = buildsystem_dir+"/resources"
images_dir = buildsystem_dir+"/images/"

#########################################################

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
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
parser.add_argument("-t", "--to", default="pdf", help="Format you want to export to. Accepts any format accepted by pandoc. Default is PDF") # Untested!
parser.add_argument("--cjk", action='store_true', default=False) # This is a kluge. How can we programmatically figure out language?
parser.add_argument("--type", default="book", choices=["article", "book"])
args = parser.parse_args()

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

shutil.copytree(images_dir, temp_dir)

print(ok_text)

########## Deal with the raw mediawiki file

# Remove references section - they're all converted to footnotes anyway, so we don't need the title for an empty section
print("* Removing wiki-only stuff........................................", end="", flush=True)

# Safely read the input filename using 'with'
with open(input_file) as f:
	s = f.read()

with open(input_file, 'w') as f:
	s = s.replace("= Before Reading =", "")
	s = s.replace("= References =", "")
	f.write(s)

f.close()

print(ok_text)

############# Now we can convert to Markdown

print("* Converting to MarkDown for pre-processing.......................", end="", flush=True)
call(["pandoc", "--from=mediawiki", input_file, "-t", "markdown", "-o", temp_dir+"/"+md_file])
print(ok_text)

print("* Changing to temp directory......................................", end="", flush=True)
os.chdir(temp_dir)
print(ok_text)

### Add YAML header

if args.cjk:
	header = resources_dir+"/header-cjk.yaml" # This is a kluge. Should really add these lines into the header.yaml programatically
else:
	header = resources_dir+"/header.yaml"

if Path(header).is_file():
	print("* Adding metadata header..........................................", end="", flush=True)
	header=open(header, "r").read() # header file to string

	# Change date to today
	day = time.strftime("%d")
	year = time.strftime("%Y")

	if args.cjk: # Can we replace this with a library that will write date in proper format??
		month = time.strftime("%m")
	else:
		month = time.strftime("%B")
	
	if args.cjk:
		todaydate = year+"年"+month+"月"+day+"日"
	else:
		todaydate = day+" "+month+", "+year
	
	header = header.replace("$DATE", todaydate)

	# Prepend to markdown file
	with open(md_file, 'r') as original: data = original.read()
	with open(md_file, 'w') as modified: modified.write(header + "\n" + data)

	print(ok_text)

else:
	print("* No metadata header found....................................", end="", flush=True)
	print(warning_text)
	warnings.append("No header.yaml\nWe couldn't find header.yaml in your resources directory. This means that a nice cover and title/author info may be missing from your PDF")

# Convert to output (default pdf) using modified eisvogel template (https://github.com/Wandmalfarbe/pandoc-latex-template)
print("* Converting to", output_format, "(this may take a while).......................", end="", flush=True)

# pandoc_args = [md_file, "-o", buildsystem_dir+"/"+output_file, "--toc", "--top-level-division=chapter", "--template="+template, "--listings", "--pdf-engine=xelatex", "--toc-depth=3", "--data-dir="+resources_dir]
pandoc_args = [md_file, "-o", buildsystem_dir+"/"+output_file, "--toc", "--template="+template, "--listings", "--pdf-engine=xelatex", "--toc-depth=3", "--data-dir="+resources_dir]

if args.cjk:
	pandoc_args.append("-V lang=zh")

if args.debug:
	pandoc_args.append("--verbose")

if args.type == "book":
	pandoc_args.append("--top-level-division=chapter")

pandoc_command = [pandoc]
pandoc_command.extend(pandoc_args) # Add arguments to the command

try:
	call(pandoc_command)
	print(ok_text)

	# Clean up temp files (unless debug argument is passed)
	if args.debug == 0:
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

except:
	print(fail_text)
	print("\nSomething went wrong. We're keeping your temp files at", temp_dir)
	exit()

reply = str(input('View output file now? (y/n): ')).lower().strip()
if reply[0] == 'y':
	os.system('/usr/bin/xdg-open'+' '+buildsystem_dir+'/'+output_file)
elif reply[0] == 'n':
	exit()