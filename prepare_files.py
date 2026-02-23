from run_experiment import parseFileToList, writeToFile
from pathlib import Path
from typing import List, Tuple, Dict

def getInputWithLabel(strFile: Path, labelFile: Path) -> List[Tuple[str, str]]:
    labels = parseFileToList(labelFile)
    strings = parseFileToList(strFile)

    return list(zip(strings, labels))

def seperateByLabel(tuples: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    stringsA = []
    labelA = None
    stringsB = []
    labelB = None

    for (str, label) in tuples:
        if labelA is None and labelB is None:
            labelA = label
            stringsA.append(str)
        elif label == labelA:
            stringsA.append(str)
        else:
            labelB = label
            stringsB.append(str)

    return {labelA: stringsA, labelB: stringsB}

def prepareAllFiles():
    '''
    splits the test files into seperate files by the labels.
    the split files are stored at:
    ./syscalls/[dataset]/prepared/[dataset].[batch].[label].test
    '''

    def doBatch(name: str, n: int):
        d = seperateByLabel(
            getInputWithLabel(Path(f'./syscalls/{name}/{name}.{str(n)}.test'),
                                 Path(f'./syscalls/{name}/{name}.{str(n)}.labels'))
        )

        for k, v in d.items():
            writeToFile(v, Path(f'./syscalls/{name}/prepared/{name}.{str(n)}.{k}.test'))

    for i in range(1, 4):
        doBatch('snd-unm', i)
        doBatch('snd-cert', i)

#prepareAllFiles()
