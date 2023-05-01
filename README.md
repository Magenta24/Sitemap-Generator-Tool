# Final Project
## Site Map Generator Tool

This repository contains the implementation of Sitemap Generator Tool 
that produces XML sitemap of a website provided by a user.
The features includes:
- producing an XML sitemap of a website specified by a user
- producing a zoomable URL graph-like diagram
- possibility to download both sitemaps
- listing collected links
- listing found documents
- listing found images
- mini-search engine that looks for words/phrases specified by a user

## Prerequisites
To run the software following need to be installed first
* Python 3.11 (downloads: [https://www.python.org/downloads/](https://www.python.org/downloads/))
* Graphviz (downloads: [https://graphviz.org/download/](https://graphviz.org/download/))


## Installation
### Creating Python environment

```
python -m venv /path/to/new/virtual/environment (venv is the name of the environment)

./path/to/new/virtual/environment/bin/activate (activate the environment)
```
### Installing requirements
```
pip install -r requirements.txt
```

## Screenshots from the application
![The form](/screenshots/form.PNG "Start form")
![Results](/screenshots/initial-view-results.PNG "Initial view of results")
![Statistics](/screenshots/statistics.PNG "Statistics of the crawler")
![Zoomable diagram](/screenshots/zoomable_pic.PNG "Zoomable picture")
![Tree structure](/screenshots/tree-structure.PNG "Vertical URL tree")
![Downloads](/screenshots/downloads.PNG "Downloads")
![Collected links](/screenshots/collected-links.PNG "Collected links")
![Found documents](/screenshots/found-documents.PNG "Found documents")
![Found images](/screenshots/found-images.PNG "Found images")
![Search engine results](/screenshots/search-engine.PNG "Search Engine results")

## License
Copyright (c) 2011-2017 GitHub Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
