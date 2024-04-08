#!/usr/bin/env python3

import argparse
import logging
import os
logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper(), format='[%(levelname)s] %(asctime)s\t%(message)s')


from hipisejm.stenparser.sejm_parser import SejmParser


def parse_arguments():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Parses stenograms from PDF files from X Sejm RP. Available on: https://www.sejm.gov.pl/sejm10.nsf/stenogramy.xsp\n\n'
        + 'Usage example:\n'
        + '  ./parser-parse-pdf.py -i resources/test_data/01_j_ksiazka.pdf -o parsed.xml',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Filepath to PDF file to parse.')

    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Filepath to XML file to save the parsed data.')

    parser.add_argument(
        '--raw', '-r',
        action="store_true",
        help='If set, then outputs only raw parse and finishes without actual parsing.')


    args = parser.parse_args()

    return args


def main():
    args = parse_arguments()

    parser = SejmParser()

    if args.raw:
        raw_output = parser.parse_file_to_raw(args.input)

        with open(args.output, "w") as f:
            for entry in raw_output:
                f.write(str(entry))
                f.write("\n")
        return

    transcript = parser.parse_file(args.input)
    if transcript:
        logging.info("Save parsed XML to: %s", args.output)
        transcript.dump_to_xml(args.output)
    else:
        logging.info("Couldn't parse the file...")


main()
