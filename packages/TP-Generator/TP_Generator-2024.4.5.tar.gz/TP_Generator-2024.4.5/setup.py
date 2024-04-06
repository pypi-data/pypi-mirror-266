import setuptools

setuptools.setup(
	name="TP_Generator",
	version="2024.4.5",
	author="TP Cyber Security",
	license="MIT",
	author_email="tpcybersec2023@gmail.com",
	description="",
	long_description=open("README.md").read(),
	long_description_content_type="text/markdown",
	install_requires=open("requirements.txt").read().split(),
	url="https://github.com/truocphan/TP-Generator",
	classifiers=[
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: Implementation :: Jython"
	],
	keywords=["TPCyberSec", "TP-Generator", "Sniper Attack", "Batteringram Attack", "Pitchfork Attack", "Clusterbomb Attack", "TOTP/ HOTP Generate", "UUID1"],
	packages=["TP_Generator"],
)