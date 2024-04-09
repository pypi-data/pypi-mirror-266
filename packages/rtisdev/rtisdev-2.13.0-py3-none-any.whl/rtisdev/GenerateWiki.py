from docstr_md.python import PySoup, compile_md
from docstr_md.src_href import Github
from shutil import copyfile
import os
import md_toc

copyfile('RTISDev.py', 'RTISDev2.py')

fileR = open('RTISDev2.py', 'r')
Lines = fileR.readlines()
fileR.close()

fileW = open('RTISDev2.py', 'w')
for line in Lines:

    line = line.replace("in rtisdev/config/premadeSettings/processing/", "[here](rtisdev/config/premadeSettings/processing/)")
    line = line.replace("in rtisdev/config/premadeSettings/recording/test.csv",
                        "[here](rtisdev/config/premadeSettings/recording/test.csv)")
    line = line.replace("in rtisdev/config/premadeSettings/recording/", "[here](rtisdev/config/premadeSettings/recording/)")
    line = line.replace("`MeasureExternalTriggerCallbackThread`", "[`MeasureExternalTriggerCallbackThread`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#measureexternaltriggercallbackthread)")
    line = line.replace("`MeasureExternalTriggerQueueThread`", "[`MeasureExternalTriggerQueueThread`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#measureexternaltriggerqueuethread)")
    line = line.replace("`RTISMeasurement`", "[`RTISMeasurement`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#rtismeasurement)")
    line = line.replace("`RTISSettings`", "[`RTISSettings`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#rtissettings)")
    line = line.replace("CTRL+C", "<kbd>CTRL</kbd>+<kbd>C</kbd>")
    line = line.replace("::", ":")
    line = line.replace("`create_measure_external_trigger_queue(dataQueue)`", "[`create_measure_external_trigger_queue(dataQueue)`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#create_measure_external_trigger_queue)")
    line = line.replace("`create_measure_external_trigger_callback(callback)`", "[`create_measure_external_trigger_callback(save_callback)`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#create_measure_external_trigger_callback)")
    line = line.replace("`get_premade_recording_settings_list()`", "[`get_premade_recording_settings_list()`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#get_premade_processing_settings_list)")
    line = line.replace("`get_premade_processing_settings_list()`", "[`get_premade_processing_settings_list()`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#get_premade_recording_settings_list)")
    line = line.replace("`get_raw_measurement(behaviour)`", "[`get_raw_measurement(behaviour)`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#get_raw_measurement)")
    line = line.replace("`get_processed_measurement(behaviour)`", "[`get_processed_measurement(behaviour)`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#get_processed_measurement)")
    line = line.replace("`get_signal_measurement(behaviour)`", "[`get_signal_measurement(behaviour)`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#get_signal_measurement)")
    line = line.replace("`get_settings()`", "[`get_settings()`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#get_settings)")
    line = line.replace("`get_current_settings()`", "[`get_current_settings()`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#get_current_settings)")
    line = line.replace("`set_recording_settings()`", "[`set_recording_settings()`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#set_recording_settings)")
    line = line.replace("`set_processing_settings()`", "[`set_processing_settings()`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#set_processing_settings)")
    line = line.replace("rtisdev/config/premadeSettings/", "https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/blob/master/rtisdev/config/premadeSettings/")
    line = line.replace("`prepare_processing()`", "[`set_processing_settings()`](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#prepare_processing)")
    fileW.writelines(line)
fileW.close()

src_href = Github('https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/blob/master/rtisdev')
soup = PySoup(path='RTISDev2.py', parser='sklearn', src_href=src_href)
compile_md(soup, compiler='sklearn', outfile='../WIKI.md')

fileR = open('../WIKI.md', 'r')
Lines = fileR.readlines()
fileR.close()

fileW = open('../WIKI.md', 'w')

exampleStarted = False
examplePassed = False
classesReached = False
emptyLine = False
emptyDescription = False

codeExampleStarted = False
jsonExampleStarted = False
multiLineCode = False

for line in Lines:
    if line == "Here is a small example that goes over most basic steps:\n":
        fileW.write("# **General Example**\n\n")
        exampleStarted = True
    if line == "For more examples, check the small method examples in the documentation.\n":
        examplePassed = True
    if line == "##RTISDev2.**RTISMeasurement**\n":
        classesReached = True
        fileW.writelines("# **Classes**\n\n")
    if line == "##RTISDev2.**open_connection**\n":
        fileW.writelines("# **Methods**\n\n")
    if emptyLine:
        if line == "    </tbody>\n":
            emptyDescription = True
            emptyLine = False
    if line == "        \n":
        emptyLine = True
    else:
        emptyLine = False

    if ">>>" in line and not codeExampleStarted:
        codeExampleStarted = True
        fileW.writelines("```python\n")
        if len(line) >= 2:
            if line[-2] is ",":
                multiLineCode = True
                line = line.replace("\n", " ")
            else:
                multiLineCode = False
    if codeExampleStarted and ">>>" not in line and "..." not in line:
        if not multiLineCode:
            codeExampleStarted = False
            fileW.writelines("```\n")
        else:
            line = line.replace("  ", "")
    if codeExampleStarted and len(line) >= 2:
        if (">>>" in line and line[-2] is ",") or (multiLineCode and line[-2] is ","):
            multiLineCode = True
            line = line.replace("\n", " ")
        else:
            multiLineCode = False
    print
    if '{' == line.replace("\n", "") and not codeExampleStarted:
        jsonExampleStarted = True
        fileW.writelines("```json\n")
    if codeExampleStarted:
        line = line.replace(">>> ", "")
        line = line.replace("...     ", "____")
        line = line.replace("...         ", "________")
        line = line.replace("...             ", "____________")
    if jsonExampleStarted and '}' != line.replace("\n", "") and '{' != line.replace("\n", ""):
        line = "    " + line
    if (exampleStarted and not examplePassed) or classesReached and not emptyDescription:
        line = line.replace("####", "#### ")
        line = line.replace("##RTISDev2.*", "## *")
        line = line.replace("RTISDev2.<b>", "<b>")
        line = line.replace("____", "    ")
        line = line.replace("https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/blob/master/rtisdev/RTISDev2.py#", "https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/blob/master/rtisdev/RTISDev.py#")
        fileW.writelines(line)
    if emptyDescription:
        emptyDescription = False
    if jsonExampleStarted and '}' == line.replace("\n", ""):
        jsonExampleStarted = False
        fileW.writelines("```\n")

fileW.close()

with open('../WIKI.md','r') as f:
    with open('../WIKITOC.md','w') as f2:
        f2.write("# **RTIS Dev Documentation - Table of Content**\n\n")
        f2.write(md_toc.build_toc('../WIKI.md').replace("**", "").replace("\r", "") + " \n")
        f2.write(f.read())
os.remove('../WIKI.md')
os.rename('../WIKITOC.md', '../WIKI.md')

os.remove("RTISDev2.py")

