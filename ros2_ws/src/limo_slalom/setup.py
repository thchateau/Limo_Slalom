from glob import glob
import os

from setuptools import find_packages, setup


package_name = 'limo_slalom'


setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
         glob(os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'worlds'),
         glob(os.path.join('worlds', '*.world'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Thierry Chateau',
    maintainer_email='thchateau@users.noreply.github.com',
    description='Starter package for the Limo slalom hackathon.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'scan_observer = limo_slalom.scan_observer:main',
        ],
    },
)
