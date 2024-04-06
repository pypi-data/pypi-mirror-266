from setuptools import setup, find_packages
from subprocess import call

VERSION = '0.0.1'
DESCRIPTION = 'PythonTutorial'
LONG_DESCRIPTION = 'A package to convert an image to pencil sketch'

# Setting up
setup(
    name="PencilSketch",
    version=VERSION,
    author="Shakthibala",
    author_email="shakthibala2004@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['imageio', 'matplotlib', 'numpy', 'scipy'],
    keywords=['python', 'tutorial', 'PencilSketch', 'Sketch', 'ImageSketch'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

# Uploading the package to PyPI
try:
    username = "__token__"
    password = "pypi-AgEIcHlwaS5vcmcCJGEyZDM0OTM2LTg3NDctNDY0OC04MDRmLTkzMGUxYTU0YmUxMwACKlszLCJhZmI5NjczNS00ODlhLTRmNDEtYWM0My0wNzkyZjcwNjliZTYiXQAABiAjA2m0Ll0dn2VV__UL2Y0zz0j_PSxNJXXCJ8PSwNwkkQ"
    call(f'twine upload --username {username} --password {password} dist/*', shell=True)
except Exception as e:
    print("Error uploading the package:", e)
