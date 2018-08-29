# mediawiki2book

Small Python script to take a wikitext file and turn it into a beautiful PDF. This is primarily aimed at my colleagues who regularly convert material from toyhouse.cc, namely the XLP Owner's Manual

## This repo contains:

* media2wiki.py - the script to export from wiki to pretty pdf book format
* xlp_manual_dev.mediawiki - an example mediawiki file for you to process
* xlp_manual_dev_example.pdf - exported example file from the mediawiki file above
* images.zip - the images referenced in the mediawiki file
* resources/header.yaml - metadata for the exported PDF
* resources/firevogel.latex - latex template to render the PDF

## You will need:

* Python 3.6+
* Pandoc (preferably 2.0 or higher)
* A lot of LaTeX packages. I didn't keep track, but they're all available by default in Ubuntu 18.04

## Instructions

1. Copy resources/firevogel.latex to $HOME/.pandoc/templates
2. Edit mediawiki2book.py and set the image directory as needed. Edit resources/header.yaml to change paper size, title page color, etc
3. Copy your mediawiki file to mediawiki2book directory. Make sure the name is *your_filename.mediawiki*
4. Run ./mediawiki2book *your_filename.mediawiki* and wait a while. It will eventually spit out *yourfilename.pdf*.

## Troubleshooting

### I don't have the latest Pandoc!

Ubuntu comes with an old version of Pandoc. Download the latest from [Pandoc's website](https://pandoc.org/installing.html)
