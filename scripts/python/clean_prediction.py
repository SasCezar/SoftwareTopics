import re
from pathlib import Path

import pandas as pd

clean_regex = re.compile("\"(?P<word>(\w+|\s)+)\.?\"]?|((is |-> )\"?(?P<word2>(\w+|\s)+)\"?)")


def extract_hypernyms(sentences):
    hypernyms = []
    for sentence in sentences:
        # Split the sentence and take the last part, then clean it
        parts = sentence.split(' is ') if ' is ' in sentence else sentence.split(' -> ')
        hypernym = parts[-1].strip(".'[]")
        hypernyms.append(hypernym)
    return hypernyms

def extract_hypernyms_advanced(sentences):
    hypernyms = []
    for sentence in sentences:
        # Handle sentences with 'is', '->', and 'would be'
        if ' is ' in sentence or ' would be ' in sentence or ' could be ' in sentence:
            if ' is ' in sentence:
                parts = sentence.split(' is ')
            elif ' would be ' in sentence:
                parts = sentence.split(' would be ')
            else:
                parts = sentence.split(' could be ')
            hypernym = parts[-1].split(' or ')[0].strip(".'[]\"")
        elif ' -> ' in sentence:
            parts = sentence.split(' -> ')
            hypernym = parts[-1].strip(".'[]\"")
        else:
            # For sentences that don't follow the expected pattern
            hypernym = sentence

        hypernyms.append(hypernym)
    return hypernyms

def clean_predictions(file_path):
    df = pd.read_csv(file_path)
    cleaned = extract_hypernyms_advanced(df['hypernym'])

    df["hypernym"] = cleaned
    df.to_csv(file_path.replace(".csv", "_cleaned.csv"), index=False)


if __name__ == '__main__':
    file_path = '../../data/interim/gitranking_completed_gpt-4-1106-preview.csv'
    clean_predictions(file_path)
