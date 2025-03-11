# x12tools

A Python module for working with X12 EDI (Electronic Data Interchange) documents.

It can:

- Parse X12 EDI documents
- Easily extract segments and their data elements
- Read and edit segment terminator and data element separator
- Updates transaction set trailers to match the actual number of segments
- Write documents to string or file

## Usage

### Parsing an X12 Document from a String

```python
>>> from x12tools.document import X12Document
>>> content = """
...     ISA*00*          *00*          *ZZ*ABCDEFGHIJKLMNO*ZZ*123456789012345*210101*1253*U*00401*000000001*0*T*:~
...     GS*IN*123456789*987654321*20210101*1253*1*X*004010~
...     ST*810*0001~
...     BIG*20210101*12345*20201231*0~
...     N1*ST*ACME CORPORATION*92*1234~
...     N1*BT*BUYER ORGANIZATION*92*5678~
...     REF*PO*7654321~
...     ITD*01*3*1**15**30~
...     IT1*1*2*EA*14.50**BP*ABC123~
...     TDS*2900~
...     SE*8*0001~
...     GE*1*1~
...     IEA*1*000000001~
... """
>>> document = X12Document.from_string(content)
>>> document
X12Document(segments=[['ISA', '00', '          ', '00', ...], ...], segment_terminator='~', element_separator='*', file_path=None)
```

### Parsing an X12 Document from a File

```python
>>> document = X12Document.from_file("path/to/file.x12")
```

### Accessing and Editing the Data Element Separator and Segment Terminator

```python
>>> document.element_separator
'*'
>>> document.segment_terminator
'~'
>>> document.element_separator = ":"
>>> document.segment_terminator = "\n"
```

Note that for readability, these changes are not reflected in other sections below.

### Extracting Segments

```python
>>> document["ST"]
['ST', '810', '0001']
>>> document.get_single_segment("ST")
(2, ['ST', '810', '0001'])
>>> document.get_segments("N1")
[(4, ['N1', 'ST', 'ACME CORPORATION', '92', '1234']), (5, ['N1', 'BT', 'BUYER ORGANIZATION', '92', '5678'])]
>>> document["N1"]
Traceback (most recent call last):
...
KeyError: "2 segments found for filters 'N1'"
>>> document[["N1", "ST"]]
['N1', 'ST', 'ACME CORPORATION', '92', '1234']
>>> document.get_segments(["N1", "ST"])
[(4, ['N1', 'ST', 'ACME CORPORATION', '92', '1234'])]
>>> document[{1: "ST"}]
['N1', 'ST', 'ACME CORPORATION', '92', '1234']
```

### Updating Segment Data Elements

```python
>>> document["ISA"][6] = "ABCD"
>>> document["ISA"]
['ISA', '00', '          ', '00', '          ', 'ZZ', 'ABCD', ...]
```

Note that elements in the ISA segment will be padded appropriately when writing to string or file, but no guarantees are made about the padding when accessing the elements directly.

### Removing Segments

```python
>>> document.remove({1: "ST"})
1
>>> document.get_segments("N1")
[(4, ['N1', 'BT', 'BUYER ORGANIZATION', '92', '5678'])]
```

### Updating Transaction Set Trailers

This is also performed automatically when writing to string or file.

```python
>>> document.update_se_lengths()
```

### Writing Document to String

By default, the document is written without newlines.

```python
>>> content = document.to_string(newlines=True)
>>> print(content)
ISA*00*          *00*          *ZZ*ABCDEFGHIJKLMNO*ZZ*123456789012345*210101*1253*U*00401*000000001*0*T*:~
GS*IN*123456789*987654321*20210101*1253*1*X*004010~
ST*810*0001~
...
SE*8*0001~
GE*1*1~
IEA*1*000000001~

```

### Writing Document to a File

```python
>>> document.to_file("path/to/output.x12")
```

## License

This project is licensed under the GNU General Public License. See LICENSE file for details.
