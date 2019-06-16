import sys

import toml


def merge(files):
    item_lists = []

    result_list = []

    number_set = set()

    for file in files:
        with open(file, 'rt') as toml_file:
            data = toml.load(toml_file)

            item_lists.append(data['items'])

    for items in item_lists:
        for item in items:
            if item['number'] in number_set:
                continue

            number_set.add(item['number'])

            result_list.append(item)

    result_list = sorted(result_list, key=lambda x: x['number'])

    output_dict = {
        "items": result_list
    }

    with open('merged.toml', 'wt') as toml_file:
        toml.dump(output_dict, toml_file)


def main():
    if len(sys.argv) < 3:
        print("Usage: {} FILE FILE".format(sys.argv[0]))
        exit(1)

    print("Merging...")
    merge(sys.argv[1:])


if __name__ == '__main__':
    main()
