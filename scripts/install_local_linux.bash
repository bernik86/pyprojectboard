#!/usr/bin/bash

VERSION="2.0.0a1"
echo "Automatic installation for pyprojectboard V$VERSION"

DIR=$(basename "$(realpath .)")

if [ "$DIR" = "scripts" ]; then
  cd ..
fi

DIR=$(basename "$(realpath .)")
if [ "$DIR" != "pyprojectboard" ]; then
    echo "ERROR: Does not seem to be in the correct directory!"
    echo "Make sure you run this script in the root directory of the github repo."
    exit 1
fi

if [ ! -f ./pyproject.toml ]; then
    echo "ERROR: Cannot find pyproject.toml. Aborting installation!"
    echo "Make sure you run this script in the root directory of the github repo."
    exit 1
fi

if [ ! -f ./src/main.py ]; then
    echo "ERROR: Cannot find main.py. Aborting installation!"
    echo "Make sure you run this script in the root directory of the github repo."
    echo 1
fi

install_deps () {
    # Install dependencies for Debian 12.7
    if command -v apt
    then
        echo "Running: sudo apt install python3.11-venv libxcb-cursor-dev"
        sudo apt install python3.11-venv libxcb-cursor-dev
    fi
}

create_venv () {

    python -m venv --copies .env
    # shellcheck source=/dev/null
    . .env/bin/activate
    pip install .
}

link_bin () {

    BIN=$(realpath ./bin/pyprojectboard.bash)
    MAIN=$(realpath ./src/main.py)
    PYENV=$(realpath .env/bin/activate)

    mkdir -p bin
    {
        echo '#!/usr/bin/bash'
        echo ". $PYENV"
        echo "python $MAIN"
        echo "deactivate"
    } > "$BIN"

    chmod u+x "$BIN"

    mkdir -p "$HOME"/.local/bin
    cd "$HOME"/.local/bin || exit 1
    ln -s "$(realpath --relative-to="$HOME"/.local/bin "$BIN")" pyprojectboard
    echo "pyprojectboard $VERSION binary was installed to: $HOME/.local/bin"
    echo "Make sure that this directory is in your PATH variable!"
    echo "This is the current content of your PATH variable:"
    echo "$PATH"
}

install_deps
create_venv
link_bin
