from pathlib import Path

import pandas as pd


def combine():
    taxonomy_path = Path('../../data/interim/taxonomy/')
    processed_folders = [Path(x) for x in taxonomy_path.iterdir() if 'processed' in str(x)]
    melted_files = [y for x in processed_folders for y in x.iterdir() if 'melted' in y.stem]

    hyperparameters = ['Take_All', 'Types_Threshold', 'Max_Depth', 'LLM', 'Sim_Threshold', 'prompt_type']

    res = []
    for file in melted_files:
        # get folder name
        folder = file.parent.stem.replace('_processed', '')
        df = pd.read_csv(file)
        if 'Take_All' in df.columns:
            df.drop(columns=['Take_All'], inplace=True)

        remap = {}
        count = 0
        for hp in hyperparameters:
            if hp in df.columns:
                remap[hp] = f"param_{count}"
                count += 1
        df.rename(columns=remap, inplace=True)

        df['source'] = folder
        res.append(df)

    res = pd.concat(res)
    res.to_csv('../../data/interim/taxonomy/combined_melted.csv', index=False)


if __name__ == '__main__':
    combine()
