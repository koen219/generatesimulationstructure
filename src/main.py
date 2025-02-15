import os
import shutil
import yaml
import importlib.util
import click

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

    # Copy parameters.ymmsl from the template
    param_src = os.path.join(template_path, "parameters.ymmsl")
    param_dst = os.path.join(name, "parameters.ymmsl")
    if os.path.exists(param_src):
        shutil.copy(param_src, param_dst)
    else:
        click.echo(f"Warning: parameters.ymmsl missing in template '{template}'.")

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
def create(folder):
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

    # Load config.py from the template folder
    config_py_path = os.path.join(template_path, "config.py")
    if not os.path.exists(config_py_path):
        click.echo(f"Error: config.py missing in template '{template}'.", err=True)
        return

    spec = importlib.util.spec_from_file_location("config_module", config_py_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    # Call the function in config.py
    param_list = list(config.items())
    generated_files = config_module.generate_files(param_list)

    # Write output files
    for filename, content in generated_files.items():
        output_path = os.path.join(folder, filename)
        with open(output_path, "w") as f:
            f.write(content)

    click.echo(f"Generated {len(generated_files)} files in '{folder}'.")


@cli.command()
@click.option("--name", required=True, help="Name of the new template")
def add(name):
    """Add a new template for simulations."""
    new_template_path = os.path.join(TEMPLATE_DIR, name)
    os.makedirs(new_template_path, exist_ok=True)

    param_path = os.path.join(new_template_path, "parameters.ymmsl")
    config_py_path = os.path.join(new_template_path, "config.py")

    # Create default parameters.ymmsl if missing
    if not os.path.exists(param_path):
        with open(param_path, "w") as f:
            f.write("# Default parameters file\n")

    # Create default config.py if missing
    if not os.path.exists(config_py_path):
        with open(config_py_path, "w") as f:
            f.write(
                "def generate_files(params):\n"
                "    return {'example.txt': 'This is a default generated file.'}\n"
            )

    click.echo(f"Template '{name}' added successfully.")


if __name__ == "__main__":
    cli()
