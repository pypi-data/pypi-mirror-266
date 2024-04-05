# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mamba_former']

package_data = \
{'': ['*']}

install_requires = \
['einops', 'torch', 'zetascale==2.2.7']

setup_kwargs = {
    'name': 'mamba-former',
    'version': '0.0.3',
    'description': 'Paper - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# MambaFormer\nImplementation of MambaFormer in Pytorch ++ Zeta from the paper: "Can Mamba Learn How to Learn? A Comparative Study on In-Context Learning Tasks"\n\n## install\n`pip3 install mamba-former`\n\n## usage\n```python\nimport torch\nfrom mamba_former.main import MambaFormer\n\n# Forward pass example\nx = torch.randint(1, 1000, (1, 100))  # Token\n# Tokens are integers representing input data\n\n# Model\nmodel = MambaFormer(\n    dim=512,  # Dimension of the model\n    num_tokens=1000,  # Number of unique tokens in the input data\n    depth=6,  # Number of transformer layers\n    d_state=512,  # Dimension of the transformer state\n    d_conv=128,  # Dimension of the convolutional layer\n    heads=8,  # Number of attention heads\n    dim_head=64,  # Dimension of each attention head\n    return_tokens=True,  # Whether to return the tokens in the output\n)\n\n# Forward pass\nout = model(x)  # Perform a forward pass through the model\n\n# If training\n# out = model(x, return_loss=True)  # Perform a forward pass and calculate the loss\n\n# Print the output\nprint(out)  # Print the output tensor\nprint(out.shape)  # Print the shape of the output tensor\n\n```\n\n\n# License\nMIT\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/MambaFormer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
