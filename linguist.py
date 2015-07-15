import os
import re
import json
import argparse
from os.path import join, isdir
from sys import argv, exit
from goslate import Goslate

gs = Goslate()

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

def translate(string, source, target):
    return gs.translate(string, target, source).encode('utf-8')

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', help='input help')
    parser.add_argument('-o', '--output', help='output help')
    parser.add_argument('source_language', type=str)
    parser.add_argument('target_language', type=str)

    args = parser.parse_args();

    input_dir = args.input if args.input is not None else 'i18n'
    output_dir = args.output if args.output is not None else 'i18n'

    source_language = args.source_language.lower()
    target_language = args.target_language.lower()

    supported = [x.lower() for x in gs.get_languages().keys()]

    if source_language not in supported:
        exit('{0} not supported.'.format(source_language))

    if target_language not in supported:
        exit('{0} not supported.'.format(target_language))

    source_dir = join(input_dir, source_language)
    target_dir = join(output_dir, target_language)

    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            filepath = join(root, filename)
            outpath = join(target_dir, filename)

            if not isdir(target_dir):
                os.mkdir(target_dir)

            with open(filepath, 'r') as f:
                strings = json.load(f, 'utf-8')

                translate_all(strings)

            with open(outpath, 'w+') as f:
                json.dump(strings, f, indent=4, separators=(',', ': '), ensure_ascii=False)
