from setuptools import setup, find_packages


setup(
    name='mqtt_sdk',
    package_dir={"": "src"},
    packages=find_packages('src', exclude=['test']),
    version='0.1',
    license='MIT',
    description='MQTT SDK to connect IOT devices to any cloud infrastructure',
    author='Awais khan',
    author_email='contact@awaiskhan.com.pk',
    url='https://github.com/Awaiskhan404/mqtt_sdk',
    keywords=['mqtt', 'iot', 'sdk', 'cloud', 'aws', 'azure', 'google cloud', 'mqtt sdk', 'mqtt client', 'mqtt broker',
              'mqtt publisher', 'mqtt subscriber', 'mqtt connect', 'mqtt disconnect', 'mqtt publish', 'mqtt subscribe',
              'mqtt on connect', 'mqtt on message', 'mqtt on disconnect', 'mqtt on publish', 'mqtt on subscribe',
              'mqtt on unsubscribe', 'mqtt on log', 'mqtt on error'],
    install_requires=[  # I get to this in a second
        'validators',
        'paho-mqtt'
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
