from subprocess import Popen, PIPE, STDOUT
from typing import List, Dict, Tuple, Iterable, Any
from pathlib import Path
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
from os import remove

class ChunkRemainderPolicy(Enum):
    KEEP = 0
    DROP = 1
    PAD = 2

PADDING_CHAR = '_'
PREPARED_TRAIN_PATH = Path('./prepared.train')

@dataclass
class Config:
    nRange: Tuple[int, int]
    n: int = field(init=False)
    rRange: Tuple[int, int]
    r: int = field(init=False)
    inputPath: Path
    chunkRemainderPolicy: ChunkRemainderPolicy = ChunkRemainderPolicy.KEEP

    def __post_init__(self):
        self.setN(self.nRange[0])
        self.setR(self.rRange[0])

    def setN(self, n: int) -> None:
        if not (n >= self.nRange[0] and n <= self.nRange[1]):
            raise ValueError(f"{n} must be between {self.nRange} inclusive")
        self.n = n

    def setR(self, r: int) -> None:
        if not (r >= self.rRange[0] and r <= self.rRange[1]):
            raise ValueError(f"{r} must be between {self.rRange} inclusive")
        self.r = r

    def iterN(self):
        for n in range(self.nRange[0], self.nRange[1] + 1):
            self.setN(n)
            yield n

    def iterR(self):
        for r in range(self.rRange[0], self.rRange[1] + 1):
            self.setR(r)
            yield r

    def copy(self):
        return Config(self.nRange, self.rRange, self.inputPath, self.chunkRemainderPolicy)

class LineModifier(ABC):
    @staticmethod
    @abstractmethod
    def apply(line: str, conf: Config) -> Iterable[str]:
        pass

class IdentityModifier(LineModifier):
    @staticmethod
    def apply(line: str, conf: Config) -> Iterable[str]:
        yield line
    
class ChunkModifier(LineModifier):
    @staticmethod
    def apply(line: str, conf: Config) -> Iterable[str]:
        chunks = [line[i:i+conf.n] for i in range(0, len(line), conf.n)]
        remainder = len(line) % conf.n

        match(conf.chunkRemainderPolicy):
            case ChunkRemainderPolicy.KEEP:
                return chunks
            case ChunkRemainderPolicy.DROP:
                if remainder > 0:
                    return chunks[:-1]
                return chunks
            case ChunkRemainderPolicy.PAD:
                if remainder > 0:
                    chunks[-1] = chunks[-1] + PADDING_CHAR * (conf.n - remainder)
                return chunks

        return chunks

def openProcess(conf: Config) -> Popen[str]:
    return Popen(
        ['java', '-jar', 'negsel2.jar', '-self', str(conf.inputPath), '-n', str(conf.n), '-r', str(conf.r), '-c', '-l'], 
        stdout=PIPE, 
        stderr=STDOUT, 
        stdin=PIPE, 
        text=True,
        bufsize=1)
    
def parseFileToList(path: Path) -> List[str]:
    with open(path) as f:
        return f.read().splitlines()
    
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
    
def runFileOnProcess(process: Popen[str], strings: List[str], language: str, conf: Config, modifier: LineModifier) -> Dict[str, Tuple[str, float]]:
    results = {}

    def runLine(line: str) -> float:
        sum = 0
        count = 0
        for chunk in modifier.apply(line, conf):
            process.stdin.write(chunk + '\n')
            process.stdin.flush()
            sum += float(process.stdout.readline().strip())
            count += 1

        if count > 0:
            return (sum / count)
        return 0.0

    for string in strings:
        results[string] = (language, runLine(string))

    return results

def run(conf: Config, inputPathsWithLabel: List[Tuple[Path, Any]], lineModifier: LineModifier, trainPrepareCRMP: ChunkRemainderPolicy):
    result = {}
    inputs = [(parseFileToList(p), l) for (p, l) in inputPathsWithLabel]

    def sort(d):
        return dict(sorted(d.items(), key=lambda item: item[1][1]))

    for n in conf.iterN():
        tempConf = conf.copy()
        tempConf.chunkRemainderPolicy = trainPrepareCRMP
        tempConf.setN(n)
        tempConf.inputPath = prepareTrainInChunks(tempConf, PREPARED_TRAIN_PATH)
        for r in conf.iterR():
            tempConf.setR(r)
            p = openProcess(tempConf)
            temp  = {}
            for (input, language) in inputs:
                temp |=  runFileOnProcess(p, input, language, conf, lineModifier)
        
            p.kill()
            result[(n, r)] = sort(temp)

            # PREPARED_TRAIN_PATH.unlink(missing_ok=True)
        # remove(PREPARED_TRAIN_PATH)

    return result

def writeToFile(strings: List[str], outputFile: Path):
    outputFile.parent.mkdir(parents=True, exist_ok=True)

    with open(outputFile, mode='w') as f:
        f.write('\n'.join(strings))

    return outputFile

def run4():
    conf = Config((10,10), (4,4), Path('./english.train'))
    files = [(Path('./english.test'), 0), (Path('./tagalog.test'), 1)]
    return run(conf, files, ChunkModifier(), ChunkRemainderPolicy.PAD)

def runAssignment1():
    conf = Config((10,10), (1,9), Path('./english.train'))
    files = [(Path('./english.test'), 0), (Path('./tagalog.test'), 1)]
    return run(conf, files, ChunkModifier(), ChunkRemainderPolicy.PAD)

def part2Example():
    conf = Config((10,12), (4,4), Path('./syscalls/snd-unm/snd-unm.train'), ChunkRemainderPolicy.PAD)
    files = [(Path('./syscalls/snd-unm/prepared/snd-unm.1.0.test'), 0), (Path('./syscalls/snd-unm/prepared/snd-unm.1.1.test'), 1)]
    return run(conf, files, ChunkModifier(), ChunkRemainderPolicy.PAD)
