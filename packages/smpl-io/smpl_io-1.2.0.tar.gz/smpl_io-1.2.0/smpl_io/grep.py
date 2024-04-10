import re
from io import StringIO

import smpl_doc.doc as doc

from .read_buffer import ReadBuffer


def grep(pattern, *inps, regex=False, open=True, A=0, B=0):
    """
    Searches for ``pattern`` in ``inp``.

    >>> from smpl_io import io
    >>> io.write("test.txt","hi\\nho1\\n2\\n3\\n4\\n")
    >>> grep("h","test.txt").read()
    'hi\\nho1\\n'
    >>> grep("h.*\\\\d","test.txt",regex=True).read()
    'ho1\\n'
    """
    r = StringIO()
    for inp in inps:
        with ReadBuffer(inp, open=open) as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                match = False
                for j in range(i - A, i + B + 1):
                    if j < 0 or j >= len(lines):
                        continue
                    if pattern in lines[j] or (regex and re.search(pattern, lines[j])):
                        match = True
                if match:
                    r.write(line)
    r.seek(0, 0)
    return r


grepf = doc.deprecated(
    version="1.0.6.1",
    removed_in="2.0.0",
    reason="Use :func:`smpl_io.grep(..., open=True)` instead.",
)(grep)
