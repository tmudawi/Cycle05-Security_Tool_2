#!/usr/bin/python

#################################################################################
# Tool Name       : LocateNewFiles_V2.py                        
#
# Author          : Tarig Mudawi        
#                   Dakota State University
#
# Tool Description: This tool gets its input as a directory folder, a time interval 
#                   in minutes and a P/S flag to either Print to screen or Save to 
#                   a file a list of all files that are created or modified within 
#                   the timeframe that the use specified.          
#                    This help when the user suspects that some suspisios files 
#                    are created by some sort of a hacker attack. 
# Features:         In this new version of the tool now do the following:
#                   1) Display all users that are logged into the system and the specific 
#                      time they logged in, the user can now compare the time of the 
#                      new/modified files to the logged time abnd try to figre out who 
#                      modified/created the files.
#                   2) Get the MD5 hash for each file and if a file changed later
#                      can determine the change in the MD5 hash. This tell the use
#                      that the contents of the file has been changed.
# Modifications:    The program now prompts the user to enter a path to save the 
#                   results instead of hardcoding them inside the code.
#                   It also validatation for directory and file extension.
##################################################################################   

import os

import datetime as dt

import sys

import win32com.client, time

strComputer = "."

objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")

objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")

colItems = objSWbemServices.ExecQuery("SELECT * FROM Win32_NetworkLoginProfile")

def CheckMD5():
    '''Get the md5 hash for the file.'''

    # A third party library to calculate the file md5 hash
    import md5checker


def GetLoggedInUsers():
    '''Returns all logged in users and the time they logged in'''

    print "\n"

    for objItem in colItems:
        if objItem.Name is not None:
            print("Logged in username: " + str(objItem.Name))

        if objItem.LastLogon is not None:
            #print("Last Logon (Normal Format): " + str(objItem.LastLogon))
            print("Last Logon: " + FormatTime(objItem.LastLogon))
            print "\n"


def FormatTime(dtmDate):
    '''This function format the time to human readable format'''

    LoggedInTime = ""

    if dtmDate[4] == 0:

        LoggedInTime = dtmDate[5] + '/'

    else:

        LoggedInTime = dtmDate[4] + dtmDate[5] + '/'

    if dtmDate[6] == 0:

        LoggedInTime = LoggedInTime + dtmDate[7] + '/'

    else:

        LoggedInTime = LoggedInTime + dtmDate[6] + dtmDate[7] + '/'
        LoggedInTime = LoggedInTime + dtmDate[0] + dtmDate[1] + \
        dtmDate[2] + dtmDate[3] + " " + dtmDate[8] + dtmDate[9] + \
        ":" + dtmDate[10] + dtmDate[11] +':' + dtmDate[12] + dtmDate[13]

    return LoggedInTime

def ListToFile(MyList, MyPath):
    '''Populate the file from the passed list of suspected files''' 

    #Open the file for writing
    with open(MyPath, 'w') as file_handler:

        for item in MyList:

            file_handler.write("{}\n".format(item))


def SearchNewFiles():
    '''Search for all files created or modified in a specific directory and within a timeframe that the user specifies'''

    # Getting the directory to scan from argv[1]
    try:
        DirToScan = sys.argv[1]
    except IndexError:
        print "\nUsage: LocateNewFiles_V2.py <argv1> <argv2> <argv3>\n"
        print "<argv1>: Path to directory to inspect its files."
        print "<argv2>: Time span in munutes."
        print "<argv3> Print results to screen (P) or Save them to a file (S)."
        sys.exit(1)

    # Validate the directory
    while 1:
        if(os.path.exists(DirToScan)):
            break
        else:
            DirToScan = raw_input("Please enter a valid directory!\n")

    # Getting the time interval from argv[2]
    try:
        time_interval = int(sys.argv[2])
    except IndexError:
        print "\nUsage: LocateNewFiles_V2.py <argv1> <argv2> <argv3>\n"
        print "<argv1>: Path to directory to inspect its files."
        print "<argv2>: Time span in munutes."
        print "<argv3> Print results to screen (P) or Save them to a file (S)."
        sys.exit(1)

    # Decide whether to print or save the results
    try:
        PrintOrSave = sys.argv[3]
    except IndexError:
        print "\nUsage: LocateNewFiles_V2.py <argv1> <argv2> <argv3>\n"
        print "<argv1>: Path to directory to inspect its files."
        print "<argv2>: Time span in munutes."
        print "<argv3> Print results to screen (P) or Save them to a file (S)."
        sys.exit(1)


    if(PrintOrSave == 'S'):
        
        # Validate file extension
        MyPath = raw_input("Enter a filename including path to save the results:\n")

        while 1:

            FileDir = os.path.dirname(MyPath)

            if not (os.path.exists(FileDir)):
                MyPath = raw_input("Enter a filename including path to save the results:\n")
            elif not(MyPath.endswith('.txt')):
                MyPath = raw_input("Enter a file with .txt extension:\n")

            else:
                break

        print ("\nFiles newly created or modified are saved at: " + MyPath)

    else:

        print "\n"

    # Create a list to hold files if the user want to
    FilesList = []

    # prepare time variable to do the scan
    now = dt.datetime.now()

    ago = now-dt.timedelta(minutes= int(time_interval))

     
    # Loop through all directories and files within the directory
    # specified by the user and display all the files created
    # or modified within that period. 
    try:
        for root,dirs,files in os.walk(unicode(DirToScan)):

            for fname in files:

                path = os.path.join(root, fname)

                st = os.stat(path)

                mtime = dt.datetime.fromtimestamp(st.st_mtime)

                if mtime > ago:

                    # user chooses to display information in the screen 
                    if PrintOrSave == 'P':

                        print('%s modified %s'%(path, mtime))

                    # user chooses to save information to a file 
                    elif PrintOrSave == 'S':

                        FilesList.append(path +"  "+ str(mtime))

                        ListToFile(FilesList, MyPath)

                    else:

                        print "No files created or modified within the last " + time_interval +" minutes!"
    except WindowsError:
        pass


def main():

    # Get a list of newly created or updated files.
    SearchNewFiles()

    # Get a list of logged in users
    GetLoggedInUsers()

    # Check if file md5 is changed
    CheckMD5()

if __name__ =="__main__":
    main()



