# IDP Python Utilities

The purpose of this library is to provide useful tools to support IDP based processes


## Install

```
pip install dist/idplib-0.0.1-py3-none-any.whl
```

Lib is not currently on pypi until it is more stable

## Usage

Usege will be broken down into a few concepts. General and tool specific.

### General

ValueUtils 

#### Normalisers
```
from idplib import ValueUtils

# Takes a digit as a string and returns a string 
# Removes spaces, hyphens, comma, dollar sign
# Or you can submit your own pattern to normalise, this allows you to handle for specific cases

result = ValueUtils.Normalise.digit('$5')
>>> '5'

result = ValueUtils.Normalise.digit('5%', pattern=r"[ -\$,%]")
>>> '5'

# Safely round numbers as python can incorrectly round floating point digits

result = ValueUtils.Normalise.safe_round(1.515)
>>> 1.52

result = ValueUtils.Normalise.safe_round(1.5155, decimal_places=3)
>>> 1.516

# Dates

# To Convert a string into a date. Handles most non American formats

result = ValueUtils.Normalise.Date.from_string('1/5/2024')
>>> datetime.datetime(2024, 5, 1, 0, 0)

# With eagle_mode set to True it will manage US style dates
result = ValueUtils.Normalise.Date.from_string('5/1/2024')
>>> datetime.datetime(2024, 5, 1, 0, 0)

# Get the tax year from a date given the tax year starts July 1

result = ValueUtils.Normalise.Date.tax_year('1/8/2024')
>>> 2025

```

#### Compare

Compare functions have some fuzzy logic and normalisation built in. Where thresholds are involved there are options to adjust the default values.

```
from idplib import ValueUtils

# Digits

result = ValueUtils.Compare.digits('$5', '$5,')
>>> True

# Strings

result = ValueUtils.Compare.string('the quick brown fox', 'the quick brown f0x')
>>> True

result = ValueUtils.Compare.string('the quick brown fox', 'the quick yellow f0x', threshold=99)
>>> False

# Strings and ignore the order of words
# Note token_ratio is 89 by default
result = ValueUtils.Compare.string('the quick brown fox', 'brown quick the fox', ignore_order=True, token_ratio=89)
>>> True

# You can also get the % match of the strings
# you can also control thresholds and word order in the same way as above

result, percent = ValueUtils.Compare.string_with_percent('the quick brown fox', 'the quick brown f0x')
>>> True, 95

```

#### Identify

Identify if specific attributes exist

```
from idplib import ValueUtils

# Credit Card Number
result = ValueUtils.Identify.credit_card_number('an actual cc number goes here')
>>> False

# ABN 
result = ValueUtils.abn('44 078 253 426')
>>> True

# TFN
# There are several options here

## Specific string IE TFN field check

result = ValueUtils.tfn('44 078 253 426')
>>> False

## Large strings IE Full Page

result = ValueUtils.tfn_in_string('My Full Page here')
>>> False

## There is also an option for max_gap which allows you to control the maximum distance between digits to prevent false positives
```

### Determining a threshold

One of the biggest challenges I have found with Fuzzy Logic is knowing what threshold to use for a given set of data.

In order to help make this easier there is a Genetic Algorithm built into the library to help determine the required threshold based on information in your usecase.

Usage:
```
from idplib.Utilities.FuzzyFinder import GA
x = GA(objectives)
x.run()
```

To prepare the objectives data create a list of lists, with each of the sublists being
```
[value1, value2, bool_should_match]
```

ie

```
[
    ["Jim", "J1m", True],
    ["Egg", "3gg", True],
    ["Bacon", "Smith", False]
]
```

If you want to generate an example of this 
```
from idplib.Utilities.FuzzyFinder import Example

Example.fuzzy()

```
This will generate a file called `example.json` which you can use as a starting point.




### HyperScience Specific

At the moment this code has been tested on V35 data only. 
When I have access to a higher version I will adjust accordingly. Alternatively feel free to raise an issue and submit a PR.

Within the HS component there are 2 primary classes, Documents, Document.

Documents will support functions which apply to the entire HS document array. This will be covered last as there are some pre-requirements.

Document relates to a single document from HS. There is a Locate class which can also be used independant of the Document class but for simplicity just use it within Document.

#### Document
```
from idplib.HS.DocumentUtils import Document

doc = Document(current_hs_document)
page_count = doc.page_count
layout = doc.layout

# Locating within a document

# Get all fields by field name
fields = doc.locate.fields_by_name('firstName')

# get all fields by occurence
occurences  = doc.locate.fields_by_occurrence(0)

# get the value at a specific position and fieldname
value = doc.locate.value_at_position(field_name='firstName', occurence=0)
>>> 'JOHN'

# get the value at a specific position and fieldname
# non HS normalised value
value = doc.locate.value_at_position(field_name='firstName', occurence=0, normalised=False)
>>> 'John'

# Locate a value at any occurence with fuzzy matching
# Note: return is (bool if the value is found, the value, occurence)
# Threshold 88 is also the default

doc.locate.match_value_any_position(field_name='firstName', value='John', threshold=88)
>>> (True, 'JOHN', 0)

```

#### Documents

There are dependencies within HS which need to be met for the Documents class. These are listed in the below

```
from idplib.HS.DocumentUtils import Documents


# Mapping filenames to their HS documents
# REQUIRED submission_files json from the submission API

updated_docs = Documents.map_filenames(hs_documents, submissions_files)

# Mapping fullpage transcriptions to their original documents
# REQUIRED full page transcription block output

updated_docs = Documents.FullPage.map(hs_documents, full_page_data)

# Converting the full page data into a single string instead of segments.
# Works on 1 document at a time

as_string = Documents.FullPage.to_string(hs_document)

```