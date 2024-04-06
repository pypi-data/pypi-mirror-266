# Kite Connect Lite Package

This project uses Poetry for dependency management and packaging.

## Prerequisites

Before getting started, ensure that you have the following installed on your system:

-   Python (version X.X.X)
-   pipx (version X.X.X) ( `brew install pipx` )

## Installation

1. Install Poetry using pipx:

    ```bash
    pipx install poetry
    ```

    pipx is a tool that allows you to install and run Python applications in isolated environments. By installing Poetry with pipx, you ensure that it doesn't interfere with other Python projects on your system.

2. Clone the repository

3. Navigate to the project directory
4. Install the project dependencies using Poetry:

    ```bash
    poetry install
    ```

    This command reads the `pyproject.toml` file and installs all the required dependencies in a virtual environment specific to the project.

## Running the Project

To run the Python file using Poetry, follow these steps:

1. Ensure that you are in the project directory
2. Activate the virtual environment created by Poetry:

    ```bash
    poetry shell
    ```

    This command spawns a shell with the virtual environment activated.

3. Run the Python file:

    ```bash
    python relative_path_to_your_script.py
    ```

    Replace `relative_path_to_your_script.py` with the actual relative path of your Python file.

    Alternatively, you can run the Python file without activating the virtual environment by using the `poetry run` command:

    ```bash
    poetry run python relative_path_to_your_script.py
    ```

    This command executes the Python file within the context of the virtual environment managed by Poetry.

## Additional Commands

Here are a few additional Poetry commands that you might find useful:

-   `poetry add <package>`: Adds a new dependency to the project.
-   `poetry update`: Updates the project dependencies to their latest versions.
-   `poetry remove <package>`: Removes a dependency from the project.
-   `poetry show`: Lists all the installed packages and their versions.
