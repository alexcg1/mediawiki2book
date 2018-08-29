#!/usr/bin/env python3

import re # Regular exps
import argparse
from subprocess import call
import os
import shutil
import time

parser = argparse.ArgumentParser()
parser.add_argument("filename")
args = parser.parse_args()

# wiki_url = 'http://toyhouse.cc:81/wiki/'
input_file = args.filename
md_file = input_file.replace("mediawiki", "md")
pdf_file = input_file.replace("mediawiki", "pdf")
pandoc_template = "eisvogel.latex"

########## Deal with images (which should already be on your machine)

print("* Creating temp directory and copying over images")
tempdir = "temp1"
images_dir = "../images/"

shutil.copytree(images_dir, tempdir)

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
call(["pandoc", "--from=mediawiki", input_file, "-t", "markdown", "-o", tempdir+"/"+md_file])

print("* Changing to temp directory")
os.chdir(tempdir)

### Add YAML header

print("* Adding metadata header")

header=open("../resources/header.yaml", "r").read() # header to string

# Change date to today

day = time.strftime("%d")
month = time.strftime("%B")
year = time.strftime("%Y")

todaydate = day+" "+month+", "+year

header = header.replace("$DATE", todaydate)

# Prepend to markdown file
with open(md_file, 'r') as original: data = original.read()
with open(md_file, 'w') as modified: modified.write(header + "\n" + data)

# Convert to PDF using modified eisvogel template (https://github.com/Wandmalfarbe/pandoc-latex-template)
print("* Converting to PDF (this may take a while)")
call(["/usr/bin/pandoc", md_file, "-o", "../"+pdf_file, "--toc", "--template", "firevogel", "--listings", "--pdf-engine=xelatex", "--top-level-division=chapter", "--toc-depth=3"])

print("* DONE!")

exit()