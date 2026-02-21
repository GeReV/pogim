import sys

import toml


def irange(start, end):
    return range(start, end + 1)


def find_index(list, predicate):
    for i, v in enumerate(list):
        if predicate(v):
            return i

    return None


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
            if item["number"] in number_set:
                # Found a duplicate number. Check if this new item is the "missing" entry. If not, replace the existing entry with this one.
                if "missing" not in item or item["missing"] != True:
                    missing_item_index = find_index(result_list, lambda v: v["number"] == item["number"])

                    if missing_item_index is not None:
                        result_list[missing_item_index] = item
                else:
                    # This is a prior missing item. Skip it.
                    continue
            else:
                if "note" not in item:
                    item["note"] = ""

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
        "note": "",
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
        print("Usage: {} ORIGINAL NEW".format(sys.argv[0]))
        exit(1)

    print("Merging...")
    merge(sys.argv[1:])

    print("Created merged.toml")


if __name__ == "__main__":
    main()
