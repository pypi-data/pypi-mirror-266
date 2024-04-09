from setuptools import setup, find_packages

setup(
    name='Doggel_Inc', 
    version='1.3.1', 
    description='Doggeł Inc packages',
    author='Lordpomind',
    author_email='lordpomind@gmail.com',
    url='',  
    package_data={
        'Doggel_Inc': ["src/*"]
    },
    packages=find_packages(),  
    install_requires=[  
        'aiohttp', 'websockets'      
    ],
    classifiers=[  
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',        
        'Programming Language :: Python :: 3.10',        
        'Programming Language :: Python :: 3.11',
    ],
)