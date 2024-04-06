from setuptools import setup, find_namespace_packages
from os.path import join, dirname
import HA_cfg_cleaner_DiosWolf


setup(
    name="HA_cfg_cleaner_DiosWolf",
    version=HA_cfg_cleaner_DiosWolf.__version__,
    packages=find_namespace_packages(),
    long_description=open(join(dirname(__file__), "README.txt")).read(),
    entry_points={
        "console_scripts": ["ha_cleaner = HA_cfg_cleaner_DiosWolf.main:start_script"]
    },
    install_requires=[
        "ruamel.yaml==0.18.5",
        "dacite==1.8.1",
        "requests==2.31.0",
        "setuptools==69.0.3",
    ],
    include_package_data=True,
)
