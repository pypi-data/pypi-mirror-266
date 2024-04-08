try:
    from setuptools import setup, find_packages
except ImportError:
    raise ImportError('Please install setuptools.')

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='ib_core_lite',
    version='1.0.0',
    author='Damir Fatkhullin',
    author_email='damir.f@it-psg.com',
    url='https://gitlab.it-psg.com/ib-elp-it-psg/ib_core_lite',
    description='Integration Bus fastapi-applications core',
    download_url='https://gitlab.it-psg.com/ib-elp-it-psg/ib_core_lite.git',
    license='MIT',
    packages=find_packages(),
    package_data={
        'ib_core_lite': ['ib_core_lite/*'],
    },
    install_requires=['fastapi', 'starlette', 'requests'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)