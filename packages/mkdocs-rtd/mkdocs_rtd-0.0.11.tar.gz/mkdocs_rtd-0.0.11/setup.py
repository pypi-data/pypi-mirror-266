# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rtd']

package_data = \
{'': ['*'],
 'rtd': ['css/*',
         'css/fonts/*',
         'img/*',
         'js/*',
         'locales/de/LC_MESSAGES/*',
         'locales/es/LC_MESSAGES/*',
         'locales/fa/LC_MESSAGES/*',
         'locales/fr/LC_MESSAGES/*',
         'locales/id/LC_MESSAGES/*',
         'locales/it/LC_MESSAGES/*',
         'locales/ja/LC_MESSAGES/*',
         'locales/pt_BR/LC_MESSAGES/*',
         'locales/ru/LC_MESSAGES/*',
         'locales/tr/LC_MESSAGES/*',
         'locales/uk/LC_MESSAGES/*',
         'locales/zh_CN/LC_MESSAGES/*',
         'locales/zh_TW/LC_MESSAGES/*']}

entry_points = \
{'mkdocs.themes': ['rtd = rtd']}

setup_kwargs = {
    'name': 'mkdocs-rtd',
    'version': '0.0.11',
    'description': 'A fork of mkdocs readthedocs theme to make it work with mkapi',
    'long_description': "# mkdocs-rtd\n\nA fork of mkdocs readthedocs theme to make it work better, especially with mkapi.\n\nWhy just use `extra_css` and `extra_javascript`?\n\n- The javascript written in `theme.js` shipped with the original theme has problems expanding the sidebar items and it's not easy to fix it only using `extra_javascript`.\n\n## Installation\n\n```bash\npip install -U mkdocs-rtd\n```\n\n## Usage\n\n```yaml\ntheme:\n  name: rtd\n```\n\nAll options are the same when using the original theme (`readthedocs`). See also:\n<https://www.mkdocs.org/user-guide/choosing-your-theme/#readthedocs>\n\n## Modifications\n\n- Add social icons (only Github supported now) to the top right corner of the page.\n- Adjust some styles\n- Open external links in new tab by default\n- Do not reset side nav items when url hash is `#` or empty\n- Make search box sticky\n- Add css support for `pymdownx.blocks.tab` (must use `alternate_style: true`)\n- Set `ignoreUnescapedHTML` to `true` for `hljs`\n- Keep current sidebar item always in view when scrolling\n",
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
