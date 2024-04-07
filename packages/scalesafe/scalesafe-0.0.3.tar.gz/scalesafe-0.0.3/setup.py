from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='scalesafe',
    version='0.0.3',  # Semantic Versioning (https://semver.org/)
    description='ScaleSafe Monitoring Engine: Toolkit for integrating monitoring into AI systems for compliance and safety.',
    long_description="""
        ScaleSafe is an open-source toolkit designed to integrate monitoring into AI systems, 
        supporting compliance with the EU AI Act, New York Bill 144, and other regulations. 
        It offers functionalities for logging AI usage, screening responses, handling human-in-the-loop control, 
        and conducting risk and compliance audits.
    """,
    author='Tobin South', 
    author_email='tsouth@mit.edu', 
    url='https://scalesafe.ai', 
    license='MIT', 
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={
        'dev': [
            'pytest>=6.2.5',
        ],
    },
    classifiers=[
        # See https://pypi.org/classifiers/ for a full list
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
