from setuptools import setup, find_packages

setup(
    name='growupmore_utils',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='A utility package for common functionalities.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'Django>=5.0.4',
        'djangorestframework>=3.15.1',
        'django-user-agents>=0.4.0',
    ],
    url='https://github.com/girishinindia/test',
    author='Girish Chaudhary',
    author_email='girishinindia@gmail.com',
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
)