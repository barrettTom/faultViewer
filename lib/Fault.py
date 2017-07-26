import lxml.etree as ET

class Fault(object):
    def __init__(self, program, rung=None):
        self.program = program
        self.rung = rung
        try:
            textElement = str(rung.find("Text").text)

            f = textElement.find("AOI_Fault_Set_Reset")

            if f == -1:
                self.valid = False
                return

            textElement = textElement[f:]
            p = textElement.find(')')
            textElement = textElement[:p].split(',')[2:4]

            self.number = int(textElement[0])
            self.catagory = textElement[1]

            self.literal = self.getLiteral()
            self.text = self.getText(self.literal)
            self.element = self.getElement()

            self.valid = True
        except:
            self.number = program
            self.catagory = ""
            self.text = ""
            self.literal = ""
            self.valid = False

    def getText(self, literal):
        if len(literal.split(':')) == 2:
            comment = literal.split(':')[1]
        elif len(literal.split(':')) == 3:
            comment = literal.split(':')[1] + literal.split(':')[2]

        name = self.program.attrib['Name'].split("_")[1]
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

            if sensor == "Consecutive" or sensor == "Vehicle":
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

    def getLiteral(self):
        literal = self.rung.find("Comment")
        if literal is not None:
            r = literal.text.split("\n")[2]
            if ">" in r:
                r = literal.text.split("\n")[1]
            return r
        else:
            return False

    def giveLiteral(self, value):
        self.literal = value
        self.element.text = ET.CDATA(self.format(value))
        
        self.text = self.getText(self.literal)

    def getElement(self):
        element = self.rung.find("Comment")
        return element

    def fix(self):
        self.catagoryFix()
        self.numberFix()

    def catagoryFix(self):
        if "Warning" in self.catagory:
            self.catagory = "M"
        elif "Stop" in self.catagory:
            self.catagory = "C"
        elif "Abort" in self.catagory:
            self.catagory = "I"
        return self

    def numberFix(self):
        n = str(self.number)
        if len(n) == 1:
            self.number = "Fault_00" + n
        if len(n) == 2:
            self.number = "Fault_0" + n
        if len(n) == 3:
            self.number = "Fault_" + n
        if self.text == "":
            self.text = self.number

