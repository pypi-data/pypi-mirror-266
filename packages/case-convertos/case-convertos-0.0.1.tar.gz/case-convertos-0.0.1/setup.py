import setuptools

setuptools.setup(
    name="case-convertos",
    version="0.0.1",
    author="Mohamed Moumni",
    description="Convert a string to upper case",
    packages=["caseConverter"],
    entry_points={
        'console_scripts': [
            'case_converter = caseConverter.case_converter:case_converter'
        ]
    }
)