from dataclasses import dataclass
import datetime
class Normal_People_Date:
	def __new__(cls, day_:"int", month_:"int", year_:"int") -> "datetime.date":
		return datetime.date(year_, month_, day_)
@dataclass
class Version:
	date: datetime.date
	version_number: str
	notes: str|None
	def validate(self):
		s = self.version_number.split(".")
		if not len(s) == 2:
			raise ValueError("Version number must have 3 parts.")
		for i in s:
			if not i.isdigit():
				raise ValueError("Version number must be numeric.")
	def __repr__(self) -> str:
		return f"V = [{self.version_number} released on {self.date}] & NOTES = ((( {self.notes} )))"

from setuptools import setup, find_packages
import sys
import os



CURRENT_VERSION = Version(
	date=Normal_People_Date(2, 4, 2024),
	version_number="0.2",
	notes="Added basic runtime type checking and other minor improvements."
)
CURRENT_VERSION.validate()

DESCRIPTION = ""
DESCRIPTION += f"Solving pythons biggest problem. Reference types (output variables/pointers) are not implemented. "
DESCRIPTION += f"This release: {repr(CURRENT_VERSION)} :D"



if len(sys.argv) == 1:
	sys.argv.append("sdist")
	sys.argv.append("bdist_wheel")



setup(
	name="refvars",
	version=CURRENT_VERSION.version_number,
	keywords=[
		"python",
		"reference",
		"variables",
		"pointers",
		"output",
		"return",
		"types",
		"reference types",
		"refvars"
	],
	author="matrikater (Joel C. Watson)",
	author_email="matrikater@matriko.xyz",
	description=DESCRIPTION,
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"Programming Language :: Python :: 3",
		"Operating System :: OS Independent",
		"Natural Language :: English",
		"Topic :: Software Development :: Libraries :: Python Modules"
	],
	packages=find_packages("refvars"),
)



def get_y_n(question:str) -> bool:
	while True:
		answer = input(question)
		if answer.lower() == "y":
			return True
		elif answer.lower() == "n":
			return False
		else:
			print("Please enter 'y' or 'n'.")

do_publish = get_y_n("Would you like to publish to PyPi? (y/n) ")
if not do_publish:
	exit(0)

again_to_be_sure = get_y_n("ARE YOU SURE? Remember, you can't unpublish. (y/n) ")
if not again_to_be_sure:
	exit(0)

os.system(f"python -m twine upload --repository pypi dist/*")
