from setuptools import setup, find_packages

setup(
    name='deps-manager',
    version='1.0.0',
    author="Harshada Tupe",
    author_email="harshadatupe8@gmail.com",
    license="MIT",
    packages=find_packages(),
    classifiers=["Programming Language :: Python :: 3 :: Only",
                 "Operating System :: OS Independent"],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'deps-manager = deps_manager.main:cli',
        ],
    },
    install_requires=[
        'click', 
    ],
)