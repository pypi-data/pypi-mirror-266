import setuptools
requirements = []
setuptools.setup(
    name='discord_check',
    version='1.0.3',
    install_requires=requirements,
    description = 'A module check token discord active',
    packages=setuptools.find_packages(),
    long_description=open('README').read(),
    long_description_content_type='text/markdown',
    project_urls={
        'GitHub': 'https://github.com/desotana/discord_check/',
    },
)
