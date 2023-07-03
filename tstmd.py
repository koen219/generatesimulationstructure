from .simulationgenerator import Parameter, Tuple, Path


class rr_Alice_shell:
    def apply(self, line: str, parset: Tuple[Parameter, ...], unique_name: str):
        print(f"Being applied to {line}")
        if line == "newtemplate":
            return [f"newtemplate=para_{unique_name}"]
        elif line == "DATADIR":
            data_folder = "${DATADIRPATH}/" + f"data-{unique_name}/"
            parameterfile = f"para_{unique_name}"
            return [
                f"DATADIR={data_folder}\n",
                f"echo \"datadir = {data_folder}\" >> {parameterfile}.par\n",
                f"echo \"storeprefix='{data_folder}'\" >> {parameterfile}.py\n",
                f"echo \"parfile = '{parameterfile}.par'\" >> {parameterfile}.py\n",
            ]
        elif line == "TAR":
            return [f"TAR=run{unique_name}\n"]
        elif line == "PARAMETERS":
            out = []
            for par in parset:
                name = par.name
                value = par.value
                if name.startswith('par'):
                    out.append(
                        f"echo \"{name[3:]} = {value}\" >> " + "${newtemplate}.par\n")
                else:
                    out.append(
                        f"echo \"{name} = {value}\" >> " + "${newtemplate}.py\n")
            return out
        else:
            raise NotImplemented(
                f"Parsing line\n----{line}\n----\nis not implemented")

class gr_Alice_slurm:
        def apply(self, folder: Path, templatefile: Path):
            jobs = [str(file.name) + '\n' for file in folder.glob("run*sh")]
            with open(folder / 'jobs', 'w') as file:
                file.writelines(jobs)
            numberOfJobs = len(jobs)
            with open(templatefile, 'r') as file:
                writeLines = []
                for line in file.readlines():
                    if line.startswith("#SBATCH --array"):
                        writeLines.append(f"#SBATCH --array=1-{numberOfJobs}\n")
                        continue
                    writeLines.append(line)
            
            with open(templatefile, 'w') as file:
                file.writelines(writeLines)
