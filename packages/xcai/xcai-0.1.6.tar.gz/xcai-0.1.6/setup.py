from setuptools import setup, find_packages

setup(
    name='xcai',  # 包名称，在PyPI中必须唯一
    version='0.1.6',           # 当前包的版本
    author='XiaoChuang.ai',        # 作者名字
    author_email='sup@XiaoChuangai.com',  # 作者邮箱
    #maintainer='Maintainer Name',          # 维护者名字，可选
    #maintainer_email='maintainer.email@example.com',  # 维护者邮箱，可选
    #url='https://github.com/yourusername/your_package',  # 项目的URL，通常是代码仓库的地址
    description='We make AI simple for you',  # 简短的项目描述
    long_description=open('README.md').read(),  # 从README文件中读取的长描述
    long_description_content_type='text/markdown',  # 长描述的内容类型（这里是Markdown）
    packages=find_packages(),  # 自动发现并包含项目中的包
    classifiers=[  # 分类器，帮助用户发现你的包
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',  # 例子中使用的是MIT许可证
    ],
    keywords='ai AI simple',  # 关键字，方便用户搜索到你的包
    license='MIT',  # 许可证类型
    install_requires=["requests"],
    #extras_require={  # 额外的依赖，可用于开发或测试
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},
    # 其他可选配置...
)