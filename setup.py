from setuptools import setup,find_packages

requires = (
        'Flask',
        )

setup(
    name='cocoProject',
    version='1.0',
    author='Carlos Tezna',
    author_email='coco.project3@gmail.com',
    description='Client controller for Coco Project "Coco" Device',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)