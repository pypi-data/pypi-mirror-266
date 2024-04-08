import codecs
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

INSTALL_REQUIRE = [
    "requests",
    "aiohttp",
    "brotli"
]

EXTRA_REQUIRE = {
    'all': [
        "curl_cffi>=0.6.2",
        "certifi",
        "async-property",          # openai
        "py-arkose-generator",     # openai
        "browser_cookie3",         # get_cookies
        "PyExecJS",                # GptForLove
        "duckduckgo-search>=5.0"  ,# internet.search
        "beautifulsoup4",          # internet.search and bing.create_images
        "brotli",                  # openai
        "platformdirs",            # webdriver
        "undetected-chromedriver>=3.5.5", # webdriver
        "setuptools",              # webdriver
        "aiohttp_socks",           # proxy
        "pillow",                  # image
        "cairosvg",                # svg image
        "werkzeug", "flask",       # gui
        "loguru", "fastapi",
        "uvicorn", "nest_asyncio", # api
        "selenium-wire"
    ],
    "image": [
        "pillow",
        "cairosvg",
        "beautifulsoup4"
    ],
    "webdriver": [
        "platformdirs",
        "undetected-chromedriver",
        "setuptools",
        "selenium-wire"
    ],
    "openai": [
        "async-property",
        "py-arkose-generator",
        "brotli"
    ],
    "api": [
        "loguru", "fastapi",
        "uvicorn", "nest_asyncio"
    ],
    "gui": [
        "werkzeug", "flask",
        "beautifulsoup4", "pillow",
        "duckduckgo-search>=5.0",
        "browser_cookie3"
    ],
    "local": [
        "gpt4all"
    ]
}

DESCRIPTION = (
    "Gsk Chatbot"
)

# Setting up
setup(
    name='gskChat',
    version="1.0.9",
    author='tafik',
    author_email='<doneld528@gmail.com>',
    description=DESCRIPTION,
    long_description_content_type='text/markdown',
    long_description="Gsk Chatbot",
    packages=find_packages(),
    package_data={
        'gskChat': ['gskChat/interference/*', 'gskChat/gui/client/*', 'gskChat/gui/server/*', 'gskChat/Provider/npm/*', 'gskChat/local/models/*']
    },
    include_package_data=True,
    install_requires=INSTALL_REQUIRE,
    extras_require=EXTRA_REQUIRE,
    entry_points={
        'console_scripts': ['gskChat=gskChat.cli:main'],
    },
    keywords=[
        'python',
        'chatbot',
        'reverse-engineering',
        'openai',
        'chatbots',
        'gpt',
        'language-model',
        'gpt-3',
        'gpt3',
        'openai-api',
        'gpt-4',
        'gpt4',
        'chatgpt',
        'chatgpt-api',
        'openai-chatgpt',
        'chatgpt-free',
        'chatgpt-4',
        'chatgpt4',
        'chatgpt4-api',
        'free',
        'free-gpt',
        'gpt4free',
        'g4f',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ],
)