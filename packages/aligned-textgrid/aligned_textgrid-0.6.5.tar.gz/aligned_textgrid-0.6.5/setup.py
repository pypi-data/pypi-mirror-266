# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aligned_textgrid',
 'aligned_textgrid.mixins',
 'aligned_textgrid.outputs',
 'aligned_textgrid.points',
 'aligned_textgrid.polar',
 'aligned_textgrid.sequences']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.24.2,<2.0.0', 'polars>=0.20.18,<0.21.0', 'praatio>=6.0.0,<7.0.0']

setup_kwargs = {
    'name': 'aligned-textgrid',
    'version': '0.6.5',
    'description': 'Classes for defining sequential information from TextGrids',
    'long_description': "# Aligned TextGrid\n\n![PyPI](https://img.shields.io/pypi/v/aligned-textgrid.png)\n![lint_and_test](https://github.com/Forced-Alignment-and-Vowel-Extraction/alignedTextGrid/actions/workflows/test_and_run.yml/badge.svg?event=pull_request&branch=main)\n[![codecov](https://codecov.io/gh/Forced-Alignment-and-Vowel-Extraction/alignedTextGrid/branch/dev/graph/badge.svg?token=27YSOQ5ZEL)](https://codecov.io/gh/Forced-Alignment-and-Vowel-Extraction/alignedTextGrid)\n[![Maintainability](https://api.codeclimate.com/v1/badges/2387cd247bd8f1211323/maintainability.png)](https://codeclimate.com/github/Forced-Alignment-and-Vowel-Extraction/alignedTextGrid/maintainability)\n[![Build\nDocs](https://github.com/Forced-Alignment-and-Vowel-Extraction/alignedTextGrid/actions/workflows/build-docs.yml/badge.svg)](https://forced-alignment-and-vowel-extraction.github.io/alignedTextGrid/)\n[![DOI](https://zenodo.org/badge/552633207.svg)](https://zenodo.org/badge/latestdoi/552633207)\n\nThe aligned-textgrid package provides a python interface for\nrepresenting and operating on TextGrids produced by forced aligners like\n[FAVE](https://github.com/JoFrhwld/FAVE) or the [Montreal Forced\nAligner](https://montreal-forced-aligner.readthedocs.io/en/latest/).\nClasses provided by aligned-textgrid represent hierarchical and\nprecedence relationships among data stored in TextGrid formats allowing\nfor simplified and more accessible analysis of aligned speech data.\n\n## Example Use Cases\n\n- You want to quickly loop through the Phone tier of a Textgrid, and\n  *also* access information about the word it is a part of.\n- You want to quickly loop over the Word tier of a Textgrid and quickly\n  count how many phones it has.\n- You want to programmatically merge together adjacent Textgrid\n  intervals.\n\nFor examples on how to use the pacakge, see the [Usage](https://forced-alignment-and-vowel-extraction.github.io/alignedTextGrid/usage) pages.\n\n## Installation\n\n<!-- TODO: documnet other package managers like conda -CB 14 March 2023 -->\n\nTo install aligned-textgrid using pip, run the following command in your\nterminal:\n\n``` bash\npip install aligned-textgrid\n```\n\n## Not another TextGrid implementation\n\nThere are several other packages that parse Praat Textgrids, including\n\n- [praatio](http://timmahrt.github.io/praatIO/praatio.html)\n- [textgrid](https://github.com/kylebgorman/textgrid)\n\n`aligned-textgrid`’s goal is to capture hierarchical and sequential\nrelationships represented in many TextGrids, and to make them easilly\naccessible to users via an intuitive interface. The goal is that from\nany arbitrary location within a TextGrid, users can easilly access\ninformation with minimally defensive coding.\n\n![](doc_src/usage/resources/diagrams/hierarchy_precedence.svg)\n\n### Example\n\nAs an example, we’ll read in a textgrid produced with forced alignment\nthat contains a single speaker with a word and phone tier.\n\n``` python\nfrom aligned_textgrid import AlignedTextGrid, Word, Phone\ntg = AlignedTextGrid(\n    textgrid_path='doc_src/usage/resources/josef-fruehwald_speaker.TextGrid', \n    entry_classes=[Word, Phone]\n    )\n```\n\nThen, we can access an arbitrary phone interval.\n\n``` python\narbitrary_interval = tg[0].Phone[20]\n```\n\nFrom this aribitrary interval, we can access information about the\nintervals preceding and following with the `.prev` and `.fol`\nattributes.\n\n``` python\nprint(arbitrary_interval.prev.label)\nprint(arbitrary_interval.label)\nprint(arbitrary_interval.fol.label)\n```\n\n    R\n    EY1\n    N\n\nWe can also access information about the word this interval is nested\nwithin with the `.inword` attribute.\n\n``` python\nprint(arbitrary_interval.inword.label)\n```\n\n    raindrops\n\nThe object returned by `.inword` is just another interval, meaning we\ncan access informaton about *it’s* context with the `.prev` and `.fol`\nattributes as well.\n\n``` python\nprint(arbitrary_interval.inword.prev.label)\nprint(arbitrary_interval.inword.label)\nprint(arbitrary_interval.inword.fol.label)\n```\n\n    strikes\n    raindrops\n    in\n\n## For more\n\n- To start jumping in, check out [the\n  quickstart](https://forced-alignment-and-vowel-extraction.github.io/alignedTextGrid/usage/)\n- To learn more about navigating TextGrids and intervals, check out the\n  usage pages on [navigating\n  TextGrids](https://forced-alignment-and-vowel-extraction.github.io/alignedTextGrid/usage/01_TextGrids/01_tg-nav.html)\n  and [navgiating\n  sequences](https://forced-alignment-and-vowel-extraction.github.io/alignedTextGrid/usage/02_Sequences/00_sequence_structure.html)\n- To learn more about the attributes you can access from textgrids and\n  sequences, see the usage pages on [TextGrid\n  attributes](https://forced-alignment-and-vowel-extraction.github.io/alignedTextGrid/usage/01_TextGrids/02_tg-info.html)\n  and [interval\n  attributes](https://forced-alignment-and-vowel-extraction.github.io/alignedTextGrid/usage/02_Sequences/02_sequence_properties.html)\n\nYou can also directly read up on [the function and class\nreferences](https://forced-alignment-and-vowel-extraction.github.io/alignedTextGrid/reference/).\n",
    'author': 'JoFrhwld',
    'author_email': 'JoFrhwld@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://forced-alignment-and-vowel-extraction.github.io/alignedTextGrid/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
