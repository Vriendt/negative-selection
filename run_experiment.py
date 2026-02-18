
from subprocess import Popen, PIPE, STDOUT
from typing import List, Dict, Tuple
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Config:
    nRange: Tuple[int, int]
    n: int = field(init=False)
    rRange: Tuple[int, int]
    r: int = field(init=False)
    inputPath: Path

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

def openProcess(conf: Config) -> Popen[str]:
    return Popen(
        ['java', '-jar', 'negsel2.jar', '-self', str(conf.inputPath), '-n', str(conf.n), '-r', str(conf.r), '-c', '-l'], 
        stdout=PIPE, 
        stderr=STDOUT, 
        stdin=PIPE, 
        text=True)

def parseFileToList(path: Path) -> List[str]:
    with open(path) as f:
        return [s.strip() for s in f.readlines()]
    
def runFileOnProcess(process: Popen[str], strings: List[str], language: str) -> Dict[str, Tuple[str, float]]:
    results = {}

    for string in strings:
        process.stdin.write(string + '\n')
        process.stdin.flush()

        result = process.stdout.readline().strip()
        results[string] = (language, float(result))

    return results

def mergeAndSortAsc(dictA: Dict[str, Tuple[str, float]], dictB: Dict[str, Tuple[str, float]]) -> Dict[str, Tuple[str, float]]:
    temp = dictA | dictB
    return dict(sorted(temp.items(), key=lambda item: item[1][1]))

def run(conf: Config, inputPaths: List[Path]):
    result = {}
    inputs = [(parseFileToList(p), p.stem) for p in inputPaths]

    for n in conf.iterN():
        for r in conf.iterR():
            p = openProcess(conf)
            temp = {}
            for (input, language) in inputs:
                temp = mergeAndSortAsc(temp, runFileOnProcess(p, input, language))
        
            result[(n, r)] = temp
    
    return result

def run4():
    conf = Config((10,10), (4,4), Path('./english.train'))
    files = [Path('./english.test'), Path('./tagalog.test')]
    return run(conf, files)

def runAssignment1():
    conf = Config((10,10), (1,9), Path('./english.train'))
    files = [Path('./english.test'), Path('./tagalog.test')]
    return run(conf, files)
