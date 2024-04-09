from setuptools import setup, find_packages

setup(
    name="AnonymixTicket",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "transformers",
        "torch",
        "gradio",
        "pandas",
    ],
    package_data={"AnonymixTicket": ["data/logo.png"]},
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'launch_redactpii=AnonymixTicket.gradio_app:main',
        ],
    },
)
