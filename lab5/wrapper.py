import lab, json, traceback
import json, traceback
import copy
import os
from importlib import reload
reload(lab) # this forces the student code to be reloaded when page is refreshed

corpusTries = {}

def load_corpus_file( path ):
  corpus_name = ''.join(os.path.basename(path).split('.')[:-1])
  with open(path, encoding="utf-8") as f:
    text = f.read()
    wordTrie = lab.make_word_trie(text)
    sentenceTrie = lab.make_phrase_trie(text)
  corpusTries[corpus_name] = (wordTrie, sentenceTrie)
  return corpus_name

def complete(args):
  try:
    return ('ok', get_completions(args))
  except:
    return ('error',traceback.format_exc())


def get_completions(args):
  tries = corpusTries[args["corpus"]]
  mode = args["trie_mode"]
  if mode in ("words", "pattern"):
    trie = tries[0]
    prefix = args["prefix"]
  else:
    trie = tries[1]
    prefix = tuple(args["prefix"].split())
  max_results = args["max_results"]
  if max_results == 0:
    max_results = None
  if mode == "pattern":
    r = [word for word, freq in lab.word_filter(trie, prefix)[:max_results]]
  elif args["autocorrect"] and mode == "words":
    r = lab.autocorrect(trie, prefix, max_results)
  else:
    if mode == "sentences":
      r = [' '.join(result) for result in lab.autocomplete(trie, prefix, max_results)]
    else:
      r = lab.autocomplete(trie, prefix, max_results)
  return r

def init():
  return None

  
