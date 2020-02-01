import os
from random import choice, sample

from version import random_version


CATEGORIES_DIR = os.path.join(os.path.dirname(__file__), 'categories')


def get_categories_shortlist():
    return sample(list(CATEGORIES), 6)


def _load_category(filename):
    category_name, _ = os.path.splitext(filename)
    releases = []
    generic_comments = []

    with open(os.path.join(CATEGORIES_DIR, filename)) as cf:
        for line in cf.readlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith('>'):
                content = line[1:].strip()

                if not content:
                    raise RuntimeError(f'empty comment in {filename}')

                if releases:
                    releases[-1]['comments'].append(content)
                else:
                    print(filename)
                    generic_comments.append(content)
            else:
                releases.append({'name': line, 'comments': []})

    return category_name, {
        'releases': releases,
        'generic_comments': generic_comments,
    }


CATEGORIES = {name: category for name, category in (
    _load_category(fn) for fn in os.listdir(CATEGORIES_DIR)
    if not fn.startswith('.')
)}


if __name__ == '__main__':
    shortlist = get_categories_shortlist()
    for i, cat in enumerate(shortlist):
        print(f'[{i + 1}] {cat}')

    category = shortlist[int(input('pick a category!\n> ')) - 1]

    product = choice(CATEGORIES[category]['releases'])['name']

    print(
        f'New release: {product}, version {random_version()}!'
        '\n\nChanges include:\n\n>'
    )
