# mediawiki2book

Small Python script to take a MediaWiki file and turn it into a beautiful PDF. This is aimed at my colleagues who regularly convert material from http://toyhouse.cc, namely the XLP Owner's Manual, but I'm happy for anyone to use or reuse this code.

## This repo contains:

* media2wiki.py - the script to export from wiki to pretty pdf book format
* xlp_manual_dev.mediawiki - an example mediawiki file for you to process
* xlp_manual_dev_example.pdf - exported example file from the mediawiki file above
* images/ - the images referenced in the example mediawiki file
* resources/header.yaml - metadata for the exported PDF
* resources/templates/firevogel.latex - latex template to render the PDF

## You will need:

* Python 3.6+
* Pandoc (preferably 2.0 or higher)
* A lot of LaTeX packages. I didn't keep track, but they're all available by default in Ubuntu 18.04

## Usage

1. Copy your mediawiki page source to a file in your working directory (called *something.mediawiki*, and put any linked images into 'images' folder in the same directory
2. Edit resources/header.yaml to change paper size, title page color, etc
3. Run ./mediawiki2book *your_filename.mediawiki* and wait a while. It will eventually spit out *yourfilename.pdf*.

mediawiki2book works pretty well with English (by default) and Chinese (*--lang zh*). No guarantees about it working for other languages yet, but feel free to push changes to make that happen!

## Troubleshooting

### I don't have the latest Pandoc!

Ubuntu comes with an old version of Pandoc. Download the latest from [Pandoc's website](https://pandoc.org/installing.html)

### Chinese/other CJK language is coming out wrong

* Run mediawiki2book with *--lang zh* or whatever your language is. Right now it's confirmed to work in Chinese and English. To add new languages you should see the code about "mainfont" in the YAML header
* Make sure you have Chinese fonts installed
* Check the [Pandoc wiki on Chinese stuff](https://github.com/jgm/pandoc/wiki/Pandoc-with-Chinese) for other troubleshooting

### Something else is going wrong

* Run mediawiki2book with the *--debug* argument to check your variables (like filenames, etc) are okay
* Run mediawiki2book with the *--veryverbose* argument to see all of pandoc's debugging info