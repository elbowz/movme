#!/usr/bin/python
# -*- coding: utf-8 -*-

# =======================================
# movme v1.6b - Copyright 2012
# Writted by muttley
# Get last version from http://code.google.com/p/unuseful-code/
# =======================================

import os
import sys
import getopt
from subprocess import call

# set 'UTF-8' standart default encoding
reload(sys)
sys.setdefaultencoding('UTF-8')

# GLOBAL VAR

# script file name
g_script = os.path.basename(sys.argv[0])
# script file absolute path
g_script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
# simulated mode 
g_simulated = False
# verbose mode 
g_verbose = 0
# config file name 
g_xml_config_file = "/etc/movme.xml"
# config file name 
g_log_file = None

# appiccico per evitare che riapra il file ogni volta
g_xml_cfg = None


def main (args):

    # PARSE OPTIONS/ARGUMENT

    try:
        opts, args = getopt.getopt(args, "hsrav:c:l:d:f:", [ '--help','--simulate', '--recursive', '--dirasfile', 
                                                            'verbose=', 'config=', 'log=', 'dir=', 'file=' ])
    except getopt.error:
        help()
        setLog(0, "Parametri errati!", LOG_BD_ERROR, 1)        

    arg_dir = arg_file = None
    arg_visit_type = MOV_BD_LISTFILES
    global g_verbose, g_xml_config_file, g_log_file, g_simulated

    # init var with arg parameters
    for opt, val in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit(0)
        if opt in ('-s', '--simulate'):
    	    g_simulated = True
        if opt in ('-r', '--recursive'):
    	    arg_visit_type = MOV_BD_RECURSIVE
        if opt in ('-a', '--recursive'):
    	    arg_visit_type = MOV_BD_DIRASFILE
        if opt in ('-v', '--verbose'):
    	    g_verbose = int(val)
        if opt in ('-c', '--config'):
    	    g_xml_config_file = val
        if opt in ('-l', '--log'):
    	    g_log_file = val
        if opt in ('-d', '--dir'):
    	    arg_dir = val
        if opt in ('-f', '--file'):
    	    arg_file = val

    # ERROR CHECK

    # minimal options
    if(arg_dir == None and arg_file == None):
        help()
        setLog(0, "Devi indicare una directory (\033[1m-d\033[22m) o un file (\033[1m-f\033[22m)", LOG_BD_ERROR, 1)

    # not compatible options
    if(arg_dir != None and arg_file != None):
        help()
        setLog(0, "Non puoi indicare sia una directory (\033[1m-d\033[22m) che un file (\033[1m-f\033[22m)!", LOG_BD_ERROR, 1)
    
    # for -d option
    if(arg_dir != None): 
        # path exist
        if(not os.path.exists(arg_dir)):
            setLog(0, "\033[1m%s\033[22m non esiste!" % arg_dir, LOG_BD_ERROR, 1)
        # is a dir        
        if(not os.path.isdir(arg_dir)):
            setLog(0, "\033[1m%s\033[22m non è una directory!" % arg_dir, LOG_BD_ERROR, 1)
        # is writable
        if(not os.access(arg_dir, os.W_OK or os.X_OK)):
            setLog(0, "Non posso scrivere in \033[1m%s\033[22m" % arg_dir, LOG_BD_ERROR, 1)

        movDirFiles(unicode(arg_dir), arg_visit_type)

    # for -f option
    else:       
        # path exist
        if(not os.path.exists(arg_file)):
            setLog(0, "\033[1m%s\033[22m non esiste!" % arg_file, LOG_BD_ERROR, 1)
        # is a file        
        if(not os.path.isfile(arg_file)):
            setLog(0, "\033[1m%s\033[22m non è un file!" % arg_file, LOG_BD_ERROR, 1)

        movFile(unicode(arg_file))

    # exit without errors
    sys.exit(0)


# quick help
def help ( ):
    global g_script

    print '\nUsage: %s [-h -s][-v X] [-c path/to/file.xml] [-l path/to/file.log] {-d path/to/dir/ [-r | -a] | -f path/to/file}' % g_script
    print '''
    \033[1m-h\033[22m          displays this help usage        --help
    \033[1m-s\033[22m          don't move files (use with -v)  --simulate
    \033[1m-r\033[22m          with -d walk on sub-dirs        --recursive
    \033[1m-a\033[22m          with -d manage dirs as files    --dirasfile
    \033[1m-v X\033[22m        verbose mode X = [1:3]          --verbose
    \033[1m-c path\033[22m     config file                     --config=path    
    \033[1m-l path\033[22m     make file log                   --log=path
    \033[1m-d path\033[22m     target dir path                 --dir=path
    \033[1m-f path\033[22m     target file path                --file=path           
    '''
    print 'Move all files (also in sub-dirs --recursive):\033[33m\n %s -r -d /home/user/.aMule/Incoming\033[39m\n' % g_script
    print 'Move Alien3.avi and create a log file:\033[33m\n %s -v 2 -l /home/user/.aMule/movme.log -f /home/user/.aMule/Incoming/Alien3.avi\033[39m\n' % g_script
    print 'Testing xml config (don\'t move anythings):\033[33m\n %s -v 2 -s -r -d /home/user/.aMule/Incoming\033[39m\n' % g_script

import shutil
# os.path.supports_unicode_filenames = True     # for unicode filename support

# type of dir visit
MOV_BD_RECURSIVE = 0
MOV_BD_DIRASFILE = 1
MOV_BD_LISTFILES = 2

# move files in dir by config.xml rules
# @src_path: char - dir path to move
# @visit_type: int - MOV_BD_RECURSIVE enter in sub-directory
#                    MOV_BD_DIRASFILE don't enter in sub-directory and manage dirs as files
#                    MOV_BD_LISTFILES list only file of src_path
# @return: bool - True files moved, False otherwise
def movDirFiles (src_path, visit_type = MOV_BD_LISTFILES):

    file_list = []  # file list with path

    # not recursive visit ( MOV_BD_LISTFILES or MOV_BD_DIRASFILE )
    if( visit_type ):
        for file_name in os.listdir(src_path):
            if (visit_type == MOV_BD_DIRASFILE or os.path.isfile(os.path.join(src_path, file_name))):   # only file (if visit_type = MOV_BD_LISTFILES)
                file_list.append(os.path.join(src_path, file_name))

    # get file also in sub-directory
    else:
        for root, dirs, files in os.walk(src_path, True, None):
            for name in files:
                file_list.append(os.path.join(root, name))

    # move all file by rules in config.xml
    for file_name in file_list:
        movFile(file_name)
           

# move file by config.xml rules
# @src_path: char - file path to move
# @return: bool - True file moved, False otherwise
def movFile (src_path):

    i = -1
    priority = {}   # dictionary with key: priority and value: filter path and filter name
    
    setLog(2, "File: \033[1m%s\033[22m in %s" % (os.path.basename(src_path),os.path.dirname(src_path)), LOG_BD_INFO)

    while True:
        i += 1
        status, filter = getFilter(i)
#        import pprint
#
#        pprint.pprint(filter)

        # filter 'i' don't extist => end of filter list
        if( not status ): break
        elif ( status == -1 ): continue  # filter 'i' is bad formatting => go next

        setLog(3, "---==| %02d \033[1m%s\033[22m (\033[4m%s\033[24m) filter analyzing  ==---" % (i, filter['name'], filter['path']), LOG_BD_INFO)

        # add key: priority (int) to dictionary
        current_priority = getPriority(src_path,filter['rules'])
        priority[ current_priority ] = filter
        
        setLog(2, "---== %02d \033[1m%s\033[22m (\033[4m%s\033[24m) priority = \033[1m%d\033[22m  ==---" % (i, filter['name'], filter['path'], current_priority), LOG_BD_INFO)

    # get the biggest priority filter
    sorted_priority_key = priority.keys()
    sorted_priority_key.sort()
    
    # noone filter get a positive priority
    if ( sorted_priority_key[-1] <= 0 ):
        setLog(1, "File: \033[1m%s\033[22m nessun filtro ha ottenuto priorita' positiva!" % src_path, LOG_BD_INFO)
        return False
    else:
        used_filter = priority[ sorted_priority_key[-1] ]
        setLog(2, "Winner filter is: \033[1m%s\033[22m with \033[1m%d\033[22m" % (used_filter['name'],sorted_priority_key[-1]), LOG_BD_INFO)        
    
    try:
        global g_simulated       
    
        # make destination dir/dirs if requested
        if (used_filter['mkdir']):
            if (not os.path.exists(used_filter['path'])):
                if (not g_simulated): 
                    os.makedirs(used_filter['path'])
                    # Set dir permission
                    if ( int(used_filter['mkdir']) != 1 ): os.system( 'chmod "%s" "%s"' % (used_filter['mkdir'], used_filter['path']) )
                
                # Logging
                if ( int(used_filter['mkdir']) != 1 ):
                    setLog(1, "Dir \033[1m%s\033[22m creata con permessi a \033[1m%s\033[22m!" % (used_filter['path'], used_filter['mkdir']), LOG_BD_INFO)
                else:
                    setLog(1, "Dir \033[1m%s\033[22m creata!" % (used_filter['path']), LOG_BD_INFO)
        
        # move the file
        if (not g_simulated):
            if (not os.path.isdir(src_path)):
                # shutil.move(src_path,used_filter['path'])
                os.system( 'mv "%s" "%s"' % (src_path, used_filter['path']) )
            else:   # ...or move de dir
                # shutil.move(src_path, os.path.join(used_filter['path'], os.path.basename(src_path)))
                os.system( 'mv "%s" "%s"' % (src_path, os.path.join(used_filter['path'], os.path.basename(src_path))) )

        setLog(1, "\033[1m%s\033[22m -> \033[4m%s\033[24m (by %s filter)" % (src_path, used_filter['path'], used_filter['name']), LOG_BD_INFO)

    except:
        setLog(0, "Impossibile spostare il file \033[1m%s\033[22m to \033[4m%s\033[24m!" % (src_path,used_filter['path']), LOG_BD_ERROR, 1)
        return False
    else:
        # perform actions
        if( len(used_filter['actions']) ): 
            performActions( os.path.join(used_filter['path'], os.path.basename(src_path)), used_filter['actions'], used_filter['name'])
        
        return True


import re
import string

# get priority by sum singol priority rules
# @src_path: char - file path target
# @rules: list - list of rules
# @return: int - global file priority
def getPriority (src_path, rules):
    
    needed_priority = -1000
    priority = 0
    file_name = os.path.basename(src_path)  # name.ext    
    file_size = os.path.getsize(src_path)   # in bytes

    file_ext = None     # file extension
    index_point = string.rfind(file_name, '.',-6,len(file_name))   # index of '.' in the last 5 character
    if ( index_point != -1 ): file_ext = file_name[index_point+1:len(file_name)]

    try:
        for rule in rules:
            
            if (rule['nome'] == "filename"):
                if (re.search( rule['text'], file_name, re.IGNORECASE )):
                    priority += int(rule['priority'])
                    setLog(3, "     |rule: \033[4mfilename\033[24m (\033[1m%s\033[22m in \033[1m%s\033[22m) [%s] %d => \033[1m%d\033[22m" % (rule['text'],file_name,rule['from'],priority-int(rule['priority']),priority), LOG_BD_INFO)

                elif (int(rule['needed'])): # if not match && needed=1 => priority - 1000
                    priority += needed_priority
                    setLog(3, "     |rule: \033[4mneeded\033[24m filename \033[1mdon't\033[22m respect (\033[1m%s\033[22m in \033[1m%s\033[22m) [%s] %d => \033[1m%d\033[22m" % (rule['text'],file_name,rule['from'],priority-int(rule['priority']),priority), LOG_BD_INFO)

            elif (rule['nome'] == "filesize_bigger"):
                target_size = memUnitConverter(rule['text'])
                if (file_size > target_size ): 
                    priority += int(rule['priority'])
                    setLog(3, "     |rule: \033[4mfilesize_bigger\033[24m (\033[1m%d > %d\033[22m) [%s] %d => \033[1m%d\033[22m" % (file_size,target_size,rule['from'],priority-int(rule['priority']),priority), LOG_BD_INFO)

            elif (rule['nome'] == "filesize_smaller"):
                target_size = memUnitConverter(rule['text'])
                if (file_size < target_size ):
                    priority += int(rule['priority'])
                    setLog(3, "     |rule: \033[4mfilesize_smaller\033[24m (\033[1m%d < %d\033[22m) [%s] %d => \033[1m%d\033[22m" % (file_size,target_size,rule['from'],priority-int(rule['priority']),priority), LOG_BD_INFO)

            elif (file_ext and rule['nome'] == "fileext"):
                finded = False
                rule_ext = rule['text'].split()
                for ext in rule_ext:
                    if (file_ext == ext):
                        priority += int(rule['priority'])
                        finded = True                        
                        setLog(3, "     |rule: \033[4mfileext\033[24m (\033[1m.%s\033[22m) [%s] %d => \033[1m%d\033[22m" % (file_ext,rule['from'],priority-int(rule['priority']),priority), LOG_BD_INFO)
                        break

                if (int(rule['needed']) and not finded ): # if not match && needed=1 => priority - 1000
                    priority += needed_priority
                    setLog(3, "     |rule: \033[4mneeded\033[24m fileext \033[1mdon't\033[22m respect (\033[1m.%s\033[22m) [%s] %d => \033[1m%d\033[22m" % (file_ext,rule['from'],priority-needed_priority,priority), LOG_BD_INFO)                

    except:
        setLog(0, "Ricontrolla le \033[1mrules\033[22m nella configurazione!", LOG_BD_ERROR, 1)
     
    return priority           


# perform actions listed in xml config
# @file_path: char - file path target
# @return: bool - true: all ok
def performActions (file_path, actions, filterName):

    file_renamed = False
    file_name = os.path.basename(file_path)  # name.ext 
    file_dir = os.path.dirname(file_path) # /home/user/
    linux_cmds = [] 

    try:  
        for action in actions:

            if (action['nome'] == "rename_prepend"):
                file_renamed = True
                file_name = action['text'] + file_name
               
            elif (action['nome'] == "rename_postpend"):
                file_renamed = True
                file_name = file_name + action['text']

            elif (action['nome'] == "exec_linux_cmd"):
                linux_cmds.append(action)
        
        global g_simulate        

        # real action perform
        if (file_renamed): 
            if (not g_simulated): 
                # shutil.move( file_path, os.path.join(file_dir , file_name) )
                os.system( 'mv "%s" "%s"' % (file_path, os.path.join(file_dir , file_name)) )
            setLog(2, " action: \033[4mrename\033[24m (\033[1m%s\033[22m) " % file_name, LOG_BD_INFO)

        # if there is some linux cmd, execute all    
        for linux_cmd in linux_cmds:
            
            cmd = linux_cmd['text']
            
            # substitute special characters
            cmd = cmd.replace( '%filename', file_name )    # file name
            cmd = cmd.replace( '%filedir', file_dir )   # full path
            cmd = cmd.replace( '%filepath', os.path.join(file_dir , file_name) )   # full path + file name
            cmd = cmd.replace( '%filtername', filterName )
            cmd = cmd.replace( '%actioninherit', linux_cmd['from'] )

            #execute command
            cmd_result = 0
            if (not g_simulated):
                #cmd_result = os.system( cmd )
                cmd_result = call( cmd, shell=True)
            setLog(2, " action: \033[4mexec_linux_cmd\033[24m (\033[1m%s\033[22m) [%s] returned \033[1m%d\033[22m" % (cmd, linux_cmd['from'], cmd_result), LOG_BD_INFO)

    except:
        setLog(0, "Problema durente l'esecuzione degli \033[1mactions\033[22m!", LOG_BD_ERROR, 1)
        return False
    else:
        return True


LOG_BD_INFO = 0
LOG_BD_ERROR = 1

# Log writer
# @verbose_level: int - set verbosity level too high => less important
# @text: char - log msg
# @msgType: int - LOG_BD_INFO, LOG_BD_ERROR
# @exit: int - 0 closing program without error, 1 with error, -1 don't close
def setLog (verbose_level, text, msgType = 0, exit = -1):

    msg_text = unicode(text)    # is it needed?
    prefix = current_time = ''
    global g_verbose, g_log_file, g_script

    if (msgType == LOG_BD_INFO and verbose_level <= g_verbose):
        prefix = "INFO.%02d:" % verbose_level

    elif (msgType == LOG_BD_ERROR):
        prefix = "ERROR:"

    else: return False

    # make log file 
    if ( g_log_file ):
        import time # get current time for log file
        current_time = time.strftime("%b %d %H:%M:%S")                                       

        file_log = open(g_log_file, 'a')                             

        # remove color tags in msg_text
        re_colorized_tag = re.compile( "\\033\[[0-9]{1,2}m" )
        msg_text = re_colorized_tag.sub( '', msg_text)
        
        file_log.write("%s %s %s\n" % (current_time, prefix, msg_text))
        file_log.close()

    # print on standard output or error and add some colors
    else:
        if (msgType == LOG_BD_INFO):
            # colorize
            verbose_color = [33,34,36,32]
            msg_text = "\033[%dm%s\033[39m" % (verbose_color[verbose_level-1],msg_text)

            sys.stdout.write("%s %s\n" % (prefix, msg_text))

        elif (msgType == LOG_BD_ERROR):
            sys.stderr.write("\033[31m%s %s\033[39m\n" % (prefix, msg_text))
    
    # exit if requested
    if(exit != -1): 
        setLog(0, "Terminazione anticipata di %s" % g_script, LOG_BD_ERROR)
        sys.exit(exit);

# Memory Unit Converter (in bytes)
# @to_convert: string - number to convert with postfix (b, K, M, G)
# @return: int - converted in bytes
def memUnitConverter (to_convert):

    # if find "b, k, m, g" at the end of sting 
    if (re.search( "[bkmg]$", to_convert, re.IGNORECASE )):
        postfix = to_convert[-1]
        to_byte = int(to_convert[0:-1])
        
        if (postfix == 'G' or postfix == 'g'):
            to_byte = to_byte*1024*1024*1024
        elif (postfix == 'M' or postfix == 'm'):
            to_byte = to_byte*1024*1024
        elif (postfix == 'K' or postfix == 'k'):
            to_byte = to_byte*1024
        
        return to_byte
        
    else: return int(to_convert)


from xml.dom import minidom        

# Get all info for a filter
# @filter_number: int - number of filter (base index: 0)
# @return: int - 1, dictionary - all filter infos
#          int - 0 no filter found, None 
#          int - -1 error in filter xml formatting, None
def getFilter (filter_number):

    global g_xml_config_file, g_xml_cfg

    # XML PARSING
    try:
        # open xml (only the first time)
        if(g_xml_cfg is None):
            g_xml_cfg = minidom.parse(g_xml_config_file)
        
        # check if correct config
        if(g_xml_cfg.firstChild.tagName != 'movme'):
            setLog(0,"\033[1m%s\033[22m non è un file di configurazione di movme!" % g_xml_config_file, LOG_BD_ERROR, 1)
    
        # get list of all nodes "filter"
        xml_filter = g_xml_cfg.firstChild.getElementsByTagName('filter')
    
        # filter number don't exist
        if(filter_number >= xml_filter.length):
            return 0, None
    
        # select filter
        xml_filter = xml_filter.item(filter_number)
    
        # variable infrastructure
        filter = {}
        rules = [] 
        actions = []
    
        # must be a filter "name" and " "path"
        if(not xml_filter.attributes.has_key('name') or not xml_filter.attributes.has_key('path')):
            setLog(0, "Il filtro \033[1m%d\033[22m non presenta gli attributi \033[1mname\033[22m o \033[1mpath\033[22m!" % filter_number, LOG_BD_ERROR)
            return -1, None
        else:
            filter['name'] = xml_filter.attributes['name'].value
            filter['path'] = xml_filter.attributes['path'].value
            if (xml_filter.attributes.has_key('mkdir')):          
                filter['mkdir'] = xml_filter.attributes['mkdir'].value
            else: filter['mkdir'] = 0    # default value
        
    #        # get list of all node in rules node
    #        xml_rules = xml_filter.getElementsByTagName('rules')[0].childNodes         
    #
    #        # read list of rules
    #        for rule in xml_rules:
    #            # only if is an ELEMENT_NODE
    #            if(rule.nodeType == 1):
    #                current_rule = {}
    #                # get rule attributes
    #                current_rule['nome'] = rule.nodeName
    #                if (rule.attributes.has_key('needed')):          
    #                    current_rule['needed'] = rule.getAttribute('needed')
    #                else: current_rule['needed'] = 0    # default value
    #                current_rule['priority'] = rule.getAttribute('priority')
    #                current_rule['text'] = rule.firstChild.nodeValue            
    #
    #                # read attrib of each rule and store in var structure
    #                rules.append(current_rule) 
    #        
    #        # add to var structure     
    #        filter['rules'] = rules
        
#        # get list of all node in actions node
#        xml_actions = xml_filter.getElementsByTagName('actions')[0].childNodes
#    
#        # read list of actions
#        for action in xml_actions:
#            # only if is an ELEMENT_NODE (1)
#            if(action.nodeType == 1):
#                # read attrib of each action and store in var structure
#                actions.append({'nome':action.nodeName,'text':action.firstChild.nodeValue}) 
    
        # get list of all node in rules node
        filter['rules'] = getParentTags (xml_filter, 'rules')

        # get list of all node in actions node     
        filter['actions'] = getParentTags (xml_filter, 'actions')
        
    except Exception, e:
        setLog(0, "Ricontrolliamo il file \033[1m%s\033[22m (%s)!" % (g_xml_config_file, e), LOG_BD_ERROR, 1)
    else:
        setLog(3, "Filtro \033[1m%s\033[22m (rules: \033[1m%u\033[22m, actions: \033[1m%u\033[22m) caricato da %s" % (filter['name'],len(filter['rules']),len(filter['actions']),g_xml_config_file), LOG_BD_INFO)
        
        # return succesfull and filter structure
        return 1, filter

# Get all tag_name inherit from <group> tag
# @target: nodeObj - xml tag filter where i start
# @tag_name: string - tag i must inherit (es. actions, rules)
# @return: list - all tag inherited
def getParentTags (target, tag_name):
    
    child_tag = []
    
    # Risalgo i tags (da figlio a padre) 
    while True:
        for children in target.childNodes:
            
            if (children.nodeType == children.ELEMENT_NODE and children.tagName == tag_name):
                for child in children.childNodes:
                    # ...iterate on all list of child nodes of tag_name (es. [filename, filesize_bigger, ...]) 
                    # read attrib of each xml_tag and store in var structure
                    if( child.nodeType == child.ELEMENT_NODE):
                        current = {}
                        
                        # get common tag_name attributes
                        current['nome'] = child.nodeName
                        current['text'] = child.firstChild.nodeValue
                        
                        # add info from inherit
                        if (target.tagName == 'group'): 
                            current['from'] = target.tagName    
                            if (target.attributes.has_key('name')): 
                                current['from'] += '.' + target.attributes['name'].value
                        else: current['from'] = 'self'
                        
                        # particulary attribs
                        if (tag_name == 'rules'):
                            # get tag_name attributes
                            if (child.attributes.has_key('needed')):          
                                current['needed'] = child.getAttribute('needed')
                            else: 
                                current['needed'] = 0    # default value
                            current['priority'] = child.getAttribute('priority')
                         
                        # actions don't have any particular attribs
                        #elif (tag_name == 'actions'):
                        
                        child_tag.append(current)
                        
        # go back in the xml tree            
        target = target.parentNode
                 
        # exit when arrive to tag <movme> or when father is not group (impossible)
        if (target.tagName == 'movme' or target.tagName != 'group'): break;

#    
#    print "-------------------after---------------------\n",mTarget.toxml()
#    # Get list of all child node of tag_name...
#    for xml_tags in target.getElementsByTagName(tag_name):
#        
#        # ...iterate on all tag_name nodes (es. [rules(1), rules(2), ...])
#        for xml_tag in xml_tags.childNodes:
#            
#            # ...iterate on all list of child nodes of tag_name (es. [filename, filesize_bigger, ...]) 
#            # only if is an ELEMENT_NODE
#            if (xml_tag.nodeType == 1):
#                if (tag_name == 'rules'):
#                    current = {}
#                    # get xml_tag attributes
#                    current['nome'] = xml_tag.nodeName
#                    if (xml_tag.attributes.has_key('needed')):          
#                        current['needed'] = xml_tag.getAttribute('needed')
#                    else: current['needed'] = 0    # default value
#                    current['priority'] = xml_tag.getAttribute('priority')
#                    current['text'] = xml_tag.firstChild.nodeValue            
#            
#                    # read attrib of each xml_tag and store in var structure
#                    child_tag.append(current)
#                elif (tag_name == 'actions'):
#                    # read attrib of each action and store in var structure
#                    child_tag.append({'nome':xml_tag.nodeName,'text':xml_tag.firstChild.nodeValue}) 
    
    return child_tag

if __name__ == "__main__":
    main(sys.argv[1:])
