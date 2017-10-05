import lxml.etree as ET
from lxml.etree import tostring, fromstring, XMLParser

class Fault(object):
    def __init__(self, rung=None, prevLine=None):
        try:
            if prevLine is None:
                self.rungInit(rung)
            else:
                self.stInit(rung, prevLine)
            self.valid = True
        except:
            self.index = rung
            self.number = self.numberFormat(self.index)
            self.catagory = ""
            self.text = self.number
            self.literal = ""
            self.st = False
            self.valid = False
    
    def stInit(self, rung, prevLine):
        if "AOI_Fault_Set_Reset" in rung.text:
            self.fullElement = [rung, prevLine]
            self.index = int(rung.text.split(",")[2])
            self.number = self.numberFormat(self.index)
            self.catagory = self.catagoryFix(rung.text.split(",")[3].strip())
            self.literal = prevLine.text.strip()
            self.element = self.getElement(rung)
            self.text = self.getText(self.literal)
            self.st = True
        else:
            raise Exception

    def rungInit(self, rung):
        textElement = str(rung.find("Text").text)
        
        f = textElement.find("AOI_Fault_Set_Reset")
        
        if f == -1:
            raise Exception

        self.fullElement = rung.find("Text")

        textElement = textElement[f:]
        p = textElement.find(')')
        textElement = textElement[:p].split(',')[2:4]

        self.index = int(textElement[0])
        self.number = self.numberFormat(self.index)
        self.catagory = self.catagoryFix(textElement[1])
        self.literal = self.getLiteral(rung)
        self.element = self.getElement(rung)
        self.text = self.getText(self.literal)
        self.st = False

    def getText(self, literal):
        if len(literal.split(':')) == 2:
            comment = literal.split(':')[1]
        elif len(literal.split(':')) == 3:
            comment = literal.split(':')[1] + literal.split(':')[2]

        name = self.element.getparent().getparent().getparent().getparent().getparent().attrib['Name'].split("_")[1]
        mtn = name[:3]
        stn = name[3:]
        if stn == "":
            stn = "G3"
        if mtn[0] == '5':
            loop = "07"
        elif mtn[0] == '6':
            loop = "08"
        elif mtn[0] == '7':
            loop = "09"
        else:
            loop = "10"

        try:
            f = comment[1:].find(" ") + 1

            sensor = comment[1:f]

            if sensor == "Consecutive" or sensor == "Vehicle" or sensor == "At" or sensor == "Manual":
                comment = loop + mtn + "_" + stn + ":" + comment
            else:
                comment = comment[f:]
                comment = loop + mtn + "_" + stn + "_" + sensor + ":" + comment
        except:
            comment = "ERROR: NOT CORRECT FORMAT"

        return comment

    def format(self, text):
        text = text.strip()
        f = '>'*75
        text = f + '\n' + text + '\n' + f
        return text

    def getLiteral(self, rung):
        literal = rung.find("Comment")
        if literal is not None:
            r = literal.text.split("\n")[2]
            if r.count(">") > 2:
                r = literal.text.split("\n")[1]
            return r
        else:
            return False

    def giveNumber(self, value):
        newNum = value.split("_")[1]
        oldNum = self.number.split("_")[1]

        self.number = self.number.replace(oldNum, newNum)
        
        if self.st:
            string = tostring(self.fullElement[0])
        else:
            string = tostring(self.fullElement)

        newNum = bytes(str(int(newNum)), encoding="utf-8")
        oldNum = bytes(str(int(oldNum)), encoding="utf-8")
        
        string = string.replace(oldNum, newNum)

        replacement = fromstring(string, parser = XMLParser(strip_cdata=False))

        if self.st:
            self.fullElement[0].getparent().replace(self.fullElement[0], replacement)
            self.fullElement[0] = replacement

        else:
            self.fullElement.getparent().replace(self.fullElement, replacement)
            self.fullElement = replacement

        self.index = int(newNum)

    def giveLiteral(self, value):
        if not self.st:
            self.literal = value
            self.element.text = ET.CDATA(self.format(value))
            self.text = self.getText(self.literal)
        else:
            self.literal = value
            self.fullElement[1].text = ET.CDATA(value)
            self.text = self.getText(self.literal)

    def getElement(self, rung):
        element = rung.find("Comment")
        return element

    def catagoryFix(self, catagory):
        if "Warning" in catagory:
            return "M"
        elif "Stop" in catagory:
            return "C"
        elif "Abort" in catagory:
            return "I"

    def numberFormat(self, number):
        n = str(number)
        if len(n) == 1:
            return "Fault_00" + n
        if len(n) == 2:
            return "Fault_0" + n
        if len(n) == 3:
            return "Fault_" + n
