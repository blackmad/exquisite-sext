from . import database

from app.main.markov import generate_completions
from app.main.markov_utils import nlp

def make_room_completions(roomId):
    newStory = database.getStory(roomId)
    print('story: ' + newStory)
    nextWords = generate_completions(
        modelName='bdsm-pos-', currentText=newStory, numCompletions=25)
    if newStory.strip()[-1] in '?!.':
        nextWords = [n.capitalize() for n in nextWords]

    punctuation = ['.', ',', '?', '!', '-', ':newline:']
    savedNouns = list(set([word.orth_ for word in nlp(newStory) if word.pos_ == 'PROPN']))
    completions = {
        'Next Words': nextWords,
        'Punctuation': punctuation,
        'Saved Nouns': savedNouns,
        'Freebies': ['and', 'or', 'not', 'with', 'to', 'the', 'a', 'an', 'with', 'in']
    }
    return completions