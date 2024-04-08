# hipisejm
# Author: Marcin Walas <kontakt@marcinwalas.pl>

Process textual data from Polish Sejm.

Does the same thing as is available on https://kdp.nlp.ipipan.waw.pl/query_corpus/
but maybe someone will find those scripts useful.

I have written those scripts because 10th term of Polish Sejm was not available on KDP at that time.

Format
======

We use XML-alike format to store parsed data.
Each day is stored in the separate file (so in general one PDF transcription will create one XML file).

You will find XSD schema for the corpus output file in resources/hipisejm-transcript-schema.xsd

You can find example of the parsed file in resources/hipisejm-transcript-example.xml

Hint, to validate your XML file:

    xmllint --schema resources/hipisejm-transcript-schema.xsd resources/hipisejm-transcript-example.xml --noout

Parsed corpus
=============

Repository contains parsed transcripts available on: https://www.sejm.gov.pl/sejm10.nsf/stenogramy.xsp

Directory: resources/parsed-data/sejm/

There are also helper scripts to download and parse PDFs available on the page in 'local' directory.

Step 1: Download PDF files to resources/raw-data/sejm/

   $ ./local/run-download-sejm.sh

Step 2: Parse all files in raw-data to parsed-data using bin/parser-parse-pdf.py (run it in virtualenv: e.g. source enter.sh)

   $ ./local/run-parse-sejm.sh

Anyway you can simply use XML files available on the repo too.

Developer hints
===============

Configuration
-------------

Create virtualenv:

    source enter.sh

Then every time you start working you can simply type it again.

To add virtualenv from `enter.sh` to jupyter (one time):

    python -m ipykernel install --user --name=hipisejm

Testing
-------

To run all tests type (use -s for debug show of prints ;) ):

    python -m pytest tests

To run specific test put path to the test file:

    python -m pytest tests/t_stenparser/test_sejm_parser.py
