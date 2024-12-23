
# Internal Libraries
import lxml.etree
import automatey.OS.FileUtils as FileUtils

# External Libraries
import lxml
import typing
import xml
    
class XML:
    
    '''
    XML representation.
    
    Note that,
    - XPath queries must always return an element.
    '''
    
    def __init__(self, root):
        self.root = root
    
    @staticmethod
    def fromFile(f:FileUtils.File) -> "XML":
        '''
        Read from XML file.
        '''
        tree = lxml.etree.parse(str(f))
        return XML(tree.getroot())
    
    def saveAs(self, f:FileUtils.File):
        '''
        Save as XML file.
        '''
        with f.openFile('wt') as handler:
            handler.writeAny(str(self))
    
    def XPath(self, query) -> typing.List["XML"]:
        '''
        Returns a list, the result of the given XPath query.
        '''
        result = self.root.xpath(query)
        return [XML(element) for element in result]

    def tag(self) -> str:
        '''
        Get tag.
        '''
        return self.root.tag
    
    def attributes(self) -> dict:
        '''
        Get attributes, as `dict`.
        '''
        return self.root.attrib
    
    def text(self) -> str:
        '''
        Get text. Returns `''` if no text is found.
        '''
        text = self.root.text if (self.root.text != None) else ''
        return text.strip()
    
    def __str__(self):
        return lxml.etree.tostring(self.root, pretty_print=True, encoding='unicode')

    def __repr__(self):
        return str(self)
