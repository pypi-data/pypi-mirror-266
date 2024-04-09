from setuptools import setup

setup(name='SdcStatsBot',
      author="Masezev",
      url="https://github.com/masezev/SdcStatsBot",
      project_urls={
          'Поддержка': 'https://discord.gg/H7FQFGEPz5',
      },
      repository='https://github.com/masezev/SdcStatsBot',
      version='0.2.1',
      description='A Python wrapper for the SDC API',
      python_requires='>=3.8.0',
      keywords='A Python wrapper for the SDC API',
      install_requires=[
            'aiohttp',
            'disnake',
            'loguru'
      ],
      packages=['SDcStatsBot'],
      author_email='csgomanagement1@gmail.com',
      zip_safe=False)
