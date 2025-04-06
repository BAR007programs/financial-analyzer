[metadata]
name = financial-analyzer
version = 0.1.0
description = AI-powered financial PDF extractor
long_description = file: README.md
long_description_content_type = text/markdown
author = Brian Rwabwogo
author_email = brianrwabogo@example.com
license = MIT
url = https://github.com/yourusername/financial-analyzer
classifiers =
    Programming Language :: Python :: 3
    License :: OSI Approved :: MIT License
    Operating System :: OS Independent

[options]
py_modules =
    main
    pdf_processor
    analyzer
    verify_file
python_requires = >=3.10
install_requires =
    pandas
    pdfplumber
    camelot-py[cv]
    pytesseract
    pdf2image
    pikepdf
    numpy
    opencv-python
    pillow
    reportlab

[options.entry_points]
console_scripts =
    financial-analyzer = main:main
