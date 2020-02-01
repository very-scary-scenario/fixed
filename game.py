import os
from random import choice, sample

from version import random_version


CATEGORIES_DIR = os.path.join(os.path.dirname(__file__), 'categories')


def get_categories_shortlist():
    return sample(list(CATEGORIES), 6)


def _load_category(filename):
    category_name, _ = os.path.splitext(filename)
    releases = []
    with open(os.path.join(CATEGORIES_DIR, filename)) as cf:
        for line in cf.readlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith('>'):
                releases[-1]['comments'].append(line[1:].strip())
            else:
                releases.append({'name': line, 'comments': []})

    return category_name, releases


CATEGORIES = {name: category for name, category in (
    _load_category(fn) for fn in os.listdir(CATEGORIES_DIR)
    if not fn.startswith('.')
)}


if __name__ == '__main__':
    shortlist = get_categories_shortlist()
    for i, cat in enumerate(shortlist):
        print(f'[{i + 1}] {cat}')

    category = shortlist[int(input('pick a category!\n> ')) - 1]

    product = choice(CATEGORIES[category])['name']

    print(
        f'New release: {product}, version {random_version()}!'
        '\n\nChanges include:\n\n>'
    )
