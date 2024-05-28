import pandas as pd

from entity import Taxonomy


def convert():
    file_path = '/pipeline/ensemble_output_2.json'
    taxo = Taxonomy.load(file_path)
    df = pd.DataFrame(taxo.pairs, columns=['term', 'hypernym', 'src'])
    df.to_csv(file_path.replace('json', 'csv'), index=False)


if __name__ == '__main__':
    convert()

