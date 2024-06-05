import os

MATHJAX_VERSION = '2.7.5'
MATHJAX_CDN_URL = f'https://cdn.jsdelivr.net/npm/mathjax@{MATHJAX_VERSION}/MathJax.js'
MATHJAX_STATIC_PATH = os.path.join('offline_mode_shared_static', 'js', f'MathJax-{MATHJAX_VERSION}.js')
