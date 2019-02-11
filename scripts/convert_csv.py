import argparse
import sys
from os import path, makedirs
from shutil import copyfile

import csv
import toml


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('file', metavar='FILE', type=str,
                        help='CSV file to process')
    parser.add_argument('-o', '--output', dest='output', action='store', default='.',
                        help='Output directory')

    args = parser.parse_args()

    if not path.exists(args.output):
        makedirs(args.output)

    output_dict = {
        "items": []
    }

    basepath = path.dirname(args.file)

    with open(args.file, 'rb') as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            filename = row['filename']

            try:
                num = int(row['number'])
            except ValueError:
                print('Skipping Pog of unknown number: %s' % row['number'])
                continue

            output_filename = 'pog_%04d%s' % (num, path.splitext(filename)[1])

            output_path = path.join(args.output, output_filename)

            copyfile(
                path.realpath(path.join(basepath, filename)),
                output_path
            )

            output_dict['items'].append({
                "filename": output_filename,
                "number": num,
                "series": row['series'],
                "backface": row['backface'] or 'default',
                "shiny": row['shiny'] == 'y'
            })

    with open(path.join(args.output, 'items.toml'), 'wb') as toml_file:
        toml.dump(output_dict, toml_file)


if __name__ == '__main__':
    main()
