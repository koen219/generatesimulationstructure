import yaml
import itertools


def process_parameters(parameters):
    parameters_ = []
    for name, pars in parameters.items():
        out = []
        for par in pars:
            out.append((name, par))
        parameters_.append(out)
    result = list(itertools.product(*parameters_))
    return result


def generateName(parameters) -> str:
    name = ""
    for par in parameters:
        name += (
            lambda s: (
                s.split(".")[-1]
                if not s.split(".")[-1].isdigit()
                else s.split(".")[-2] + "-" + s.split(".")[-1] + "-"
            )
        )(par[0])
        name += str(par[1]).replace(".", "_")
    return name


def set_nested_value(d, key, value):
    keys = key.split(".")
    for k in keys[:-1]:  # Traverse until the second last key
        if k not in d:
            raise RuntimeError(
                f"Parameter {k} not found! You could check the spelling?"
            )
        d = d[k]  # Move to the next level
    if isinstance(d, list):
        d[int(keys[-1])] = value
    elif isinstance(d, dict):
        d[keys[-1]] = value  # Set the final key to the value
    else:
        raise RuntimeError(f"Setting {d} at {keys[-1]} to {value} did not work.")


def set_value_in_parfile(parfile, parameters):
    for parameter in parameters:
        set_nested_value(parfile, parameter[0], parameter[1])



def main():
    file = "parameters.yaml"
    number_of_cores = 3
    code_dir = "/home/koen/cpm-md/cpmmd/"


    with open(file, "r") as f:
        org_parfile = list(yaml.safe_load_all(f))[0]

    parameters = {
        "cpm.j_matrix.1": [0.5, 0.1, 0.05],
    }
    run_commands = []
    results = process_parameters(parameters)
    for result in results:
        name = generateName(result)

        parfile_name = f"par_{name}.ymmsl"
        datafile_name = f"./data_{name}"

        parfile = org_parfile.copy()
        set_value_in_parfile(parfile, result + [("storage.output_folder", datafile_name)])
        # set_value_in_parfile(parfile, [("storage.output_folder", datafile_name)])

        with open(parfile_name, "w") as f:
            yaml.dump(parfile, f)

        cmd = f"""\
"python {code_dir}/run.py {parfile_name}"\
"""
        run_commands.append(cmd)

    with open("runs.txt", "w") as f:
        for name in run_commands[:-1]:
            f.write(name)
            f.write("\n")
        f.write(run_commands[-1])

    with open("run.sh", "w") as file:
        file.write("chmod +x makemovie.sh\n")
        file.write(f"cat runs.txt | xargs -n 1 -P{number_of_cores} sh -c")



if __name__ == "__main__":
    main()


def generate_files(basepar, params, number_of_cores):
    """This is the only function needed to be implemented in a config.py.

    Args:
    basepar: A path to the baseparameter file.
    params: A list of tuples. Each tuple has another (name, value) tuple.
    number_of_cores: The number of cores that this simulation might use.

    Returns:
    A dictonary with keys filenames and values their substance.
    """

    code_dir = "/home/koen/cpm-md/cpmmd/"

    run_commands = ""

    filenames = []
    filesubstance = []

    with open(basepar, "r") as f:
        org_parfile = list(yaml.safe_load_all(f))[0]

    for par in params:


        # config = ymmsl.load(Path(basepar))
        name = generateName(par)

        filename = f"./par_{name}"
        rundir = f"./data_{name}"

        parfile = org_parfile.copy()
        set_value_in_parfile(parfile, par)
        set_value_in_parfile(parfile,  [("storage.output_folder", rundir)])

        filenames.append(filename + ".yaml")
        filesubstance.append(yaml.dump(parfile))

        # run_command = f'"muscle_manager --run-dir {rundir} --start-all {filename}.ymmsl && TSTplot {rundir} video {rundir}/instances/state_dumper/workdir/ --pde --draw-nascent-adhesions false && sh ./makemovie.sh {rundir}/instances/state_dumper/workdir/ && cp {rundir}/instances/state_dumper/workdir/movie.mp4 ./{filename}.mp4"\n'
        run_command = f"\"python {code_dir}/run.py {filename}.yaml && . {code_dir}/../blender/bin/activate && python {code_dir}/../plot_blender.py video {rundir} && sh makemovie.sh {rundir} && mv {rundir}/movie.mp4 ./mov_{name}.mp4\"\n"
        run_commands += run_command

    makemovie = 'cd $1\nffmpeg -r 10 -pattern_type glob -i "*.png" -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -f mp4 -vcodec libx264 -pix_fmt yuv420p movie.mp4'

    run = f"""
. {code_dir}/../venv/bin/activate
chmod +x makemovie.sh
cat runs.txt | xargs -n 1 -P{number_of_cores} sh -c
"""

    output = {
        "runs.txt": run_commands,
        "makemovie.sh": makemovie,
        "run.sh": run,
    }
    for name, substance in zip(filenames, filesubstance):
        output[name] = substance

    return output

