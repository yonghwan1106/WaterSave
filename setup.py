from setuptools import setup, find_packages

   setup(
       name='watersave',
       version='0.1',
       packages=find_packages(),
       install_requires=[
           'streamlit>=1.22.0',
           'pandas>=1.5.3',
           'numpy>=1.24.3',
           'plotly>=5.10.0',
       ],
   )