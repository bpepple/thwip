# -*- coding: utf-8 -*-

'''
Copyright 2012-2014  Anthony Beville
Copyright 2017 Brian Pepple
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from io import StringIO
import os
import sys
import zipfile

from natsort import natsorted

from .comicinfoxml import ComicInfoXML
from .filenameparser import FileNameParser
from .genericmetadata import GenericMetadata


try:
    from PIL import Image
    pil_available = True
except ImportError:
    pil_available = False


class MetaDataStyle:
    CIX = 1
    name = ['ComicRack', ]


class ZipArchiver:
    ''' Zip Implementation '''

    def __init__(self, path):
        self.path = path

    def readArchiveFile(self, archive_file):
        data = ""
        zf = zipfile.ZipFile(self.path, "r")

        try:
            data = zf.read(archive_file)
        except zipfile.BadZipfile as e:
            print >> sys.stderr, u"Bad zipfile [{0}]: {1} :: {2}".format(
                e, self.path, archive_file)
            zf.close()
            raise IOError
        except Exception as e:
            zf.close()
            print >> sys.stderr, u"Bad zipfile [{0}]: {1} :: {2}".format(
                e, self.path, archive_file)
            raise IOError
        finally:
            zf.close()
        return data

    def getArchiveFilenameList(self):
        try:
            zf = zipfile.ZipFile(self.path, "r")
            namelist = zf.namelist()
            zf.close()
            return namelist
        except Exception as e:
            print >> sys.stderr, u"Unable to get zipfile list [{0}]: {1}".format(
                e, self.path)
            return []


class UnknownArchiver:

    """Unknown implementation"""

    def __init__(self, path):
        self.path = path

    def readArchiveFile(self):
        return ""

    def getArchiveFilenameList(self):
        return []


class ComicArchive:
    logo_data = None

    class ArchiveType:
        Zip, Unknown = range(2)

    def __init__(self, path, default_image_path=None):
        self.path = path
        self.ci_xml_filename = 'ComicInfo.xml'
        self.resetCache()
        self.archive_type = self.ArchiveType.Unknown
        self.archiver = UnknownArchiver(self.path)
        self.default_image_path = default_image_path

        if self.zipTest():
            self.archive_type = self.ArchiveType.Zip
            self.archiver = ZipArchiver(self.path)

    def resetCache(self):
        """ Clears the cached data """
        self.has_cix = None
        self.page_count = None
        self.page_list = None
        self.cix_md = None

    def loadCache(self, style_list):
        for style in style_list:
            self.readMetadata(style)

    def rename(self, path):
        self.path = path
        self.archiver.path = path

    def zipTest(self):
        return zipfile.is_zipfile(self.path)

    def isZip(self):
        return self.archive_type == self.ArchiveType.Zip

    def isWritable(self):
        if self.archive_type == self.ArchiveType.Unknown:
            return False
        elif not os.access(self.path, os.W_OK):
            return False
        return True

    def isWritableForStyle(self, data_style):

        return self.isWritable()

    def seemsToBeAComicArchive(self):
        if (
            (self.isZip())
            and
            (self.getNumberOfPages() > 0)
        ):
            return True
        else:
            return False

    def readMetadata(self, style):
        if style == MetaDataStyle.CIX:
            return self.readCIX()
        else:
            return GenericMetadata()

    def hasMetadata(self, style):
        if style == MetaDataStyle.CIX:
            return self.hasCIX()
        else:
            return False

    def getPage(self, index):
        image_data = None
        filename = self.getPageName(index)

        if filename is not None:
            try:
                image_data = self.archiver.readArchiveFile(filename)
            except IOError:
                print >> sys.stderr, u"Error reading in page.  Substituting logo page."
                image_data = ComicArchive.logo_data

        return image_data

    def getPageName(self, index):
        if index is None:
            return None

        page_list = self.getPageNameList()

        num_pages = len(page_list)
        if num_pages == 0 or index >= num_pages:
            return None

        return page_list[index]

    def getScannerPageIndex(self):
        scanner_page_index = None

        # make a guess at the scanner page
        name_list = self.getPageNameList()
        count = self.getNumberOfPages()

        # too few pages to really know
        if count < 5:
            return None

        # count the length of every filename, and count occurences
        length_buckets = dict()
        for name in name_list:
            fname = os.path.split(name)[1]
            length = len(fname)
            if length in length_buckets:
                length_buckets[length] += 1
            else:
                length_buckets[length] = 1

        # sort by most common
        sorted_buckets = sorted(
            length_buckets.iteritems(),
            key=lambda k_v: (
                k_v[1],
                k_v[0]),
            reverse=True)

        # statistical mode occurence is first
        mode_length = sorted_buckets[0][0]

        # we are only going to consider the final image file:
        final_name = os.path.split(name_list[count - 1])[1]

        common_length_list = list()
        for name in name_list:
            if len(os.path.split(name)[1]) == mode_length:
                common_length_list.append(os.path.split(name)[1])

        prefix = os.path.commonprefix(common_length_list)

        if mode_length <= 7 and prefix == "":
            # probably all numbers
            if len(final_name) > mode_length:
                scanner_page_index = count - 1

        # see if the last page doesn't start with the same prefix as most
        # others
        elif not final_name.startswith(prefix):
            scanner_page_index = count - 1

        return scanner_page_index

    def getPageNameList(self, sort_list=True):
        if self.page_list is None:
            # get the list file names in the archive, and sort
            files = self.archiver.getArchiveFilenameList()

            # seems like some archive creators are on  Windows, and don't know
            # about case-sensitivity!
            if sort_list:
                def keyfunc(k):
                    return k.lower()
                files = natsorted(files, key=keyfunc, signed=False)

            # make a sub-list of image files
            self.page_list = []
            for name in files:
                if (name[-4:].lower() in [".jpg",
                                          "jpeg",
                                          ".png",
                                          ".gif",
                                          "webp"] and os.path.basename(name)[0] != "."):
                    self.page_list.append(name)

        return self.page_list

    def getNumberOfPages(self):

        if self.page_count is None:
            self.page_count = len(self.getPageNameList())
        return self.page_count

    def readCIX(self):
        if self.cix_md is None:
            raw_cix = self.readRawCIX()
            if raw_cix is None or raw_cix == "":
                self.cix_md = GenericMetadata()
            else:
                self.cix_md = ComicInfoXML().metadataFromString(raw_cix)

            # validate the existing page list (make sure count is correct)
            if len(self.cix_md.pages) != 0:
                if len(self.cix_md.pages) != self.getNumberOfPages():
                    # pages array doesn't match the actual number of images we're seeing
                    # in the archive, so discard the data
                    self.cix_md.pages = []

            if len(self.cix_md.pages) == 0:
                self.cix_md.setDefaultPageList(self.getNumberOfPages())

        return self.cix_md

    def readRawCIX(self):
        if not self.hasCIX():
            return None
        try:
            raw_cix = self.archiver.readArchiveFile(self.ci_xml_filename)
        except IOError:
            raw_cix = ""
        return raw_cix

    def hasCIX(self):
        if self.has_cix is None:
            if not self.seemsToBeAComicArchive():
                self.has_cix = False
            elif self.ci_xml_filename in self.archiver.getArchiveFilenameList():
                self.has_cix = True
            else:
                self.has_cix = False
        return self.has_cix

    def applyArchiveInfoToMetadata(self, md, calc_page_sizes=False):
        md.pageCount = self.getNumberOfPages()

        if calc_page_sizes:
            for p in md.pages:
                idx = int(p['Image'])
                if pil_available:
                    if 'ImageSize' not in p or 'ImageHeight' not in p or 'ImageWidth' not in p:
                        data = self.getPage(idx)
                        if data is not None:
                            try:
                                im = Image.open(StringIO.StringIO(data))
                                w, h = im.size

                                p['ImageSize'] = str(len(data))
                                p['ImageHeight'] = str(h)
                                p['ImageWidth'] = str(w)
                            except IOError:
                                p['ImageSize'] = str(len(data))

                else:
                    if 'ImageSize' not in p:
                        data = self.getPage(idx)
                        p['ImageSize'] = str(len(data))

    def metadataFromFilename(self, parse_scan_info=True):
        metadata = GenericMetadata()

        fnp = FileNameParser()
        fnp.parseFilename(self.path)

        if fnp.issue != "":
            metadata.issue = fnp.issue
        if fnp.series != "":
            metadata.series = fnp.series
        if fnp.volume != "":
            metadata.volume = fnp.volume
        if fnp.year != "":
            metadata.year = fnp.year
        if fnp.issue_count != "":
            metadata.issueCount = fnp.issue_count
        if parse_scan_info:
            if fnp.remainder != "":
                metadata.scanInfo = fnp.remainder

        metadata.isEmpty = False

        return metadata
