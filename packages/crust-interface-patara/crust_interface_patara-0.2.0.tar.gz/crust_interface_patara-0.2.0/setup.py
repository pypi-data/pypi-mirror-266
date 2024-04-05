# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crustinterface']

package_data = \
{'': ['*']}

install_requires = \
['substrate-interface>=1.4.0,<2.0']

setup_kwargs = {
    'name': 'crust-interface-patara',
    'version': '0.2.0',
    'description': 'A simple tool to interact with Crust Shadow, Crust Polkadot Parachain and Crust Mainnet. Under development',
    'long_description': '# crust-file-uploader\n\nhttps://crust.network/\nhttps://apps.crust.network/\nhttps://wiki.crust.network/en\nhttps://polkadot.js.org/apps/?rpc=wss%3A%2F%2Frpc-shadow.crust.network%2F#/explorer\n\nThis is a simple tool to pin your files sing Crust Network or Crust Shadow.\n\n## Setup\n### Installation:\n```bash\npip3 install crust-interface-patara\n```\n\n## Features\n\nThe module is divided into `Mainnet` and `Shadow`\n\n`Mainnet` provides Crust interaction functionality to check user balance, calculate file storage price, placing\nfile storage order, add tokens to renewal pool and checking replicas count.\n\n```python\nimport time\nfrom crustinterface import Mainnet\nfrom substrateinterface import KeypairType\n\nseed = "seed"\nmainnet = Mainnet(seed=seed, crypto_type=KeypairType.SR25519)\n\n# get any IPFS CID and size\ncid, size =  "QmbJtyu82TQSHU52AzRMXBENZGQKYqPsmao9dPuTeorPui", 18  # <any way to get an IPFS CID and size. One may use ipfshttpclient2 from IPFS-Toolkit>\n\n# Check balance\nbalance = mainnet.get_balance()\nprint(balance)\n\n# Check price in Main net. Price in pCRUs\nprice = mainnet.get_appx_store_price(int(size))\nprint(price)\n\n# Store file in Mainnet for CRUs\nfile_stored = mainnet.store_file(cid, size)\nprint(file_stored)\n\n# Add renewal pool\nfile_prepaid = mainnet.add_renewal_pool_balance(cid, price*2)\nprint(file_prepaid)\n\n\n# Get replicas\ntime.sleep(10)\nreplicas = mainnet.get_replicas(cid)\nprint(replicas)\n\n```\n\n`Shadow` allows you to perform `Xstorage` extrinsic in Crust Shadow network.\n```python\nfrom crustinterface import Shadow\nfrom substrateinterface import KeypairType\n\nseed = "seed"\nshadow = Shadow(seed=seed, crypto_type=KeypairType.SR25519)\n\n# get any IPFS CID and size\ncid, size =  "QmbJtyu82TQSHU52AzRMXBENZGQKYqPsmao9dPuTeorPui", 18  # <any way to get an IPFS CID and size. One may use ipfshttpclient2 from IPFS-Toolkit>\n\nprint(cid, size)\n\n# Check balance\nbalance = shadow.get_balance()\nprint(balance)\n\n# Store file in Shadow for CSMs\nfile_stored = shadow.store_file(cid, size)\nprint(file_stored)\n```\n\n`Parachain` allows you to perform `Xstorage` extrinsic in Crust Polkadot Parachain network.\n```python\nfrom crustinterface import Parachain\nfrom substrateinterface import KeypairType\n\nseed = "seed"\nparachain = Parachain(seed=seed, crypto_type=KeypairType.SR25519)\n\n# get any IPFS CID and size\ncid, size =  "QmbJtyu82TQSHU52AzRMXBENZGQKYqPsmao9dPuTeorPui", 18  # <any way to get an IPFS CID and size. One may use ipfshttpclient2 from IPFS-Toolkit>\n\nprint(cid, size)\n\n# Check balance\nbalance = parachain.get_balance()\nprint(balance)\n\n# Store file in Shadow for CSMs\nfile_stored = parachain.store_file(cid, size)\nprint(file_stored)\n```\n',
    'author': 'PaTara43',
    'author_email': 'p040399@outlook.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/PaTara43/crust-interface-patara',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
