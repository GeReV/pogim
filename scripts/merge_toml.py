import sys

import toml


def irange(start, end):
    return range(start, end + 1)


def merge(files):
    base_list = set(irange(1, 1030))
    base_list = base_list.difference(irange(541, 600))
    base_list = base_list.difference(irange(661, 720))
    base_list = base_list.difference(irange(841, 1000))

    item_lists = []

    result_list = []

    number_set = set()

    for file in files:
        with open(file, "rt") as toml_file:
            data = toml.load(toml_file)

            item_lists.append(data["items"])

    for items in item_lists:
        for item in items:
            if item["number"] in number_set and ("missing" not in item or item["missing"] != True):
                # Replace missing item if new one isn't missing.
                missing_item_index = next(i for i, v in enumerate(
                    result_list) if v["number"] == item["number"])

                result_list[missing_item_index] = item

                continue

            number_set.add(item["number"])

            result_list.append(item)

    missing_numbers = base_list.difference(number_set)

    result_list.extend(map(lambda x: {
        "number": x,
        "series": "missing",
        "backface": "default",
        "preview": "missing.svg",
        "shiny": False,
        "original": "missing.svg",
        "missing": True,
    }, missing_numbers))

    result_list = sorted(result_list, key=lambda x: x["number"])

    output_dict = {
        "items": result_list
    }

    with open("merged.toml", "wt") as toml_file:
        toml.dump(output_dict, toml_file)


def main():
    if len(sys.argv) < 3:
        print("Usage: {} FILE FILE".format(sys.argv[0]))
        exit(1)

    print("Merging...")
    merge(sys.argv[1:])


if __name__ == "__main__":
    main()
