from setuptools import setup, find_packages

setup(
    name='TuringCoder',
    version='0.1.0',
    author='FukjemiCZ',
    author_email='turing.coder@fukjemi.cz',
    packages=find_packages(exclude=['DemoApp', 'docs']),
    include_package_data=True,
    url='https://github.com/FukjemiCZ/TuringCoder',
    license='LICENSE',
    description='TuringCoder is an innovative Python application designed to streamline your workflow through automations, leveraging the power of OpenAI\'s GPT models. Whether you\'re organizing your project files, processing text data, or integrating AI-based text generation, DemoApp offers a flexible solution tailored to various needs.',
    long_description=open('Readme.md').read(),
    long_description_content_type='text/markdown',  # Přidej tento řádek
    install_requires=[
        "requests",
        "json5"
    ],
    entry_points={
        'console_scripts': [
            'turingcoder=.main:main',
        ],
    }
)
