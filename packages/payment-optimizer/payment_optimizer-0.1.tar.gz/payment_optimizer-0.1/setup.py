import pathlib
import setuptools

setuptools.setup(
    name="payment_optimizer",
    version="0.1",
    description="Optimizing the payment process of e-commerce",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Elen Sukiasyan, Nane Mambreyan, Areg Amirjanyan, Gayane Ohanjanyan, Hasmik Sahakyan",
    license="The Unlicense",
    classifiers=[
        "Development Status :: 3 - Alpha"
    ],
    python_requires=">=3.10, <3.12", 
    install_requires=["requests", "pandas>=2.0"],
    packages=["Documents", "payment_optimizer"]
)
