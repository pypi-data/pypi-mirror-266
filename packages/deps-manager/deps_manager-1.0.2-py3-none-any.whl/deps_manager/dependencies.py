"""
This module handles all dependency management operations based on the language.
"""

# Python standard library imports
import subprocess

# Local application imports
from .utils import handle_error


@handle_error
def install_dependencies(requirements_file, language, venv_path):
    """
    Installs dependencies.
    """
    if language == 'python':
        pip_executable = 'pip'
        if venv_path:
            pip_executable = f"{venv_path}/bin/pip"  # For Linux and MacOS
        subprocess.run([pip_executable, 'install', '-r', requirements_file], check=True)
    
    elif language == 'cpp':
        subprocess.run(['conan', 'install', '-r', requirements_file], check=True)

@handle_error
def uninstall_dependency(package, language, venv_path):
    """
    Uninstalls dependencies.
    """
    if language == 'python':
        pip_executable = 'pip'
        if venv_path:
            pip_executable = f"{venv_path}/bin/pip"  # For Linux and MacOS
        subprocess.run([pip_executable, 'uninstall', '-y', package], check=True)
    elif language == 'cpp':
        subprocess.run(['conan', 'uninstall', '-y', package], check=True)

@handle_error
def list_dependencies(language, venv_path):
    """
    Lists dependencies.
    """
    if language == 'python':
        pip_executable = 'pip'
        if venv_path:
            pip_executable = f"{venv_path}/bin/pip"  # For Linux and MacOS
        subprocess.run([pip_executable, 'list'], check=True)
    elif language == 'cpp':
        subprocess.run(['conan', 'list'], check=True)

@handle_error
def update_dependencies(requirements_file, language, venv_path):
    """
    Updates dependencies.
    """
    if language == 'python':
        pip_executable = 'pip'
        if venv_path:
            pip_executable = f"{venv_path}/bin/pip"  # For Linux and MacOS
        subprocess.run([pip_executable, 'install', '--upgrade', '-r', requirements_file], check=True)
    elif language == 'cpp':
        subprocess.run(['conan', 'update', '-r', requirements_file], check=True)

@handle_error
def lock_dependencies(requirements_lock_file, language, venv_path):
    """
    Build a lockfile to lock current dependencies.
    """
    if language == 'python':
        if venv_path:
            python_executable = f"{venv_path}/bin/python"
            # requirements_file = f"{venv_path}/../{requirements_lock_file}"
            subprocess.run([f"{venv_path}/bin/pip", "freeze"], stdout=open(requirements_lock_file, "w"), check=True)
    elif language == 'cpp':
        subprocess.run(['conan', 'lock', '-r', requirements_lock_file, '-o', lock_file], check=True)
