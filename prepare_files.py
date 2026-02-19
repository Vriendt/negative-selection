from run_experiment import parseFileToList, Config, ChunkModifier, ChunkRemainderPolicy
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

def writeToFile(strings: List[str], outputFile: Path):
    outputFile.parent.mkdir(parents=True, exist_ok=True)

    with open(outputFile, mode='w') as f:
        f.write('\n'.join(strings))

    return outputFile

def prepareAllFiles():
    def doBatch(name: str, n: int):
        d = seperateByLabel(
            getInputWithLabel(Path(f'./syscalls/{name}/{name}.{str(n)}.test'),
                                 Path(f'./syscalls/{name}/{name}.{str(n)}.labels'))
        )

        for k, v in d.items():
            writeToFile(v, Path(f'./syscalls/{name}/prepared/{name}.{str(n)}.{k}.test'))

    for i in range(1, 4):
        doBatch('snd-unm', i)

    for i in range(1, 4):
        doBatch('snd-cert', i)

def prepareTrainInChunks(conf: Config, outputFile: Path) -> Path:
    '''
    expects conf.inputPath the path of the train file.
    conf.n is the chunk size
    conf.chunkRemainderPolicy decides what to do with chunks of size < conf.n
    '''
    chunks = []
    for line in parseFileToList(conf.inputPath):
        chunks.extend(ChunkModifier().apply(line, conf))

    return writeToFile(chunks, outputFile)

#prepareAllFiles()
