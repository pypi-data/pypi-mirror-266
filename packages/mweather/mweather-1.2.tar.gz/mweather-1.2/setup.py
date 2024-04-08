import setuptools
with open(r'C:\Users\say gex\Desktop\проектыц\weather\README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='mweather',
	version='1.2',
	author='mc.c0rp',
	author_email='mc.c0rp@icloud.com',
	description='Бесплатное и быстрое api для получения погоды.',
	long_description=long_description,
	long_description_content_type='text/markdown',
	packages=['mweather'],
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)