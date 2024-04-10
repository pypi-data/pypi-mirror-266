from setuptools import setup,find_packages
from datetime import datetime
version='0.4.48'

setup(name='MobileInventoryCLI',
      version=version,
      author="Carl Joseph Hirner III",
      author_email="k.j.hirner.wisdom@gmail.com",
      description="modify/update/use MobileInventoryPro *.bck files",
      classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',

          ],
      packages=find_packages(),
      python_requires='>=3.6',
      install_requires=['cython','pint','pyupc-ean','openpyxl','plyer','colored','numpy','pandas','Pillow','python-barcode','qrcode','requests','sqlalchemy','argparse','geocoder'],
      package_data={
        '':["*.config","*.txt","*.README","*.TTF"],
        }
      )

