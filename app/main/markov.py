# THIS IS A STUPID USE OF A MARKOV MODEL - not using weights at all

import markovify

from markovify.chain import BEGIN
import random

from os import listdir
from os.path import isfile, join
import os.path

from app.main.markov_utils import POSifiedText, nlp
import pygtrie as trie

import traceback

model_dir = 'models'

model_files = [os.path.join(model_dir, f) for f in listdir(
    model_dir) if isfile(join(model_dir, f))]

models = {}
modelTries = {}

for model_file in model_files:
    modelname = os.path.basename(model_file).split('.')[0]
    # models[modelname] = markovify.Text.from_json(open(model_file).read())
    if '-pos' in model_file:
        models[modelname] = POSifiedText.from_json(open(model_file).read())
    else:
        models[modelname] = markovify.Text.from_json(open(model_file).read())
    modelTries[modelname] = trie.Trie().fromkeys(models[modelname].chain.model.keys())


def generate_completions(modelName, currentText, numCompletions):
    if modelName not in models:
        raise 'No model named %s' % modelName
    model = models[modelName]

    completions = set()

    print('currentText %s' % currentText)
    wordSample = currentText.split(' ')[-20:]
    endText = ' '.join(wordSample)
    print('endText %s' % endText)
    parsedText = tuple(model.word_split(endText))
    print('wordSample len %s' % len(wordSample))
    numWordsToTake = min([5, len(wordSample)])

    while numWordsToTake >= 0 and len(completions) < numCompletions:
        print('taking %s' % numWordsToTake)
        split = parsedText[-numWordsToTake:]

        numWordsToTake -= 1

        print('trying split: %s' % (split,))
        word_count = len(split)

        model = models[modelName]
        modeltrie = modelTries[modelName]
        print('last char: %s' % currentText.strip()[-1])

        if word_count > 0 and word_count < model.state_size and currentText.strip()[-1] not in '?!.':
            print('trying to expand ...')
            try:
              expansions = [key for key in modeltrie.iteritems(split)]
            except Exception as e:
              traceback.print_exc()
              print('failed ...')
              print(e)
              continue

            print('expanded to %s' % expansions)
            for (expansion, _) in expansions:
              toAdd = None

              if 'PUNCT' in expansion[len(split)] and len(expansion) > len(split) + 1:
                toAdd = expansion[len(split)+1]
              elif len(expansion) > len(split):
                toAdd = expansion[len(split)]

              if toAdd:
                print('adding %s' % toAdd)
                completions.add(toAdd)
        else:
          if currentText[-1] in '?!.':
            split = tuple((BEGIN,) * (model.state_size))
            print('changed split to %s' % (split,))

          print('split was big enough')
          try:
            newCompletions = set([
              models[modelName].chain.move(split)
              for n in range(numCompletions*3)
            ])
            print('adding new completions')
            completions = completions.union(newCompletions)
          except Exception as e:
            print('That split did not work %s' % (split,))
        # print(completions)

        

    print(len(completions))
    completions = list(completions)
    random.shuffle(completions)
    return [model.word_join([w,]) for w in completions[:numCompletions]]
