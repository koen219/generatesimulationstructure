import os
import shutil
import yaml
import importlib.util
from pathlib import Path
import click
from .parse import parse_parameter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(SCRIPT_DIR, "../templates")


@click.group()
def cli():
    """Gensim: Simulation File Generator"""
    pass


@cli.command()
@click.option("--name", required=True, help="Name of the simulation folder")
@click.option("--template", required=True, help="Template to use")
def new(name, template):
    """Create a new simulation folder with parameters."""
    template_path = os.path.join(TEMPLATE_DIR, template)
    if not os.path.isdir(template_path):
        click.echo(f"Error: Template '{template}' not found.", err=True)
        return

    os.makedirs(name, exist_ok=True)

    # Copy baseparameters from the template
    param_src = os.path.join(template_path, "baseparameters")
    param_dst = os.path.join(name, "baseparameters")
    if os.path.exists(param_src):
        shutil.copy(param_src, param_dst)
    else:
        click.echo(f"Warning: baseparameters missing in template '{template}'.")

    config_py_path = os.path.join(template_path, "config.py")
    spec = importlib.util.spec_from_file_location("config_module", config_py_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    # Some setups, such as the TST, do not put all their parameters in a single file.
    # This additional function, creates the new parameterfile from config.py
    if hasattr(config_module, "generate_additional_init"):
        config_module.generate_additional_init(name)

    # Generate config.yaml
    # config_data = {"template": template, "search": {}, "with": {}}
    config_path = os.path.join(name, "config.yaml")
    with open(config_path, "w") as f:
        yaml.dump({"template": template}, f, default_flow_style=False)
        yaml.dump({"with": {}}, f, default_flow_style=False)
        yaml.dump({"search": {}}, f, default_flow_style=False)

    click.echo(f"Created simulation '{name}' using template '{template}'.")


@cli.command()
@click.argument("folder")
@click.option("--number_of_cores", type=int)
def create(folder, number_of_cores):
    """Generate simulation files based on config."""
    config_path = os.path.join(folder, "config.yaml")
    if not os.path.exists(config_path):
        click.echo("Error: config.yaml not found in the specified folder.", err=True)
        return

    # Load config.yaml
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    template = config.get("template")
    template_path = os.path.join(TEMPLATE_DIR, template)
    if not os.path.isdir(template_path):
        click.echo(f"Error: Template '{template}' not found.", err=True)
        return

    basepar_path = Path(os.path.join(folder, "baseparameters")).resolve()
    if not basepar_path.exists():
        click.echo(f"Error: baseparameters not found in specified folder", err=True)
        return

    # Load config.py from the template folder
    config_py_path = os.path.join(template_path, "config.py")
    if not os.path.exists(config_py_path):
        click.echo(f"Error: config.py missing in template '{template}'.", err=True)
        return

    spec = importlib.util.spec_from_file_location("config_module", config_py_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    if not number_of_cores:
        if "number_of_cores" in config:
            number_of_cores = config.get("number_of_cores")
        else:
            click.echo(
                f"No 'number_of_cores' specified as argument or in 'config.yaml'"
            )
            return

    # Call the function in config.py
    param_list = parse_parameter(config)  # list(config.items())
    generated_files = config_module.generate_files(
        basepar_path, param_list, number_of_cores
    )

    # Write output files
    for filename, content in generated_files.items():
        output_path = os.path.join(folder, filename)
        with open(output_path, "w") as f:
            f.write(content)

    click.echo(
        f"Generated {len(generated_files)} files in '{folder}' given {len(param_list)} parameter combinations."
    )


@cli.command()
@click.option("--name", required=True, help="Name of the new template")
@click.option(
    "--config",
    required=True,
    help="Name of the configuration file to use or of the template that has already a config.py",
)
@click.option("--par", required=True, help="Name of parameter file to use")
def add(name, config, par):
    """Add a template to be used for new simulations."""
    template_path = os.path.join(TEMPLATE_DIR, name)

    # Create template directory
    os.makedirs(template_path, exist_ok=True)

    # Determine the source for config.py
    config_source = None
    if os.path.isfile(config):
        config_source = config  # Direct file path
    elif os.path.isdir(os.path.join(TEMPLATE_DIR, config)):
        existing_template = os.path.join(TEMPLATE_DIR, config, "config.py")
        if os.path.isfile(existing_template):
            config_source = existing_template  # Copy from existing template
    else:
        click.echo(
            f"Error: {config} is not a valid file or existing template", err=True
        )
        return

    # Copy config.py
    config_dest = os.path.join(template_path, "config.py")
    shutil.copy(config_source, config_dest)

    # Copy baseparameters
    if not os.path.isfile(par):
        click.echo(f"Error: Parameter file {par} not found", err=True)
        return

    shutil.copy(par, os.path.join(template_path, "baseparameters"))

    click.echo(f"Template '{name}' added successfully.")


@cli.command()
@click.option("--name", required=True, help="Name of template to change")
@click.option("--par", required=False, help="Name of parameter file to change")
@click.option("--config", required=False, help="Name of config to change")
def update(name, config, par):
    template_path = os.path.join(TEMPLATE_DIR, name)
    if not os.path.exists(template_path):
        click.echo(f"Template '{name}' does not exists!", err=True)
        return

    if config is None and par is None:
        click.echo(
            f"Specify '--config' or '--par' to change the config.py file or the 'baseparameters' parameter file.",
            err=True,
        )
        return

    if config and not os.path.exists(config):
        click.echo(f"Can not find config file '{config}'", err=True)
        return

    if par and not os.path.exists(par):
        click.echo(f"Can not find par file '{par}'", err=True)
        return

    if config:
        config_dest = os.path.join(template_path, "config.py")
        shutil.copy(config, config_dest)
        click.echo("Updated config file")

    if par:
        par_dest = os.path.join(template_path, "baseparameters")
        shutil.copy(par, par_dest)


@cli.command()
@click.option("--name", required=True, help="Name of template to remove")
def remove(name):
    """Remove a template."""
    template_path = os.path.join(TEMPLATE_DIR, name)
    if not os.path.exists(template_path):
        click.echo(f"Template '{name}' does not exists!", err=True)
        return

    shutil.rmtree(template_path)


@cli.command()
def list():
    """List all templates."""
    click.echo("Current templates are:")
    for name in [f.name for f in os.scandir(TEMPLATE_DIR) if f.is_dir()]:
        click.echo(f" - {name}")


if __name__ == "__main__":
    cli()
