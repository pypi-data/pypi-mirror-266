import setuptools



setuptools.setup(
    name="dzwl",                                     # 包的分发名称，使用字母、数字、_、-
    version="20240409",                                        # 版本号, 版本号规范：https://www.python.org/dev/peps/pep-0440/
    author="zj",                                       # 作者名字
    author_email="author@example.com",                      # 作者邮箱
    description="PyPI Tutorial",                            # 包的简介描述
    long_description='123',                      # 包的详细介绍(一般通过加载README.md)
    packages=setuptools.find_packages(),  
    install_requires=[],  # 依赖的包
    python_requires='>=3'
)

# 这是最简单的配置
# 有关详细信息，请参阅(https://packaging.python.org/guides/distributing-packages-using-setuptools/)