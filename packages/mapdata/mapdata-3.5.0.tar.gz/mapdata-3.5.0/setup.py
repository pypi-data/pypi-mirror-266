import setuptools
import io
import glob

with io.open('README.md', encoding='utf-8') as f:
	long_description = f.read()

symbol_files = glob.glob("mapdata/symbols/16x16/*.xbm") + glob.glob("mapdata/symbols/20x20/*.xbm") + \
			glob.glob("mapdata/symbols/24x24/*.xbm") + glob.glob("mapdata/symbols/28x28/*.xbm")

setuptools.setup(name='mapdata',
	version='3.5.0',
	description="An interactive map and table explorer for geographic coordinates in a spreadsheet, CSV file, or database",
	author='Dreas Nielsen',
	author_email='cortice@tutanota.com',
    url='https://osdn.net/project/mapdata/',
    packages=['mapdata'],
	scripts=['mapdata/mapdata.py'],
	data_files=[('symbols', symbol_files), ('config', ['mapdata/configfile/mapdata.conf'])],
    license='GPL',
	install_requires=['tkintermapview', 'pyproj', 'jenkspy', 'odfpy', 'openpyxl', 'xlrd', 'matplotlib', 'seaborn', 'loess', 'statsmodels', 'scipy', 'scikit-learn', 'pymannkendall', 'umap-learn', 'pynndescent'],
	python_requires = '>=3.8',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'Environment :: X11 Applications',
		'Environment :: Win32 (MS Windows)',
		'Intended Audience :: End Users/Desktop',
		'Intended Audience :: Information Technology',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Operating System :: POSIX',
		'Operating System :: Microsoft :: Windows',
		'Programming Language :: Python :: 3',
		'Topic :: Office/Business',
		'Topic :: Scientific/Engineering'
		],
	keywords=['Map', 'Locations', 'CRS', 'CSV', 'Spreadsheet', 'Database', 'PNG', 'JPG', 'Postscript'],
	long_description_content_type="text/markdown",
	long_description=long_description
	)
