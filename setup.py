from setuptools import setup, find_packages


setup(
    name='MIPTario',
    version='0.0.1',
    description='Mario game for MIPT ',
    long_description="See Description as README.md",
    long_description_content_type='text/markdown',
    author='editus',
    packages=find_packages(where='src'),
    python_requires='>=2.3, <2.7',
    install_requires=['pygame','pysqlite']
)


print("""__  __     _____ _____ _______ 
        |  \/       |_   _|  __ \__   __|
        | \  /      | | | | |__) | | |
        | |\/|      | | | |  ___/  | |
        | |  |      |_| |_| |      | | 
        |_|  |_ario|_____|_|      |_|  
        """)

