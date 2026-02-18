
from subprocess import Popen, PIPE, STDOUT
from typing import List, Dict, Tuple
from pathlib import Path

def openProcess(r: int) -> Popen[str]:
    return Popen(
        ['java', '-jar', 'negsel2.jar', '-self', 'english.train', '-n', '10', '-r', str(r), '-c', '-l'], 
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

def run(rMin: int, rMax: int, inputPaths: List[Path]):
    result = {}
    inputs = [(parseFileToList(p), p.stem) for p in inputPaths]

    for i in range(rMin, rMax + 1):
        p = openProcess(i)
        temp = {}
        for (input, language) in inputs:
           temp = mergeAndSortAsc(temp, runFileOnProcess(p, input, language))
        
        result[i] = temp
    
    return result

def run4():
    files = [Path('./english.test'), Path('./tagalog.test')]
    return run(4, 4, files)

def runAssignment1():
    files = [Path('./english.test'), Path('./tagalog.test')]
    return run(1, 9, files)

print(runAssignment1())