# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exa', 'exa.structs', 'exa.utils']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.5.3,<0.6.0', 'torch>2.0.0']

entry_points = \
{'console_scripts': ['swarms = swarms.cli._cli:main']}

setup_kwargs = {
    'name': 'exxa',
    'version': '0.6.4',
    'description': 'Exa - Pytorch',
    'long_description': "[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Exa\nBoost your GPU's LLM performance by 300% on everyday GPU hardware, as validated by renowned developers, in just 5 minutes of setup and with no additional hardware costs.\n\n-----\n\n## Principles\n- Radical Simplicity (Utilizing super-powerful LLMs with as minimal lines of code as possible)\n- Ultra-Optimizated Peformance (High Performance code that extract all the power from these LLMs)\n- Fludity & Shapelessness (Plug in and play and re-architecture as you please)\n\n---\n\n## 📦 Install 📦\n```bash\n$ pip3 install exxa\n```\n-----\n\n\n## Usage\n\n\n\n\n\n\n## 🎉 Features 🎉\n\n- **World-Class Quantization**: Get the most out of your models with top-tier performance and preserved accuracy! 🏋️\u200d♂️\n  \n- **Automated PEFT**: Simplify your workflow! Let our toolkit handle the optimizations. 🛠️\n\n- **LoRA Configuration**: Dive into the potential of flexible LoRA configurations, a game-changer for performance! 🌌\n\n- **Seamless Integration**: Designed to work seamlessly with popular models like LLAMA, Falcon, and more! 🤖\n\n----\n\n## 💌 Feedback & Contributions 💌\n\nWe're excited about the journey ahead and would love to have you with us! For feedback, suggestions, or contributions, feel free to open an issue or a pull request. Let's shape the future of fine-tuning together! 🌱\n\n[Check out our project board for our current backlog and features we're implementing](https://github.com/users/kyegomez/projects/8/views/2)\n\n\n# License\nMIT\n\n# Todo\n\n- Setup utils logger classes for metric logging with useful metadata such as token inference per second, latency, memory consumption\n- Add cuda c++ extensions for radically optimized classes for high performance quantization + inference on the edge\n\n\n\n",
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/Exa',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
