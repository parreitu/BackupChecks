BackupChecks
============

This python script can help you to check if your backups are OK. You can chech if you have recent backups, if they have a correct size, e.a.

Here you have some examples to know how to use. 

I will use this as post-scritp in Elkarbackup: https://github.com/elkarbackup/elkarbackup

minimum_size = 50 
maximum_days = 5 # If the file would have more than 5 days, it would be to old
recursive = False 

path = "/media/Backups/elkarbackup/0003/0012/Daily.0/home"
myfolder = BackupFolder(path, [{'extension':".bak",'include_text_in_name':'MYDB','maximum_days':maximum_days, 'minimum_size_mb':minimum_size}], recursive)
myfolder = BackupFolder(path, [{'extension':".bak",'maximum_days':maximum_days, 'minimum_size_mb':minimum_size}], recursive)
myfolder = BackupFolder(path, [{'extension':".bz2", 'minimum_size':50, 'minimum_files_number':2 }], recursive)

myfolder.check_folder()

path: is the path of the folder that we want to check
check_extensions: is a list of dictionaries, whereas each dictionary gives information about the validation to make for 
                 files of one expecific extension. The keys of the dictionary may be:
    - extension: the extension to check
    - maximum_days: if one file is older than this value (in days), it would be considered as error. Default 10 days
    - minimum_size_mb: if one file is smaller than this vale, it would be considered as error. Default 5MB
    - minimum_files_number: There may exists at least this number of files for this extension. Otherwise, it would be considerer as error. Default 1 file
    - include_text_in_name: By default not checked. You can use this if you want only check files that have some test in their name.
recursive_check: if true, the check will be done recursively
