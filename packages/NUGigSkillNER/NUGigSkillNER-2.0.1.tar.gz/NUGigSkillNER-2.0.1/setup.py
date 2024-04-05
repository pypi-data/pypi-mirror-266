import setuptools


dependencies = [
    "numpy",
    "pandas",
    "nltk",
    "spacy",
    "jellyfish",
    "scipy"
]

setuptools.setup(
    name="NUGigSkillNER",
    version="2.0.1",
    author="Ethan Mandel",
    author_email="emandel2630@gmail.com",
    description="An NLP module to automatically Extract skills and certifications from unstructured job postings, texts, and applicant's resumes",
    url="https://github.com/emandel2630/NUGigSkillNER",
    keywords=["skillNer", 'python', 'NLP', "NER",
              "skills-extraction", "job-description"],
    packages=setuptools.find_packages(),
    install_requires=dependencies,
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
)
