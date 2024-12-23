
# Internal Libraries
import lxml.etree
import automatey.OS.FileUtils as FileUtils

# External Libraries
import lxml
import typing
import copy
    
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

    def getTag(self) -> str:
        '''
        Get tag.
        '''
        return self.root.tag
    
    def setTag(self, tag:str):
        '''
        Set tag.
        '''
        self.root.tag = tag
    
    def attributes(self) -> dict:
        '''
        Get attributes, as `dict`.
        
        Note,
        - It can be used for reading, and setting attributes.
        '''
        return self.root.attrib
    
    def getText(self) -> str:
        '''
        Get text. Returns `''` if no text is found.
        '''
        text = self.root.text if (self.root.text != None) else ''
        return text.strip()
    
    def setText(self, text:str):
        '''
        Set text.
        '''
        self.root.text = text
    
    def __str__(self):
        return lxml.etree.tostring(self.root, pretty_print=True, encoding='unicode')

    def __repr__(self):
        return str(self)
    
    # Formatting-specific operation(s)
    
    def removeChildElement(self, xml:"XML"):
        self.root.remove(xml.root)
    
    def copyElement(self) -> "XML":
        return copy.deepcopy(self)
    
    def insertElement(self, xml:"XML", idx:int=-1):
        if idx == -1:
            self.root.append(xml.root)
        else:
            self.root.insert(idx, xml.root)