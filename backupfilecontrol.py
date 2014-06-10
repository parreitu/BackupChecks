#!/usr/bin/python

from os import path
from time import ctime
from datetime import datetime, timedelta
import os, os.path
import sys

from sendemail import send_email


# BackupFile class
class BackupFile:
    def __init__(self, path, maximum_days = 30, minimum_size_mb = 0):
        """   With this class we encapsulate different checks for backups files """
        if os.path.isfile(path):
            self.path = path
            self.minimum_age = datetime.now() - timedelta(days = maximum_days)
            self.minimum_size = minimum_size_mb * 1024 * 1024
	    self.size_in_mb = str(round(os.path.getsize(self.path)/float(1024)/float(1024),3)) + " MB"
            self.filetime = datetime.fromtimestamp(os.path.getmtime(self.path))
        else:
            raise Exception("The file path is incorrect")

    def __repr__(self):
        return "The file path is " + self.path + "FileTime " + str(self.filetime) + " Minimum age " + str(self.minimum_age)

    def out_of_date(self):
        "Here we check if the datetime stamp of the file is older than the maximum_days parameter"
        if self.filetime < self.minimum_age:
            return True
        else:
            return False             

    def incorrect_size(self):
        "Here we check if the size of the file is lower than the minimum_size in bytes"
        if os.path.getsize(self.path) < self.minimum_size:
            return True
        else:
            return False             

    
    def check_bzip(self):
        "Return True if the check is correct, False otherwise"

        try:
            result = os.system('bunzip2 -qt %s > /dev/null' % (self.path) )
            if result == 0:
                return True
            else:
                return False
        except:
            return False


class BackupFolder:
    def __init__(self, path, check_extensions, recursive_check = True):
        """   With this class we encapsulate different checks for backups files """
        if os.path.isdir(path):
            self.path = path
            self.check_extensions = check_extensions
            self.recursive_check = recursive_check
        else:
            raise Exception("The folder path is incorrect")

    def __repr__(self):
        return "The folder path is: " + self.path 

    def check_folder(self):
        " Here we check the files in the folder"

        # Populate a list with to many dictionaries as extensions to check. Each dictionary will save the
        # values of the variables needed to check 
        DEFAULT_MAXIMUM_DAYS = 10
        DEFAULT_MINIMUM_SIZE_MB = 5

        EMAIL_FROM = "myname@mydomain.com"
        EMAIL_TO = ["myname@mydomain.com", "othername@mydomain.com"]


        extensions_dict_list = []
        tmp_extension_list = []
        tmp_include_text_in_name_dict = {}
        for each_extension in self.check_extensions: # check_extensions is a list of dictionaries
            # each_extension is a dictionary
            new_dict = {}            
            new_dict['extension'] = each_extension['extension']

            if 'maximum_days' in each_extension.keys():
                new_dict['maximum_days'] = each_extension['maximum_days']
            else:
                new_dict['maximum_days'] = DEFAULT_MAXIMUM_DAYS

            if 'minimum_size_mb' in each_extension.keys():
                new_dict['minimum_size_mb'] = each_extension['minimum_size_mb']
            else:
                new_dict['minimum_size_mb'] = DEFAULT_MINIMUM_SIZE_MB

            if 'minimum_files_number' in each_extension.keys():
                new_dict['minimum_files_number'] = each_extension['minimum_files_number']
            else:
                new_dict['minimum_files_number'] = 1

            if 'include_text_in_name' in each_extension.keys():
                tmp_include_text_in_name_dict[each_extension['extension']] = each_extension['include_text_in_name'] 

            tmp_extension_list.append(each_extension['extension'])

            new_dict['files_count'] = 0
            new_dict['errors_count'] = 0
            new_dict['errors_msg'] = ""

            # In extensions_dict_list we have a list of dicts with information and variables
            # about the data to check               
            extensions_dict_list.append(new_dict)

        file_list =[]      
  
        # Now, we have to build a list with the files that meets the requirements. Depending of the value of
        # self.recursive, we have to check only the files into a folder, or all the files bellow the folder (recursively)
        if self.recursive_check:
            for root, dirs, files in os.walk(self.path):
                for f in files:
                    for extension in tmp_extension_list: # here we check each extension                        
                        if (os.path.splitext(f)[1] == extension): # this file meets the extension requirement
                            if not (extension in tmp_include_text_in_name_dict.keys()) or (f.find(tmp_include_text_in_name_dict[extension]) != -1 ):
                                # There isn't a include_text_in_name for this extension  OR the file meets the include_text_in_name requirement
                                # In both cases, we have to check this file
                                fullpath = os.path.join(root, f)
                                file_list.append(fullpath)
        else:
            dir = os.listdir(self.path)
            for f in dir:
                for extension in tmp_extension_list: # here we check each extension
                    if (os.path.splitext(f)[1] == extension): # this file meets the extension requirement
                        if not (extension in tmp_include_text_in_name_dict.keys()) or (f.find(tmp_include_text_in_name_dict[extension]) != -1 ):
                            # There isn't a include_text_in_name for this extension  OR the file meets the include_text_in_name requirement
                            # In both cases, we have to check this file
                            fullpath = os.path.join(self.path, f) 
                            file_list.append(fullpath)                          

        
        # Now, in "file_list" list, we have all the files that we have to check
        for fullpath in file_list:            
            # We have to check which extension is, because each extension can have diferent values 
            # to check
            for extension in tmp_extension_list:
                if (os.path.splitext(fullpath)[1] == extension):
                    # in extension_dict we will get the dictionary that have the variables for each extension.
                    for extension_dict in extensions_dict_list:
                        if extension_dict['extension'] == extension:
                            # in my_extension_dict we have the dictionary for the file's extension with all the needed variables
                            my_extension_dict = extension_dict
                    my_extension_dict['files_count'] += 1 # there is at least one file with this extension
                    # now we create a new instance of the BackupFile class with each file, using the values that we
                    # we have in the dictionary for each extension to check
                    thisfile = BackupFile(fullpath, extension_dict['maximum_days'], extension_dict['minimum_size_mb'])
                    if thisfile.out_of_date():
                        my_extension_dict['errors_count'] += 1
                        my_extension_dict['errors_msg'] += "File is more than " + str(maximum_days) + " days old. File: " + thisfile.path + " File time " + str(thisfile.filetime) + " minimum age "+ str(thisfile.minimum_age) + "\n\n"

                    if thisfile.incorrect_size():
                        my_extension_dict['errors_count'] += 1
                        my_extension_dict['errors_msg'] += "Check the file size, is lower than the minimum " + thisfile.path +" . File size: " + thisfile.size_in_mb  + "\n\n"

                    if extension == ".bz2": # Especifical check for bz2 files
                        if not thisfile.check_bzip():
                            my_extension_dict['errors_count'] += 1
                            my_extension_dict['errors_msg'] += "BZIP2 Error!! Check this file "  + thisfile.path
        
        # now, we've to check if we've find files for each extension. If not, we don't have backups for this extension   
        email_message = "PATH --> " + self.path + "\n\n"

        some_errors = False
        for each_extension_dict in extensions_dict_list:
            if each_extension_dict['files_count'] == 0:
                each_extension_dict['errors_count'] += 1
                each_extension_dict['errors_msg'] += "CAUTION !! There aren't " + "'" +each_extension_dict['extension' ] +"'" + " copies in the backup folder\n\n"

            if each_extension_dict['files_count'] <  each_extension_dict['minimum_files_number']:
                each_extension_dict['errors_count'] += 1
                each_extension_dict['errors_msg'] += "CAUTION !! There is/are only " + str(each_extension_dict['files_count']) + " file/s and there would be at least " + str(each_extension_dict['minimum_files_number'])  + " files in the backup folder\n\n"               

            if each_extension_dict['errors_count'] > 0:
                email_message += each_extension_dict['errors_msg'] 
                some_errors = True

        if some_errors:
            mail_subject = "Elkarbackup: Errors"
        else:
            mail_subject = "Elkarbackup: All OK"

        send_email (EMAIL_FROM, EMAIL_TO, mail_subject, email_message)   
        



# minimum_size = 50 
# maximum_days = 5 # If the file would have more than 5 days, it would be to old
# recursive = False 

# path = "/media/Backups/elkarbackup/0003/0012/Daily.0/home"
# myfolder = BackupFolder(path, [{'extension':".bak",'include_text_in_name':'MYDB','maximum_days':maximum_days, 'minimum_size_mb':minimum_size}], recursive)
# myfolder = BackupFolder(path, [{'extension':".bak",'maximum_days':maximum_days, 'minimum_size_mb':minimum_size}], recursive)
# myfolder = BackupFolder(path, [{'extension':".bz2", 'minimum_size':50, 'minimum_files_number':2 }], recursive)
# myfolder.check_folder()

# path: is the path of the folder that we want to check
# check_extensions: is a list of dictionaries, whereas each dictionary gives information about the validation to make for 
#                   files of one expecific extension. The keys of the dictionary may be:
#      - extension: the extension to check
#      - maximum_days: if one file is older than this value (in days), it would be considered as error. Default 10 days
#      - minimum_size_mb: if one file is smaller than this vale, it would be considered as error. Default 5MB
#      - minimum_files_number: There may exists at least this number of files for this extension. Otherwise, it would be considerer as error. Default 1 file
#      - include_text_in_name: By default not checked. You can use this if you want only check files that have some test in their name.
# recursive_check: if true, the check will be done recursively



