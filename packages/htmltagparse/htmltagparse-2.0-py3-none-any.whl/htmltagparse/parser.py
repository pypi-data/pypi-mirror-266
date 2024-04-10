import re
import htmltagparse
from .html_tags import *
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import timeoutcall
from .exceptions import *
import re
import warnings

__all__ = [
    "HtmlPage",
    "html2txt",
    "getElementAttributes",
    "getElementAttributeValue",
    "getTagContents",
]

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

def searchForGroup(pattern: str, text: str, group: str) -> str:
    try:
        return re.search(pattern, text, flags=(re.MULTILINE | re.DOTALL)).group(group)
    except:
        return

# large pages may hang script
def findTags(htmlContent: str) -> list:
    foundTags = []
    for tag in voidTags:
        tagSearch = re.search(rf"<{tag}\s?(?:.*?)?/?>", htmlContent, re.MULTILINE | re.DOTALL)
        if bool(tagSearch):
            foundTags.append(tag)
    for tag in nonVoidTags:
        tagSearch = re.search(rf"<{tag}\s?(?:.*?)>(?:.*?)</{tag}>", htmlContent, re.MULTILINE | re.DOTALL)
        if bool(tagSearch):
            foundTags.append(tag)
    return foundTags

# large pages may hang script
def findSources(htmlContent: str) -> list:
    foundSources = {}
    for tag in all_tags:
        allSourcesFound = re.findall(rf"<{tag} (?:[^>]*?)src=(?:\"|')(?P<src>.*?)(?:\"|')/?>", htmlContent, re.MULTILINE | re.DOTALL)
        if bool(allSourcesFound):
            foundSources[tag] = allSourcesFound
    return foundSources

def findHrefs(htmlContent: str) -> list:
    foundHrefs = {}
    for tag in tagsWithHref:
        if tag in voidTags:
            tagInfo = re.findall(rf"<{tag} (?:[^>]*?)href=(?:\"|')(?P<href>.*?)(?:\"|')(?:.*?)/?>", htmlContent, re.MULTILINE | re.DOTALL)
        elif tag in nonVoidTags:
            tagInfo = re.findall(rf"<{tag} (?:[^>]*?)href=(?:\"|')(?P<href>.*?)(?:\"|')(?:.*?)>(?:.*?)</{tag}>", htmlContent, re.MULTILINE | re.DOTALL)
        if tagInfo != []:
            foundHrefs[tag] = tagInfo
    return foundHrefs

def findIds(htmlContent: str) -> list:
    foundIds = []
    for tag in voidTags:
        tagIds = re.findall(rf"<{tag} (?:[^>]*?)id=(?:\"|')(?P<id>.*?)(?:\"|')(?:.*?)/?>", htmlContent, re.MULTILINE | re.DOTALL)
        for i in tagIds:
            foundIds.append(i)
    for tag in nonVoidTags:
        tagIds = re.findall(rf"<{tag} (?:[^>]*?)id=(?:\"|')(?P<id>.*?)(?:\"|')(?:.*?)>(?:.*?)</{tag}>", htmlContent, re.MULTILINE | re.DOTALL)
        for i in tagIds:
            foundIds.append(i)
    return foundIds

def getElementAttributeValue(elementOuterHtml: str, attrName: str) -> str:
    """Returns the value of an html attribute value

    :param elementOuterHtml: the outerHtml text to be searched
    :param attrName:         the attribute value of which contains the value to be returned"""
    elementOuterHtml = elementOuterHtml[elementOuterHtml.index("<"):]
    tagName = searchForGroup(r"^<(?P<tag>\w+)", elementOuterHtml, "tag")
    attrValue = searchForGroup(rf"<{tagName} (?:[^>]*?){attrName}=(?:\"|')(?P<value>.*?)(?:\"|')(?:.*?)/?>", elementOuterHtml, "value")
    return attrValue

def getElementAttributes(elementOuterHtml: str) -> dict[str, str]:
    """Returns a dictionary of attributes associated with an HTML element.

    :param elementOuterHtml: the outerHtml text to be searched"""
    elementOuterHtml = elementOuterHtml[elementOuterHtml.index("<"):]
    tagName = searchForGroup(r"^<(?P<tag>\w+)", elementOuterHtml, "tag")
    tagOpening = searchForGroup(rf"<{tagName} (?P<opening>.*?)>", elementOuterHtml, "opening")
    attributeList = re.findall(r"(?P<attr>\w+)=(?:\"|')(?P<value>.*?)(?:\"|')", tagOpening)
    attributes = {}
    for attr in attributeList:
        attributes[attr[0]] = attr[1]
    return attributes

def getTagContents(elementOuterHtml: str) -> str:
    """Returns the contents of an HTML element.

    :param elementOuterHtml: the outer html of the element which contains the contents to be returned"""
    elementOuterHtml = elementOuterHtml[elementOuterHtml.index("<"):]
    tagName = searchForGroup(r"^<(?P<tag>\w+)", elementOuterHtml, "tag")
    tagContents = searchForGroup(rf"<{tagName}\s?(?:.*?)?>(?P<content>.*?)</{tagName}>", elementOuterHtml, "content")
    return tagContents

def getHtmlMetadata(htmlContent: str) -> list[dict]:
    metadataContents = []
    metaTags = re.findall(r"<meta (?:.*?)/?>", htmlContent, re.MULTILINE | re.DOTALL)
    for i in range(len(metaTags)):
        metaTags[i] = re.sub(r"<meta (?P<cont>.*?)/?>", r"\g<cont>", metaTags[i])
    for tag in metaTags:
        workingMetadata = re.findall(r"(?P<attr>\w+)=(?:\"|')(?P<value>.*?)(?:\"|')", tag)
        workingMetadataDict = {}
        for meta in workingMetadata:
            workingMetadataDict[meta[0]] = meta[1]
        metadataContents.append(workingMetadataDict)
    return metadataContents

def html2txt(htmlContent: str):
    """Parses HTML data into plain text."""
    return BeautifulSoup(str(htmlContent), features="html5lib").get_text()

class HtmlPage:
    """Contains information from HTML text."""
    def __init__(self, htmlContent: str, timeout=5):
        self.html = htmlContent if htmlContent != None else ''
        self.text = html2txt(htmlContent)
        self.uri = None
        self.response = None
        self.title = htmltagparse.titleFromHtml(htmlContent)
        self.sources = findSources(htmlContent)
        self.hrefs = findHrefs(htmlContent)
        self.ids = findIds(htmlContent)
        self.lang = searchForGroup(r"<html (?:.*?)lang=(?:\"|')(?P<lang>.*?)(?:\"|')(?:.*?)>", self.html, "lang")
        self.encoding = searchForGroup(r"<meta (?:.*?)charset=(?:\"|')(?P<encoding>.*?)(?:\"|')(?:.*?)/?>", self.html, "encoding")
        self.metadata = getHtmlMetadata(self.html)
        try:
            self.tags = timeoutcall.call(findTags, timeout, "could not fetch tags within timeout duration", htmlContent)
        except TimeoutError as ERROR:
            self.tags = HtmlTagError(str(ERROR))
    def __str__(self):
        return self.uri
    def __repr__(self):
        return repr(list(vars(self)))
    def searchTagExists(self, tagName: str) -> bool:
        """Checks if the specified tag appears within the page html.

        :param tagName: name of tag to be validated"""
        if not tagName in all_tags:
            return False
        return bool(re.search(rf"<{tagName}\s?(?:.*?)/?>", self.html, re.MULTILINE | re.DOTALL))
    def searchTag(self, tagName: str, htmlFormat=True) -> list:
        """Returns a list of HTML tag occurrences.

        :param tag:        the tag name to be searched
        :param htmlFormat: determines whether the target text will be html or text format"""
        contents = []
        if tagName in voidTags:
            for t in re.findall(rf'<{tagName}\s?(?:.*?)/?>', self.html, flags=(re.M|re.S)):
                contents.append(t)
        else:
            for t in re.findall(rf'<{tagName}\s?(?:.*?)?>(?:.*?)</{tagName}>', self.html, flags=(re.M|re.S)):
                contents.append(t)
        if not htmlFormat:
            for i in range(len(contents)):
                contents[i] = html2txt(str(contents[i]))
        return contents
    def regex(self, pattern: str, findall=False, htmlFormat=True):
        """Search page content with a regex pattern.
        Regex flags "re.MULTILINE" and "re.DOTALL" are in use with this function.

        :param pattern:    the regex pattern which will be used to search page content
        :param findall:    returns a list of text which matches the specified regex pattern
        :param htmlFormat: determines whether the target text will be html or text format"""
        targetText = str(self.html) if htmlFormat else str(self.text)
        compiledPattern = re.compile(pattern, flags=(re.MULTILINE | re.DOTALL))
        regexMatch = compiledPattern.search(targetText) if not findall else compiledPattern.findall(targetText)
        return regexMatch
    def getIdContents(self, elementId: str) -> str:
        """Returns the innerHtml contents of an element with a specified ID.

        :param elementId: the id of which is assigned to the element that contains the contents to be returned"""
        for tag in nonVoidTags:
            idContent = searchForGroup(rf"<(?:{tag}) (?:.*?)id=(?:\"|')(?:{elementId})(?:\"|')(?:.*?)>(?P<content>.*?)</{tag}>", self.html, "content")
            if idContent != None:
                return idContent
