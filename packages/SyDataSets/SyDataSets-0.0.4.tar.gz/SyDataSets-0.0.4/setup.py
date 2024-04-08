from setuptools import find_packages, setup

name = 'SyDataSets'
requires_list = open(f'{name}/requirements.txt', 'r', encoding='utf8').readlines()
requires_list = [i.strip() for i in requires_list]

setup(
    name=name,  
    version="0.0.4",
    author="zhuchao",
    author_email="zhuchao@meteplus.com",
    description="Provided to meteplus for data processing",
    python_requires=">=3.6",
    packages=find_packages(),
    package_data={"": ["*"]},  
    include_package_data=True, 
    zip_safe=False,
    # 设置依赖包
    install_requires=requires_list
)