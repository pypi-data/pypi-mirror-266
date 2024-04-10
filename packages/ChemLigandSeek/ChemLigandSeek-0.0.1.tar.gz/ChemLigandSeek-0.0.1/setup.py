from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='ChemLigandSeek',
    version='0.0.1',
    description='hemLigandSeek: A Python tool for rapid ligand-based screening, utilizing the PubChem API to identify potential active candidates for bioassays. Filters out compounds violating Lipinski Rule of Five for optimized drug-like properties.',
    long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='https://github.com/ahmed1212212/ChemLigandSeek.git',
    author='Ahmed Alhilal',
    author_email='aalhilal@udel.edu',
    license='MIT',
    classifiers=classifiers,
    keywords='Cheminformatics',
    packages=find_packages(),
    install_requires=[
        'rdkit',
        'ipython',
        'mordred',
        'glob2',
        'pandas',
        'xgboost',
        'seaborn',
        'numpy',
        'matplotlib',
        'lazypredict',
        'chembl_webresource_client',
        'padelpy',
        'scikit-learn',
        'imblearn',
        'shap',
        'Pillow',
        'skunk',
        'cairosvg',
        'matplotlib-venn',  # Install matplotlib-venn separately if needed
        'statsmodels',
        'pubsams',
        'fastapi',
        'kaleido',
        'python-multipart',
        'uvicorn'
    ]
)
