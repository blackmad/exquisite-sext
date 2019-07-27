#!/usr/bin/env python3
import markovify
import sys
import os
import time
from os import walk
import os

import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('corpusdir', metavar='corpusdir', nargs=1,
                    help='corpusdir or file')
parser.add_argument('--pos', dest='pos', action='store_true',
                    default=False,
                    help='use POS model')

args = parser.parse_args()
print(args.corpusdir)

def process_corpusdir(corpusdir):
  combined_model = None

  files = []
  if os.path.isfile(corpusdir):
    files = [('', '', [corpusdir,])]
  else:
    files = os.walk(corpusdir)

  if args.pos:
    from app.main.markov_utils import POSifiedText

  for (dirpath, _, filenames) in files:
      for (i, filename) in enumerate(filenames):
          with open(os.path.join(dirpath, filename)) as f:
              print('training on %s [%s/%s]' % (filename, i, len(filenames)))
              if args.pos:
                model = POSifiedText(f, retain_original=False, state_size=5)
              else:
                text = f.read().replace(',', '')
                model = markovify.Text(text, retain_original=False, state_size=5)
              if combined_model:
                  combined_model = markovify.combine(
                      models=[combined_model, model])
              else:
                  combined_model = model

  print(combined_model.make_sentence())
  model_json = combined_model.to_json()

  if args.pos:
    outputfilename = '%s-pos-%s.json' % (time.time(), corpusdir.replace('/', '_'))
  else:
    outputfilename = '%s-%s.json' % (time.time(), corpusdir.replace('/', '_'))
  print('writing to %s' % outputfilename)
  outputfile = open(outputfilename, 'w')
  outputfile.write(model_json)
  outputfile.close()

for corpusdir in args.corpusdir:
  print(corpusdir)
  process_corpusdir(corpusdir)
