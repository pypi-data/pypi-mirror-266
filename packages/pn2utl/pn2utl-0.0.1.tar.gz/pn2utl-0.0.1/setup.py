import os
import setuptools
# from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension
from distutils.sysconfig import get_config_vars

(opt,) = get_config_vars('OPT')
os.environ['OPT'] = " ".join(
    flag for flag in opt.split() if flag != '-Wstrict-prototypes'
)

src = 'src'
sources = [os.path.join(root, file) for root, dirs, files in os.walk(src)
           for file in files
           if file.endswith('.cpp') or file.endswith('.cu')]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(

    name="pn2utl",
    version="0.0.1",
    author="leehiking",
    author_email="gz6201347@163.com",
    description="test first package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/leehiking/my_pkg_1",
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),

    # packages=setuptools.find_packages(),
    install_requires=['torch>=1.0', 'numpy>=1.0'],
    setup_requires=['wheel'],
    python_requires=">=3.0",

    packages=["pn2utl"],
    package_dir={"pn2utl": "functions"},
    ext_modules=[
        CUDAExtension(
            name='pn2utl._C',
            sources=sources,
            extra_compile_args={'cxx': ['-g'], 'nvcc': ['-O2']}
        )
    ],
    cmdclass={'build_ext': BuildExtension}
)
