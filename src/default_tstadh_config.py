import ymmsl


def generateName(parameters) -> str:
    name = ""
    for par in parameters:
        name += par[0].split(".")[-1]
        name += str(par[1]).replace(".", "_")
    return name


from pathlib import Path


def generate_additional_init(name):
    folder = Path(name).resolve()

    (folder / "J.dat").write_text(
        """\
4
0
50 50
50 50 50
50 50 40 50
"""
    )


def generate_files(basepar, params, number_of_cores):
    """This is the only function needed to be implemented in a config.py.

    Args:
    basepar: A path to the baseparameter file.
    params: A list of tuples. Each tuple has another (name, value) tuple.
    number_of_cores: The number of cores that this simulation might use.

    Returns:
    A dictonary with keys filenames and values their substance.
    """

    run_commands = ""

    filenames = []
    filesubstance = []

    for par in params:
        config = ymmsl.load(Path(basepar))
        name = generateName(par)

        filename = f"./par_{name}"
        rundir = f"./data_{name}"

        for p in par:
            config.settings[p[0]] = p[1]
        config.settings["cellular_potts.Jtable"] = str(
            (Path(rundir) / "../J.dat").resolve()
        )
        Path(rundir).mkdir(exist_ok=False)
        filenames.append(filename + ".ymmsl")
        filesubstance.append(ymmsl.dump(config))

        run_command = f'"muscle_manager --run-dir {rundir} --start-all {filename}.ymmsl && TSTplot {rundir} video {rundir}/instances/state_dumper/workdir/ --pde --draw-nascent-adhesions false && sh ./makemovie.sh {rundir}/instances/state_dumper/workdir/ && cp {rundir}/instances/state_dumper/workdir/movie.mp4 ./{filename}.mp4"\n'
        run_commands += run_command

    makemovie = 'cd $1\nffmpeg -r 10 -pattern_type glob -i "*.png" -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -f mp4 -vcodec libx264 -pix_fmt yuv420p movie.mp4'

    run = f"""
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
