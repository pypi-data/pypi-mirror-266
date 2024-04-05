from distutils.core import setup

setup(
    name='queue_app_provider',  # How you named your package folder (MyLib)
    packages=['queue_app_provider'],  # Chose the same as "name"
    version='0.1',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Simple backend processor that receives binary data and stores it in a queue that it''s processed in '
                'a background thread.',  # Give a short description about your library
    author='David Rodriguez Alfayate',  # Type in your name
    author_email='david.rodriguez.alfayate@gmail.com',  # Type in your E-Mail
    url='https://github.com/drodriguezalfayate/flask-binary-queue/',  # Provide either the link to your github or to your website
    keywords=['QUEUE BACKGROUND PROCESSOR'],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'flask',
        'requests',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
