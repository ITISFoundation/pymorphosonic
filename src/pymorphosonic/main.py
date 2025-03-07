import logging
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pymorphosonic")

ENVIRONS = ["INPUT_FOLDER", "OUTPUT_FOLDER"]
try:
    input_dir, output_dir = [Path(os.environ.get(v, None)) for v in ENVIRONS]
except KeyError:
    raise ValueError("Required env vars {ENVIRONS} were not set")
OUTPUT_FILE = "output_data.zip"


def copy(src, dest):
    try:
        src, dest = str(src), str(dest)
        shutil.copytree(
            src, dest, ignore=shutil.ignore_patterns("*.zip", "__pycache__", ".*")
        )
    except OSError as err:
        # If the error was caused because the source wasn't a directory
        if err.errno == shutil.errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            logger.error("Directory not copied. Error: %s", err)


def clean_dir(dirpath: Path):
    for root, dirs, files in os.walk(dirpath):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def run_cmd(cmd: str):
    subprocess.run(cmd.split(), shell=False, check=True, cwd=input_dir)
    # TODO: deal with stdout, log? and error??


def unzip_dir(parent: Path):
    for filepath in list(parent.rglob("*.zip")):
        if zipfile.is_zipfile(filepath):
            with zipfile.ZipFile(filepath) as zf:
                zf.extractall(filepath.parent)


def zipdir(dirpath: Path, ziph: zipfile.ZipFile):
    """Zips directory and archives files relative to dirpath"""
    for root, dirs, files in os.walk(dirpath):
        for filename in files:
            filepath = os.path.join(root, filename)
            ziph.write(filepath, arcname=os.path.relpath(filepath, dirpath))
        dirs[:] = [name for name in dirs if not name.startswith(".")]


def ensure_main_entrypoint(code_dir: Path) -> Path:
    code_files = list(code_dir.rglob("*.py"))

    if not code_files:
        raise ValueError("No python code found")

    if len(code_files) > 1:
        code_files = list(code_dir.rglob("main.py"))
        if not code_files:
            raise ValueError("No entrypoint found (e.g. main.py)")
        if len(code_files) > 1:
            raise ValueError(f"Many entrypoints found: {code_files}")

    main_py = code_files[0]
    return main_py


def ensure_requirements(code_dir: Path) -> Path:
    requirements = list(code_dir.rglob("requirements.txt"))
    if len(requirements) > 1:
        raise ValueError(f"Many requirements found: {requirements}")

    elif not requirements:
        # deduce requirements using pipreqs
        logger.info("Not found. Recreating requirements ...")
        requirements = code_dir / "requirements.txt"
        run_cmd(f"touch {requirements}")
    else:
        requirements = requirements[0]
    return requirements


def setup():
    logger.info("Cleaning output ...")
    clean_dir(output_dir)

    # TODO: snapshot_before = list(input_dir.rglob("*"))

    # NOTE The inputs defined in ${INPUT_FOLDER}/inputs.json are available as env variables by their key in capital letters
    # For example: input_1 -> $INPUT_1
    #
    
    logger.info("Processing input ...")
    unzip_dir(input_dir)

    # logger.info("Copying input to output ...")
    # copy(input_dir, code_dir)

    logger.info("Searching main entrypoint ...")
    main_py = ensure_main_entrypoint(input_dir)
    logger.info("Found %s as main entrypoint", main_py)

    logger.info("Searching requirements ...")
    requirements_txt = ensure_requirements(input_dir)

    logger.info("Preparing launch script ...")
    venv_dir = Path.home() / ".venv"
    # TODO: pipreqs tries to download XCore. Can that be avoided?
    script = [
        "#!/bin/sh",
        "set -o errexit",
        "set -o nounset",
        "IFS=$(printf '\\n\\t')",
        'echo "Creating virtual environment ..."',
        f'python3 -m venv --system-site-packages --symlinks --upgrade "{venv_dir}"',
        f'echo Installing requirements from "{requirements_txt}"',
        f"echo Currently installed packages:",
        f'"{venv_dir}"/bin/pip list',
        f'"{venv_dir}"/bin/pip install -r "{requirements_txt}"',
        f'echo "Executing code {main_py.name}"...',
        f'"{venv_dir}"/bin/python3 "{main_py}"',
        'echo "DONE ..."',
    ]
    main_script_path = Path("main.sh")
    logger.info(f"Trying to create file in {main_script_path.absolute()}")
    with main_script_path.open("w") as fp:
        for line in script:
            print(f"{line}\n", file=fp)

    # # TODO: take snapshot
    # logger.info("Creating virtual environment ...")
    # run_cmd("python3 -m venv --system-site-packages --symlinks --upgrade .venv")
    # run_cmd(".venv/bin/pip install -U pip wheel setuptools")
    # run_cmd(f".venv/bin/pip install -r {requirements}")

    # # TODO: take snapshot
    # logger.info("Executing code ...")
    # run_cmd(f".venv/bin/python3 {main_py}")


def teardown():
    logger.info("Zipping output ....")

    # TODO: sync zipped name with docker/labels/outputs.json
    with tempfile.TemporaryDirectory() as tmpdir:
        zipped_file = Path(f"{tmpdir}/{OUTPUT_FILE}")
        with zipfile.ZipFile(str(zipped_file), "w", zipfile.ZIP_DEFLATED) as zh:
            zipdir(output_dir, zh)

        logger.info("Cleaning output")
        clean_dir(output_dir)

        logger.info("Moving %s", zipped_file.name)
        shutil.move(str(zipped_file), str(output_dir))


if __name__ == "__main__":
    action = "setup" if len(sys.argv) == 1 else sys.argv[1]
    try:
        if action == "setup":
            setup()
        else:
            teardown()
    except Exception as err:  # pylint: disable=broad-except
        logger.error("%s . Stopping %s", err, action)