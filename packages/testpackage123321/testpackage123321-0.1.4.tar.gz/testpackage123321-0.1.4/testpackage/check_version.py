from library_exceptions import UnsupportedPythonVersion
import sys

def check_python_version():
    """Checks Python version and raises UnsupportedPythonVersion if incompatible."""
    if not (3.9 <= sys.version_info.major <= 3.11):
        raise UnsupportedPythonVersion()

if __name__ == "__main__":
    try:
        check_python_version()
    except UnsupportedPythonVersion as e:
        print(f"Error: {e}")
        print("This library requires Python 3.9 to 3.11. Please upgrade or downgrade your Python installation.")
        exit(1)  # Indicate an error exit code
