from setuptools import find_packages, setup


setup(name='bopt_slf',
      version='1.0.1',
      description='Bayesian optimization for constrained or unconstrained, continuous, discrete or mixed data problems',
      author='Javier Morlet',
      author_email='a00833961@tec.mx',
      packages = find_packages(),
      install_requires=[
          'numpy>=1.23.5',
          'sympy>=1.11.1',
          'pandas>=2.0.3',
          'GPy>=1.10.0',
          'scipy>=1.10.1',
          'scikit-learn>=1.1.3',
          'properscoring>=0.1',
          'prince>=0.12.1',
          'matplotlib>=3.7.3'
          ]
     )