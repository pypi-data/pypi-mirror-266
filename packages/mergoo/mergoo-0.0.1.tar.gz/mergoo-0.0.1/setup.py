from setuptools import setup, find_packages

setup(
    name="mergoo",
    version="0.0.1",
    description="Implementation of Leeroo LLM composer.",
    author="Leeroo Team",
    author_email="support@leeroo.com",
    url="https://github.com/Leeroo-AI/mergoo",
    license="LGPLv3.0",
    keywords=["LLM", "compose", "MoE", "router"],
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "tqdm==4.66.2",
        "mergekit==0.0.4.2",
        "safetensors~=0.4.2",
        "accelerate~=0.27.2",
        "transformers",
        "huggingface_hub",
        "peft",
        "typing-extensions",
        "sentencepiece",
        "protobuf",
        "numpy",
    ],
)