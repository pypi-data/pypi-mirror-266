from setuptools import setup

file = open('README.md', 'r',encoding='utf-8')
readme = file.read()


setup(
    name='selenium-network-intercept',
    version='0.0.1',
    license='MIT License',
    author='Alexandre Mariano',
    long_description=readme,
    long_description_content_type='text/markdown',
    author_email='alexandre_mariano@hotmail.com.br',
    keywords=['selenium', 'network', 'intercept','http','requests','selenium network intercept','selenium intercept'],
    description='Interceptador de requisições http não oficial do selenium 4',
    packages=['network_intercept'],
    install_requires=[]
)

file.close()