# Readme

KPCommons is a collection of methods which are regularly needed.

## Util

Util.py contains a method to calculate the overlap between two ranges. For example,

~~~
Util.calculate_overlap(0, 10, 5, 10)
~~~

would return a result of 5. The first two arguments are the start and end position of the first range, and the last two
arguments are the positions of the second range.

**Note**: In case of no overlap, the distance between the two ranges is returned as a negative result.

## Footnote

Footnote.py contains a collection of methods for working with footnotes.