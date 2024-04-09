from setuptools import setup

setup(
    name='anon_testo',
    version='0.4.0',    
    description='Anonimizzatore di documenti GateNLP',
    url='https://github.com/RafVale/anon_testo',
    author='Raffaele Valendino',
    author_email='raffaele.valendino@gmail.com',
    license='MIT',
    packages=['anon_testo'],
    install_requires=['spacy <= 3.2.0',
                    'presidio-analyzer <= 2.2.25',
                    'presidio-anonymizer <= 2.2.25',
                    'typing-inspect==0.8.0',
                    'typing_extensions==4.5.0'
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: Microsoft :: Windows :: Windows 10',        
        'Programming Language :: Python :: 3.9',
    ],
)
