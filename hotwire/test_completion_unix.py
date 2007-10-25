# -*- tab-width: 4 -*-
import os, sys, unittest, tempfile, shutil, platform

import hotwire
from hotwire.command import HotwireContext
from hotwire.completion import *

class CompletionTestsUnix(unittest.TestCase):
    def setUp(self):
        self._tmpd = None
        self._context = HotwireContext()        

    def tearDown(self):
        if self._tmpd:
            shutil.rmtree(self._tmpd)
        self._context = None

    def _setupTree1(self):
        self._tmpd = tempfile.mkdtemp(prefix='hotwiretest')
        self._context.chdir(self._tmpd)
        testd = os.path.join(self._tmpd, 'testdir')
        os.mkdir(testd)
        open(os.path.join(self._tmpd, 'testf'), 'w').close()
        os.symlink(testd, os.path.join(self._tmpd, 'foolink'))

    def testCd1(self):
        self._setupTree1()
        cds = CdCompleter.getInstance()
        results = list(cds.search('test', context=self._context))
        self.assertEquals(len(results), 1)
        (mstr, start, mlen) = results[0].get_matchdata()
        self.assertEquals(mstr, os.path.join(self._tmpd, 'testdir/'))
        self.assertEquals(results[0].exact, False)
        
    def testCd2(self):
        self._setupTree1()
        cds = CdCompleter.getInstance()        
        results = list(cds.search('foo', context=self._context))
        self.assertEquals(len(results), 1)        
        (mstr, start, mlen) = results[0].get_matchdata()
        self.assertEquals(mstr, os.path.join(self._tmpd, 'foolink/'))
        self.assertEquals(results[0].exact, False)
