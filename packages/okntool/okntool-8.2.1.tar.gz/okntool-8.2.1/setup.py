from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

long_description = 'Command line program to draw okn related graphs.'

setup(
    name='okntool',
    version='8.2.1',
    author='Zaw Lin Tun',
    author_email='zawlintun1511@gmail.com',
    url='https://github.com/jtur044/okntool',
    description='OKN related graphs drawing program',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache Software",
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['oknserver_graph_plot_config.json',
                       'simpler_plot_config.json',
                       'indi_va_table_template.html',
                       'sum_va_table_template.html']},
    entry_points={
        'console_scripts': [
            'okntool = okntool.okntool:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords='OKN related graphs drawing program',
    install_requires=requirements,
    zip_safe=False
)
