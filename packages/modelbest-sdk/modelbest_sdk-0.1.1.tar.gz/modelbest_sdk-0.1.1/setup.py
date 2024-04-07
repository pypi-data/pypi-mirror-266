from setuptools import setup, find_packages

setup(
    name='modelbest_sdk',
    version='0.1.1',
    author='HankyZhao',
    author_email='zhq980115@gmail.com',
    description='Everything about modelbest data include data format mbtable, dataset, dataloader, and tools',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://codeup.aliyun.com/64ddb0a87f62ff9b3d23ca15/modelbest_sdk',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
