from setuptools import setup

readme = ''
with open('README.md') as f:
    readme = f.read()

setup(name='Liacord',
      author="Masezev",
      url="https://github.com/masezev/Liacord.py",
      project_urls={
          'Discord': 'https://discord.gg/H7FQFGEPz5',
      },
      repository='https://github.com/masezev/Liacord.py',
      version='0.1.5',
      description='A Python wrapper for the Discord API',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      packages=['Liacord'],
      license='MIT',
      author_email='csgomanagement1@gmail.com',
      zip_safe=False)
