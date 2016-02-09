#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
A StringIO like class implement by Alex
"""

__author__ = "Alex"
__all__ = ["MyStringIO"]


def _test_ifclosed(closed):
    if closed:
        raise ValueError, "I/O operation on closed file"


class MyStringIO():
    def __init__(self, buf = ""):
        if not isinstance(buf, basestring):
            buf = str(buf)
        self.buf = buf
        self.length = len(buf)
        self.pos = 0
        self.closed = False

    def __iter__(self):
        return self

    def next(self):
        _test_ifclosed(self.closed)
        r = self.readline()
        if not r:
            raise StopIteration
        return r

    def close(self):
        """
        Set closed attribute to True. A closed buffer can not be used for
        further IO Operation. close() can be called more than once without
        error.
        """
        if not self.closed:
            self.closed = True
            del self.pos, self.buf

    def tell(self):
        """
        Return current file position.
        """
        _test_ifclosed(self.closed)
        return self.pos

    def seek(self, pos, whence = 0):
        """
        Set the file's current position.
        """
        _test_ifclosed(self.closed)
        spos = self.pos
        slen = self.length
        if whence == 1:
            pos += self.pos
        elif whence == 2:
            pos += self.length
        self.pos = max(0, pos)

    def read(self, size = -1):
        """
        Read at the most size bytes, return as a string.
        If the size argument is negative or omitted, read until EOF is reached.
        """
        _test_ifclosed(self.closed)
        if size < 0:
            newpos = self.length
        else:
            newpos = min(self.length, self.pos + size)
        r = self.buf[self.pos:newpos]
        self.pos = newpos
        return r

    def readline(self):
        """
        Read next line from file, return as a string.
        """
        _test_ifclosed(self.closed)
        sep = self.buf.find("\n", self.pos)
        newpos = self.length if sep == -1 else sep + 1
        r = self.buf[self.pos:newpos]
        self.pos = newpos
        return r

    def readlines(self, size = -1):
        """
        Call readline() repeatedly and return a list of the lines so read.
        The optional size argument, if given, is an approximate bound on the
        total number of bytes in the lines returned.
        """
        _test_ifclosed(self.closed)
        lines = []
        total = 0

        line = self.readline()
        while line: 
            lines.append(line)
            total += len(line)
            if 0 < size <= total:
                break
            line = self.readline()
        return lines
    
    def write(self, s):
        """
        Write string to buffer.
        """
        _test_ifclosed(self.closed)
        if not s: return
        if not isinstance(s, basestring):
            s = str(s)
        curpos = self.pos
        curlen = self.length
        slen = len(s)

        if curpos > curlen:
            self.buf += '\0' * (curpos - curlen)
            curlen = self.length = curpos

        newpos = curpos + slen
        if newpos < curlen:
            self.buf = self.buf[:curpos] + s + self.buf[newpos:]
        elif newpos == curlen:
            self.buf = self.buf[:curpos] + s
        else:
            self.length = newpos
            self.buf = self.buf[:curpos] + s
        self.pos = newpos

    def writelines(self, lines):
        """
        Write a sequence of string to the file.
        """
        _test_ifclosed(self.closed)
        for line in lines:
            self.write(line)
    
    def truncate(self, size = None):
        """
        Truncate the file to at most size bytes.
        Size default to the current file position, as returnd by tell()
        """
        _test_ifclosed(self.closed)
        if size is None:
            size = self.pos
        elif size < 0:
            raise IOError("Invalid argument")
        elif size < self.length:
            self.pos = size
        self.buf = self.buf[:size]
        self.length = size

    def getvalue(self):
        """
        Return the value of buffer.
        """
        _test_ifclosed(self.closed)
        return self.buf


def test():
    import sys
    if sys.argv[1:]:
        file = sys.argv[1]
    else:
        file = '/etc/passwd'
    lines = open(file, 'r').readlines()
    text = open(file, 'r').read()
    f = MyStringIO()
    for line in lines[:-2]:
        f.write(line)
    f.writelines(lines[-2:])
    if f.getvalue() != text:
        raise RuntimeError, 'write failed'
    length = f.tell()
    print 'File length =', length
    print 'Text length =', len(text)
    f.seek(len(lines[0]))
    print "Position =", f.tell()
    f.write(lines[1])
    print f.getvalue()
    f.seek(0)
    print 'First line =', repr(f.readline())
    print 'Position =', f.tell()
    line = f.readline()
    print 'Second line =', repr(line)
    f.seek(-len(line), 1)
    line2 = f.read(len(line))
    if line != line2:
        raise RuntimeError, 'bad result after seek back'
    f.seek(len(line2), 1)
    l = f.readlines()
    line = l[-1]
    f.seek(f.tell() - len(line))
    line2 = f.read()
    if line != line2:
        raise RuntimeError, 'bad result after seek back from EOF'
    print 'Read', len(l), 'more lines'
    print 'File length =', f.tell()
    if f.tell() != length:
        raise RuntimeError, 'bad length'
    f.truncate(length/2)
    f.seek(0, 2)
    print 'Truncated length =', f.tell()
    if f.tell() != length/2:
        raise RuntimeError, 'truncate did not adjust length'
    f.close()


if __name__ == '__main__':
    test()
