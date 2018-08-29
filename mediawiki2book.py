#!/usr/bin/env python3

#### These are the main things you may want to edit! ####

images_dir = "../xlp-manual/images/"

#########################################################

import argparse
import subprocess
from subprocess import call
import os
import shutil
import time
import tempfile

# Set up arguments
parser = argparse.ArgumentParser(description="Convert MediaWiki files to other formats")
parser.add_argument("filename", help="The MediaWiki file you want to convert")
parser.add_argument("--debug", action='store_true', default=False, help="Keep temporary files for debugging purposes and give verbose output")
parser.add_argument("-t", "--to", default="pdf", help="Format you want to export to. Accepts any format accepted by pandoc. Default is PDF") # Untested!
args = parser.parse_args()

## Define important variables
images_dir = "../xlp-manual/images/"
output_format = args.to
pandoc = "/usr/bin/pandoc"

input_file = args.filename
md_file = input_file.replace("mediawiki", "md")
output_file = input_file.replace("mediawiki", output_format)
buildsystem_dir = os.getcwd()
resources_dir = buildsystem_dir+"/"+"resources"

########## Deal with images (which should already be on your machine)

with tempfile.TemporaryDirectory() as temp_dir:  
    print("* Creating temp directory",temp_dir,"and copying over images")

shutil.copytree(images_dir, temp_dir)

########## Deal with the raw mediawiki file

# Remove references section - they're all converted to footnotes anyway, so we don't need the title for an empty section
print("* Removing wiki-only stuff")

# Safely read the input filename using 'with'
with open(input_file) as f:
    s = f.read()

with open(input_file, 'w') as f:
    s = s.replace("= Before Reading =", "")
    s = s.replace("= References =", "")
    f.write(s)

f.close()

############# Now we can convert to Markdown

print("* Converting to MarkDown for pre-processing")
call(["pandoc", "--from=mediawiki", input_file, "-t", "markdown", "-o", temp_dir+"/"+md_file])

print("* Changing to temp directory")
os.chdir(temp_dir)

### Add YAML header

print("* Adding metadata header")

header=open(resources_dir+"/header.yaml", "r").read() # header to string

# Change date to today

day = time.strftime("%d")
month = time.strftime("%B")
year = time.strftime("%Y")

todaydate = day+" "+month+", "+year

header = header.replace("$DATE", todaydate)

# Prepend to markdown file
with open(md_file, 'r') as original: data = original.read()
with open(md_file, 'w') as modified: modified.write(header + "\n" + data)

# Convert to output (default pdf) using modified eisvogel template (https://github.com/Wandmalfarbe/pandoc-latex-template)
print("* Converting to", output_format, "(this may take a while)")

pandoc_args = [md_file, "-o", buildsystem_dir+"/"+output_file, "--toc", "--template", "firevogel", "--listings", "--pdf-engine=xelatex", "--top-level-division=chapter", "--toc-depth=3"]
# subprocess.Popen("/usr/bin/pandoc" + pandoc_args)

pandoc_command = [pandoc]
pandoc_command.extend(pandoc_args) # Add arguments to the command
call(pandoc_command)

# Clean up temp files (unless debug argument is passed)
if args.debug == 0:
	print("* Cleaning up temp directory")
	shutil.rmtree(temp_dir)
else:
	print("* Leaving temp files at", temp_dir)

print("* DONE!")

exit()