import os
from typing import Iterable
from urllib.parse import urlparse

from pronto import Ontology, Term

OBO_PATH = '/Users/cthoyt/dev/chiro/chiro.obo'
OBO_CACHE_PATH = '/Users/cthoyt/dev/chiro/chiro.obo.json'


def monkey_patch_downloader(cache_directory: str):
    import pronto.utils.io
    old_get_handle = pronto.utils.io.get_handle

    def new_get_handle(path: str):
        try:
            parse_result = urlparse(path)
        except ValueError:
            return old_get_handle(path)
        else:
            filename = os.path.basename(parse_result.path)
            path = os.path.abspath(os.path.join(cache_directory, filename))
            if not os.path.exists(path):
                raise FileNotFoundError(f'Could not find cached file at {path}')
            return open(path, "rb", buffering=0)

    new_get_handle._old = old_get_handle

    pronto.utils.io.get_handle = new_get_handle

    def revert():
        pronto.utils.io.get_handle = old_get_handle

    new_get_handle.revert = revert


def main():
    print('monkey patching')
    monkey_patch_downloader('/Users/cthoyt/dev/pyobo/bel')

    if os.path.exists(OBO_CACHE_PATH):
        ontology = Ontology(OBO_CACHE_PATH)
    else:
        print(f'Parsing from {OBO_PATH}')
        ontology = Ontology(OBO_PATH)
        with open(OBO_CACHE_PATH, 'wb') as file:
            ontology.dump(file, format='json')

    terms: Iterable[Term] = ontology.terms()
    for term in terms:
        print(term)
        print(term.intersection_of)


if __name__ == '__main__':
    main()
