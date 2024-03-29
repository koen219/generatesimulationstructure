from pathlib import Path
from typing import List, Dict, Optional, Protocol, Tuple, Union
from dataclasses import dataclass, field
import itertools

class FileReader:
    def __init__(self, path: Path, token: str = '!'):
        self._path: Path = path
        self._replacementToken = token

    def TokenPositions(self) -> Tuple[List[int], List[str]]:
        positions = []
        lines = []
        with open(str(self._path), 'r') as f:
            for k, line in enumerate(f.readlines()):
                if line.startswith(self._replacementToken):
                    positions.append(k)
                    lines.append(line[len(self._replacementToken):-1])

        return positions, lines

    def HasReplacementToken(self) -> bool:
        with open(str(self._path), 'r') as f:
            for line in f.readlines():
                if line.startswith(self._replacementToken):
                    return True
        return False

    @property
    def contents(self):
        with open(self._path, 'r') as f:
            lines = f.readlines()
        return lines


@dataclass
class Parameter:
    name: str
    value: str
    # template: str


@dataclass
class Parameters:
    name: str
    _values: List

    @property
    def values(self):
        return [Parameter(self.name, value) for value in self._values]


class NameGenerator(Protocol):
    def generateName(self, parameters: Tuple[Parameter, ...]) -> str: ...


class TrivialNameGenerator:
    def generateName(self, parameters: Tuple[Parameter, ...]) -> str:
        name = ""
        for par in parameters:
            name += par.name+str(par.value).replace('.', '_')
        return name


class ReplacementRules(Protocol):
    def apply(self, line: str,
              parset: Tuple[Parameter, ...], unique_name: str) -> List[str]: ...

class GlobalRules(Protocol):
    def apply(self, folder: Path, templatefile: Path): ...

class SimulationGenerator:
    def __init__(self, folder: Path):
        assert folder.exists(), f"Directory {folder} not found"
        self._folder = folder.resolve()
        self._templates: Dict[str, Path] = {}
        self._parameters: List[Tuple[Parameter, ...]] = []

        self.nameGenerator: NameGenerator = TrivialNameGenerator()

        self._replacementRules: Dict[str, ReplacementRules] = {}
        self._globalRules: Dict[str, GlobalRules] = {}
    
    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, parameters: Union[List[Tuple[Parameter, ...]],List[Parameter]] ):
        self._parameters = [(par,) if not isinstance(par,tuple) else par for par in parameters]


    @property
    def templates(self):
        return self._templates

    def add_template(self, name: str, templatefile: str):
        pathtofile = Path(templatefile).resolve()
        assert pathtofile.exists(), f"File {pathtofile} does not exists!"
        self._templates[name] = pathtofile

    def add_replacement_rule(self, name: str, rule: ReplacementRules):
        self._replacementRules[name] = rule

    def add_global_rule(self, name, rule: GlobalRules):
        self._globalRules[name] = rule
    
    def _writeFile(self, contents: List[str], filename: str):
        with open(self._folder / filename, 'w') as f:
            f.writelines(contents)

    def generate(self):
        files_that_need_parsing = [(name, file) for name, file in self._templates.items()
                                   if FileReader(file).HasReplacementToken()
                                   ]
        assert all(name in self._replacementRules.keys()
                   for name, _ in files_that_need_parsing), f"No rules for parsing {files_that_need_parsing}"
        for parset in self.parameters:
            unique_name = self.nameGenerator.generateName(parset)
            for name, file in files_that_need_parsing:
                reader = FileReader(file)
                contents = reader.contents
                replacements, lines = reader.TokenPositions()
                
                newlines = {}
                for index, line in zip(replacements, lines):
                    newline = self._replacementRules[name].apply(line, parset, unique_name)
                    newlines[index] = newline
                    assert contents[index][0] == '!' 
                new_contents = []                
                for index, line in enumerate(contents):
                    if index in replacements:
                        new_contents.extend(newlines[index])
                    else:
                        new_contents.append(line)

                if hasattr(self.nameGenerator, "generateFileName"):
                    filename=self.nameGenerator.generateFileName(# type: ignore
                        parset)  
                else:
                    filename=f"run{unique_name}{file.suffix}"
                self._writeFile(new_contents, filename)
        for name, rule in self._globalRules.items():
            rule.apply(self._folder, self._templates[name]) 
            
if __name__ == '__main__':
    from tstmd import rr_Alice_shell, gr_Alice_slurm
    sm = SimulationGenerator(Path("/Users/koenkeijzer/Documents/generatesimulationstructure/simulation"))

    sm.add_template('py', "./template.py")
    sm.add_template('par', "./template.par")
    sm.add_template('sh', "./template.sh")
    sm.add_template('slurm', "./job.slurm")

    sm.add_replacement_rule('sh', rr_Alice_shell())
    sm.add_global_rule('slurm', gr_Alice_slurm())

    A = Parameters('A', list(range(3)))#, 'py')
    #B = Parameters('B', list(range(3,7)))#, 'py')
    sm.parameters = [(x,) for x in A.values ] #list(itertools.product(A.values, B.values))

    print("Parameters are", sm.parameters, "which are ", len(sm.parameters))

    sm.generate()
