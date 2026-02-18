from subprocess import Popen, PIPE, STDOUT
from typing import List, Dict, Tuple, Iterable
from pathlib import Path
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum

class ChunkRemainderPolicy(Enum):
    KEEP = 0
    DROP = 1
    PAD = 2

PADDING_CHAR = '_'

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
                    chunks[-1] = chunks[-1] + PADDING_CHAR * remainder
                return chunks

        return chunks

def openProcess(conf: Config) -> Popen[str]:
    return Popen(
        ['java', '-jar', 'negsel2.jar', '-self', str(conf.inputPath), '-n', str(conf.n), '-r', str(conf.r), '-c', '-l'], 
        stdout=PIPE, 
        stderr=STDOUT, 
        stdin=PIPE, 
        text=True)
    
def parseFileToList(path: Path, conf: Config, modifier: LineModifier) -> List[str]:
    result = []

    with open(path) as f:
        for line in f.read().splitlines():
            result.extend(modifier.apply(line, conf))

    return result
    
def runFileOnProcess(process: Popen[str], strings: List[str], language: str) -> Dict[str, Tuple[str, float]]:
    results = {}

    for string in strings:
        process.stdin.write(string + '\n')
        process.stdin.flush()

        result = process.stdout.readline().strip()
        results[string] = (language, float(result))

    return results

def run(conf: Config, inputPaths: List[Path], lineModifier: LineModifier):
    result = {}
    inputs = [(parseFileToList(p, conf, lineModifier), p.stem) for p in inputPaths]

    def sort(d):
        return dict(sorted(d.items(), key=lambda item: item[1][1]))

    for n in conf.iterN():
        for r in conf.iterR():
            p = openProcess(conf)
            temp  = {}
            for (input, language) in inputs:
                temp |=  runFileOnProcess(p, input, language)
        
            p.kill()
            result[(n, r)] = sort(temp)
    
    return result

def run4():
    conf = Config((10,10), (4,4), Path('./english.train'))
    files = [Path('./english.test'), Path('./tagalog.test')]
    return run(conf, files, IdentityModifier())

def runAssignment1():
    conf = Config((10,10), (1,9), Path('./english.train'))
    files = [Path('./english.test'), Path('./tagalog.test')]
    return run(conf, files, IdentityModifier())
