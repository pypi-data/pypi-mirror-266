from setuptools import setup, find_packages

setup(
    name="Anonymizer-ticket",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "transformers",
        "torch",
        "gradio",
        "pandas",
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'my_package=my_package.gradio_app:main',
        ],
    },
)
