from prespy.scla import sndan
import sys
import argparse

def scla():
    parser = argparse.ArgumentParser(description='Analyse sound latencies')
    parser.add_argument('--runid', '-i', help='An id for the sound plot', default='scla')
    parser.add_argument('soundfile', help='A sound recording of port and sound output')
    parser.add_argument('logfile', help='Stimulus delivery recording of event sequence')
    parser.add_argument('--schannel', '-c', help='The channel sounds were recorded in', default=1)
    parser.add_argument('--maxdur', '-m', help='Max duration for sound/port event', default=0.012)
    parser.add_argument('--thresh', '-t', help='Threshold for sound/port detection', default=0.2)

    args = parser.parse_args()

    res = sndan.scla(**vars(args))
    report = ['==================================']
    for result in res:
        report.append(result)
        for measure in ['mean', 'min', 'max', 'stddev']:
            report.append('\t{}: {}'.format(measure, res[result][measure]))
        report.append('----------------------------------')
    report.append(report[0])

    print('\n'.join(report))
