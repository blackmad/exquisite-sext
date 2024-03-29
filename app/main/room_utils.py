from . import database

from app.main.markov import generate_completions
from app.main.markov_utils import nlp

def make_room_completions(roomId):
    newStory = database.getStory(roomId).replace(',', '')
    print('story: ' + newStory)

    nextWords = generate_completions(
        modelName='bdsm', currentText=newStory, numCompletions=25)
    if newStory.strip()[-1] in '?!.':
        nextWords = [n.capitalize() for n in nextWords]

    punctuation = ['.', ',', '?', '!', '-', ':newline:']
    savedNouns = list(set([word.orth_ for word in nlp(newStory) if word.pos_ == 'PROPN']))
    completions = [
        {
          'name': 'Next Words',
          'words': nextWords,
        },
        {
          'name': 'Punctuation',
          'words': punctuation,
        },
        {
          'name': 'Saved Nouns',
          'words': savedNouns,
        },
        {'name': 'Freebies',
        'words': ['and', 'or', 'not', 'with', 'to', 'the', 'a', 'an', 'with', 'in']
        }
    ]
    
    return completions