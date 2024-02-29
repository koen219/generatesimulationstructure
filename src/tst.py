from .simulationgenerator import Parameter, Tuple, Path
from dataclasses import dataclass
from typing import List


class rr_Alice_shell:
    def apply(self, line: str, parset: Tuple[Parameter, ...], unique_name: str):
        print(f"Being applied to {line}")
        if line == "newtemplate":
            return [f"newtemplate=para_{unique_name}"]
        elif line == "DATADIR":
            data_folder = "${DATADIRPATH}/" + f"data-{unique_name}/"
            parameterfile = f"para_{unique_name}"
            return [
                f"DATADIR=data-{unique_name}\n",
                f"echo \"datadir = {data_folder}\" >> {parameterfile}.par\n",
            ]
        elif line == "TAR":
            return [f"TAR=run{unique_name}\n"]
        elif line == "PARAMETERS":
            out = []
            for par in parset:
                name = par.name
                value = par.value
                out.append(
                    f"echo \"{name[3:]} = {value}\" >> " + "${newtemplate}.par\n")
            return out
        else:
            raise RuntimeError(f"Parsing line\n----{line}\n----\nis not implemented")

@dataclass
class _LineRule:
    name: str
    command: str
    value: str

class gr_Alice_slurm:
        def __init__(self):
            self._linerules: List[_LineRule] = []

        def apply(self, folder: Path, templatefile: Path):
            jobs = [str(file.name) + '\n' for file in folder.glob("run*sh")]
            with open(folder / 'jobs', 'w') as file:
                file.writelines(jobs)
            self.set_numberOfJobs(len(jobs))
            with open(templatefile, 'r') as file:
                writeLines = []
                for line in file.readlines():
                    writeLines.append(self._parseLine(line))
#                    if line.startswith("#SBATCH --array"):
#                        writeLines.append(f"#SBATCH --array=1-{numberOfJobs}\n")
#                        continue
            
            with open(templatefile, 'w') as file:
                file.writelines(writeLines)
        def _parseLine(self, line: str):
            """
            Reads line and checks if it needs to be replaced, if so returns replaced line. Otherwise returns original line.
            """
            for rule in self._linerules:
                if line.startswith(rule.command):
                    return rule.value
            return line

        def set_numberOfJobs(self, number):
            self._linerules.append(
                _LineRule('numberOfJobs', 
                          '#SBATCH --array',
                          f"#SBATCH --array=1-{number}\n"
                    )
                )

        def set_time(self, time):
            self._linerules.append(
                _LineRule('time', 
                          '#SBATCH --time',
                          f"#SBATCH --time={time}\n"
                    )
                )
        def set_node(self, node):
            # TODO: Automatically add gpu node
            value = f"#SBATCH --partition=\"{node}\"\n"
            if 'gpu' in node:
                value += "#SBATCH --gpus=1\n"
        
            self._linerules.append(
                _LineRule('time', 
                          '#SBATCH --partition',
                          value
                    )
                )

class rr_Local:
    def __init__(self, folder):
        self._folder = folder
    def apply(self, line: str, parset: Tuple[Parameter, ...], unique_name:str)->List[str]:
        data_folder = f"{self._folder}/data-{unique_name}"
        parfile = f"par_{unique_name}"
        if line == 'INIT':
            return [
                f'DATAFOLDER="{data_folder}/"\n',
                f'PARFILE={parfile}\n'
                    ]

        if line == 'PARAMETERS':
            out = [ ]
            for par in parset:
                    name = par.name
                    value = par.value
                    out.append(
                        f"echo \"{name[3:]} = {value}\" >> " + "${PARFILE}.par\n")
            return out
        raise NotImplementedError()

