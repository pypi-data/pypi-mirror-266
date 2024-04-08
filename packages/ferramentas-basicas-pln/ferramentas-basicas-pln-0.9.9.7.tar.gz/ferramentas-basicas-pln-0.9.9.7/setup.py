from setuptools import setup, find_packages

with open(r'README.md','r',encoding='utf-8') as f:
    descricao_longa = f.read()

setup(
    name='ferramentas-basicas-pln',
    version='0.9.9.7',
    packages=find_packages(),
    install_requires = ['regex'],
    description='Kit de ferramentas para processos básicos de Processamento de Linguagem Natural.',
    long_description=descricao_longa,
    long_description_content_type="text/markdown",
    author='Igor Caetano de Souza',
    project_urls={
        "GitHub Repository":"https://github.com/IgorCaetano/ferramentas_basicas_pln"        
    }
)