from setuptools import setup, find_packages

setup(
    name='pluginTest',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'mkdocs'
    ],
    entry_points={
        'mkdocs.plugins': [
            'pluginTest = pluginTest.plugin:BadgesPlugin'
        ]
    },
    python_requires='>=3.5'
)