from setuptools import setup, find_packages

with open("README.md","r") as ofile:
    long_description_file = ofile.read()
    
setup(
    name='signapse',
    version='1.0.12',
    description='Signapse_synthetic_signer',
    long_description=long_description_file,
    long_description_content_type="text/markdown",
    author='Basheer Alwaely',
    author_email='basheer@signapse.ai',
    url='https://github.com/signapse/signapse',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
    install_requires=[
        'essentials',
        'setuptools',
        'wheel==0.38.4',
        'mediapipe==0.10.3',
        'opencv-python==4.7.0.72',
        'opencv-python-headless==4.7.0.72',
        'pandas==2.0.3',
        'pickle5==0.0.11',
        'protobuf==3.20.*',
        'boto3 == 1.24.47',
        'ffmpeg-python == 0.2.0',
        'scipy == 1.8,',
        'pycpd==2.0.0',
        'torch==1.11.0+cu113',
        'torchvision==0.12.0+cu113',
        'torchaudio==0.11.0',
        'Pillow==9.3.0',
        'imageio',
        'PyYAML',
    ]
)
