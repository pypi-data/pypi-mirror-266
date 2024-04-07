from setuptools import setup, find_packages

setup(
    name='qleegss',
    version='0.0.11',
    keywords='eeg sleep staging analysis',
    description='a python analyse tool for LM Data Recorder data',
    license='MIT License',
    url='https://github.com/eegion/qleegss',
    author='zhd',
    author_email='shrugor@163.com',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=['scipy', 'numpy', 'torch', 'tqdm', 'lspopt', 'pandas', 'reportlab', 'openpyxl', 'matplotlib'],
)
