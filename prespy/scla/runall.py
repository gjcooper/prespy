# coding: utf-8
from sndan import scla, ExtractError
import sys


def runit(orig, rtext, settings, factors, measures):
    """Run the whole procedure with certain settings"""
    for t in orig:
        print(t[0])
        settings['mdur'] = float(t[3])
        settings['thresh'] = float(t[4])
        try:
            res = scla(t[0], t[1], t[2], **settings)
        except ValueError as e:
            print(e.message)
            continue
        except ExtractError as e:
            print(e.message)
            continue
        print('Successfully extracted')

        results = [t[0], t[3], t[4]]
        for f in factors:
            for m in measures:
                results.append(str(round(res[f][m], 1)))

        rtext += '\t'.join(results) + '\n'
    return rtext


def runall(fn, ofn):
    """Use runit on all lines extracted from fn and write to ofn"""
    with open(fn, 'r') as tf:
        tests = [t.split('\t') for t in tf.read().splitlines()]

    settings = {'mdur': 0.012, 'thresh': 0.2}  # Defaults
    factors = ['Lower Bound', 'Upper Bound', 'Port Time Diffs',
               'Snd Time Diffs', 'Port Code Lengths']
    measures = ['mean', 'min', 'max', 'stddev']

    rtext = 'ID\tmdur\tthresh\t'
    rtext += '\t'.join([f+'_'+m for f in factors for m in measures]) + '\n'
    rtext = runit(tests, rtext, settings, factors, measures)
    with open(ofn, 'w') as rf:
        rf.write(rtext)


if __name__ == '__main__':
    runall(*sys.argv[1:])
