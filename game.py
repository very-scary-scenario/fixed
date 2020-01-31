from random import choice


if __name__ == '__main__':
    product = choice([
        'spiders',
        'Blåhaj',
        'Fallout 76',
        'Coca-Cola',
        'Wooloo',
    ])

    version = 'version {}'.format(choice([
        '0.0.1',
        '1.0 alpha 3',
        '15.0.2',
        '2019.07.9',
        '2.0',
        '0.9.2',
    ]))

    print(
        f'New relase: {product}, version {version}!\n\nChanges include:\n\n>'
    )
