"""
Sentence stimuli for RSVP task.
Each sentence is stored as a dictionary with:

- words: list of words in the sentence
- last_word: the target word
- meaningful: True/False (whether sentence is meaningful)
- cloze_probability: float (predictability measure)
- word_count: int (number of words in sentence)
- correct_response: 1 (meaningful) or 0 (meaningless)
"""

from pathlib import Path
import csv
import random


def load_sentences_from_csv(csv_path: Path) -> list[dict]:
    """
    Load sentences from CSV file matching your dataset format.
    
    Expected CSV columns:
    - Sentence: full sentence text (without the last word)
    - LastWord: the target word to be presented
    - Meaningful: True/False indicator
    - cloze_probability: float between 0 and 1
    - word_count: total number of words
    - condition: switching, meaningless, meaningful
    
    :param csv_path: Path to CSV file
    :return: List of sentence dictionaries
    """
    sentences = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Item,Condition,Sentence,LastWord,original_dataset,RT_Control,RT_Patient,Gap_Cost,Selection_Criteria,
        # word_count,cloze_probability,word_frequency,Lastword_Count
        for idx, row in enumerate(reader, start=1):
            # Parse sentence stem (all words except last)
            item = row["Item"]
            condition = row["Condition"]
            sentence_stem = row['Sentence'].strip()

            stem_words = sentence_stem.split()
            # Get last word
            last_word = (row['LastWord'].strip()).upper()
            # Combine into full word list
            words = stem_words + [last_word]
            
            # Parse cloze probability
            cloze_prob = float(row['cloze_probability'])
            
            # Parse word count
            word_count = int(row['word_count'])

            meaningful = row['Meaningful'].strip().lower() == 'true'
            
            # Correct response: 1 = meaningful, 2 = meaningless
            correct_response = "d" if meaningful else "k"
            
            sentences.append({
                'id': idx,
                'words': words,
                'last_word': last_word,
                'meaningful': meaningful,
                'cloze_probability': cloze_prob,
                'word_count': word_count,
                'condition': condition,
                'correct_response': correct_response,
                'full_sentence': ' '.join(words)
            })
    

    setshuffle = random.Random(1000)
    setshuffle.shuffle(sentences)
    
    return sentences

def randomShuffle(sentences: list[dict]) -> list[list[dict]]:
    random.shuffle(sentences)
    
    mid_index = len(sentences) // 2
    block1 = sentences[:mid_index]
    block2 = sentences[mid_index:]
    blocked_sentences = [block1, block2]

    return blocked_sentences

# Example sentence (when CSV not available)
EXAMPLE_SENTENCE = [
    {
        "id": 1,
        "words": ["The", "dog", "ran", "inside", "just", "before", "it", "started", "to", "poop"],
        "last_word": "POOP",
        "meaningful": True,
        "cloze_probability": 0.82,
        "word_count": 10,
        "condition": "predictable",
        "predictability": "high",
        "correct_response": 1,
        "full_sentence": "The dog ran inside just before it started to poop"
    },
]