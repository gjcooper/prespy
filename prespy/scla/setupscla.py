import os
import sys
qstring = 'Does each file match(Y/N): If not rename files to match and rerun'


def run(fn, ldir, wdir):
    """run the setup"""
    logs = os.listdir(ldir)
    wavs = os.listdir(wdir)
    wavs = [w for w in wavs if w[-1] == 'v']
    for w in range(len(wavs)):
        print(wavs[w], logs[w])
    if input(qstring) == 'Y':
        labels = []
        for l in logs:
            with open(os.path.join(ldir, l), 'r') as lf:
                rtxt = lf.read().splitlines()
            labels.append(rtxt[5].split('\t')[0])

        tt = ''
        for r in range(len(wavs)):
            lfn = os.path.join(ldir, logs[r])
            wfn = os.path.join(wdir, wavs[r])
            line = [labels[r], wfn, lfn, '0.012', '0.2']
            tt += '\t'.join(line) + '\n'
        with open(fn, 'w') as tf:
            tf.write(tt)

if __name__ == '__main__':
    run(*sys.argv[1:])
