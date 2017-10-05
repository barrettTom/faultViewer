import lxml.etree as ET
from lxml.etree import tostring, fromstring, XMLParser

class Fault(object):
    def __init__(self, element):
        try:
            if element.tag == "Rung":
                self.rungInit(element)
            else:
                self.stInit(element)
            self.valid = True
        except:
            self.index = element
            self.number = self.numberFormat(self.index)
            self.catagory = ""
            self.text = self.number
            self.literal = ""
            self.valid = False

    def rungInit(self, rung):
        textElement = str(rung.find("Text").text)

        f = textElement.find("AOI_Fault_Set_Reset")
        if f == -1:
            raise Exception

        textElement = textElement[f:]
        p = textElement.find(')')
        textElement = textElement[:p].split(',')[2:4]

        self.element = rung
        self.index = int(textElement[0])
        self.number = self.numberFormat(self.index)
        self.catagory = self.catagoryFix(textElement[1])
        self.literal = self.getLiteral(rung)
        self.text = self.getText(self.literal)
        self.st = False

    def stInit(self, line):
        if "AOI_Fault_Set_Reset" in line.text:
            self.element = line
            self.index = int(line.text.split(",")[2])
            self.number = self.numberFormat(self.index)
            self.catagory = self.catagoryFix(line.text.split(",")[3].strip())
            self.literal = line.getprevious().text.strip()
            self.text = self.getText(self.literal)
            self.st = True
        else:
            raise Exception

    def getText(self, literal):
        if len(literal.split(':')) == 2:
            comment = literal.split(':')[1]
        elif len(literal.split(':')) == 3:
            comment = literal.split(':')[1] + literal.split(':')[2]

        name = self.element.getparent().getparent().getparent().getparent().attrib['Name'].split("_")[1]
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
        
        if not self.st:
            string = tostring(self.element.find("Text"))
        else:
            string = tostring(self.element)

        newNum = bytes(str(int(newNum)), encoding="utf-8")
        oldNum = bytes(str(int(oldNum)), encoding="utf-8")
        
        string = string.replace(oldNum, newNum)

        replacement = fromstring(string, parser = XMLParser(strip_cdata=False))

        if not self.st:
            self.element.replace(self.element.find("Text"), replacement)
        else:
            self.element.getparent().replace(self.element, replacement)
            self.element = replacement

        self.index = int(newNum)

    def giveLiteral(self, value):
        if not self.st:
            self.literal = value
            self.element.find("Comment").text = ET.CDATA(self.format(value))
            self.text = self.getText(self.literal)
        else:
            self.literal = value
            self.element.getprevious().text = ET.CDATA(value)
            self.text = self.getText(self.literal)

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
