import os
import re
import json
from os.path import join, isdir
from sys import argv, exit
from goslate import Goslate

gs = Goslate()

if len(argv) < 3:
    exit('Not enough arguments')

source_language = argv[1]
target_language = argv[2]

def wrap(string):
    pattern_start = re.compile('{{')
    pattern_end = re.compile('}}')

    string = pattern_start.sub('<span>{{', string)
    string = pattern_end.sub('}}</span>', string)

    return string

def unwrap(string):
    pattern_start = re.compile('<span> {{', re.IGNORECASE)
    pattern_end = re.compile('}} </span>', re.IGNORECASE)

    string = string.replace('</ ', '</')
    string = pattern_start.sub('{{', string)
    string = pattern_end.sub('}}', string)

    return string

def translate_all(strings):
    for string in strings:
        if type(strings[string]) == type(dict()):
            translate_all(strings[string])
        else:
            original_string = wrap(strings[string])

            translated_string = unwrap(translate(original_string, source_language, target_language))

            original_variables = re.findall('{{.*}}', original_string)
            translated_variables = re.findall('{{.*}}', translated_string)

            if len(original_variables) > 0:
                for i, var in enumerate(original_variables):
                    translated_string = translated_string.replace(translated_variables[i], str(var))

            strings[string] = translated_string

def translate(string, source, target):
    return gs.translate(string, target, source).encode('utf-8')

for root, dirs, files in os.walk(join('i18n', source_language)):
    for filename in files:
        filepath = join(root, filename)
        outpath = join(join('i18n', target_language), filename)

        if not isdir(join('i18n', target_language)):
            os.mkdir(join('i18n', target_language))

        with open(filepath, 'r') as f:
            strings = json.load(f)

            translate_all(strings)

        with open(outpath, 'w+') as f:
            json.dump(strings, f, indent=4, ensure_ascii=False)
