from setuptools import setup, find_packages


VERSION = '1.0.0'
DESCRIPTION = "A Python library for customizable text printing in the terminal."


# Setting up
setup(
    name="ArtisanPrint",
    version=VERSION,
    author="Naman Garg",
    author_email="edu.ngarg@gmail.com",
    description=DESCRIPTION,
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/Naman-0206/ArtisanPrint',
    project_urls={
        "Bug Tracker": "https://github.com/Naman-0206/ArtisanPrint/issues"
    },
    license='MIT',
    keywords=[
        'text',
        'printing',
        'colors',
        'styles',
        'terminal',
        'formatting',
        'ANSI',
        'console',
        'output',
        'CLI',
        'developer',
        'tool',
        'utility',
        'Python',
        'library',
        'package',
        'customization',
        'enhancement',
        'programming',
        'development'
    ],
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
