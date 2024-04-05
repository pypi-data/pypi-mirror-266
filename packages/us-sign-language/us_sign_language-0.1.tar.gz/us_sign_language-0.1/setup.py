from setuptools import setup, find_packages

setup(name='us_sign_language',
      version='0.1',
      packages=find_packages(),
      install_requires=['tensorflow<=2.8.0',
                        'mediapipe<=0.8.11',
                        'numpy>=1.19.3',
                        'opencv-python>=4.9.0.80',
                        'asyncio>=3.4.3']
      )
