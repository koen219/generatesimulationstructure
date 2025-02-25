import yaml
import itertools

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


def generate_files(basepar, params, number_of_cores):
    """This is the only function needed to be implemented in a config.py.

    Args:
    basepar: A path to the baseparameter file.
    params: A list of tuples. Each tuple has another (name, value) tuple.
    number_of_cores: The number of cores that this simulation might use.

    Returns:
    A dictonary with keys filenames and values their substance.
    """

    code_dir = "/home/koen/cpm-md/"

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
        # run_command = f"\"python {code_dir}/run.py {filename}.yaml && . {code_dir}/../blender/bin/activate && python {code_dir}/../plot_blender.py video {rundir} && sh makemovie.sh {rundir} && mv {rundir}/movie.mp4 ./mov_{name}.mp4\"\n"
        run_command = f"\"cpmmd {filename}.yaml && sh makemovie.sh {rundir} && mv {rundir}/movie.mp4 ./mov_{name}.mp4\"\n"
        run_commands += run_command

    makemovie = f"""\
. {code_dir}/.blender/bin/activate
cd $1
python {code_dir}/src/scripts/plot_blender.py video .
ffmpeg -r 10 -pattern_type glob -i "*.png" -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -f mp4 -vcodec libx264 -pix_fmt yuv420p movie.mp4
"""

    run = f"""
. {code_dir}/.venv/bin/activate
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

