import pandas as pd


def stats():
    in_path = '/home/sasce/PycharmProjects/SoftwareTopics/data/result/software_taxonomy_validation_anonymized_merged_w_LLM.csv'

    df = pd.read_csv(in_path)

    """Get count of pairs for each annotator. And also the percentage"""
    annotator_counts = df.groupby('annotator').size().reset_index(name='counts')
    annotator_counts = annotator_counts.assign(percentage=annotator_counts['counts'] / len(df) * 100)
    annotator_counts.to_csv('../../data/result/annotator_counts.csv', index=False)

    """For each annotator get the percentage of is_correct column"""
    annotator_stats = df.groupby('annotator').agg({'is_correct': 'mean'}).reset_index()
    annotator_stats.to_csv('../../data/result/annotator_stats.csv', index=False)

    """Drop the rows that have 99 as annotator"""
    df = df[df['annotator'] != 99]

    """Group by the columns term,hypernym and then sum over the is_correct column and percentage"""
    df = df.groupby(['term', 'hypernym']).agg({'is_correct': 'sum'}).reset_index()
    df = df.assign(percentage=df['is_correct'] / len(df) * 100)
    """If the is_correct column is greater than 3 replace it with ≥3"""
    df = df.assign(is_correct=df['is_correct'].apply(lambda x: '>3' if x > 3 else x))

    out_path = '../../data/result/annotation_stats.csv'
    df.to_csv(out_path, index=False)

    """Count each group of is_correct column and percentage"""
    stats = df.groupby('is_correct').size().reset_index(name='counts')
    stats = stats.assign(percentage=stats['counts'] / len(df) * 100)
    stats.to_csv('../../data/result/annotation_stats_counts.csv', index=False)

if __name__ == '__main__':
    stats()
