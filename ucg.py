import sys
import os
import json
import platform

from pathlib import Path

from hurry.filesize import size

#from tkinter import *
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from shutil import copy2		## Copy with timestamp preservation

import colorama
from colorama import Fore, Back, Style
colorama.init()
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL

##
##
##

program = "UCG (UAE Configuration Generator)"
version = "v0.1 beta"

print(Style.BRIGHT)
print("=======================================================================")
print(program)
print(version)
print("=======================================================================")
print(Style.RESET_ALL)

print()
#print("os.name:",os.name)							# nt | linux | posix
print("platform.system():",platform.system())		# Windows | Linux | Darwin
print("platform.release():",platform.release())

print()
print("platform.python_version():",platform.python_version())
#print("platform.python_revision():",platform.python_revision())

##
## If on Windows - allow taskbar icon to be same as window icon
##

if platform.system() == 'Windows':

	import ctypes

	myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

##
##
##

print()

currentFile = __file__
realPath = os.path.realpath(currentFile)
cwd = os.path.dirname(realPath)
#cwd_parent = os.path.abspath(os.path.join(cwd, os.pardir))
cwd_parent = os.path.dirname(cwd)

print("realPath:",realPath)
print("CWD: ", cwd)
print("CWD Parent: ", cwd_parent)

if getattr( sys, 'frozen', False ) :
       print("Running as an executable")
else :
        print("Running as a script")

##
##
##

#
# User Config
#


#target_platform - which target_platform to generate for:
#target_platform = "android-puae";				# Android RetroArch P-UAE
#target_platform = "android-uae4arm";			# Android uae4arm
#target_platform = "snesc-puae";				# NES/SNES Classic/Mini RetroArch P-UAE
#target_platform = "snesc-uae4arm";			# NES/SNES Classic/Mini RetroArch uae4arm

target_platform = ''

# Default chipset:
chipset = "ocs";	
#chipset = "aga";

#
# Target platform configs
#

target_platform_config = {}


def load_target_platform_config():
	
	
	#
	# Load configs from file
	#
	
	conf_path = Path(cwd) / "conf/templates"

	for dirName, subdirList, fileList in os.walk(conf_path):
		
		#
		# Target Platforms
		#
			
		for platform_dir in subdirList:
			#print("Platform:", platform_dir)
			target_platform_config[platform_dir] = {}
			
			#
			# Target Platform configs
			#
			
			target_platform_config[platform_dir]['config'] = {}
			
			for config_dirName, config_subdirList, config_fileList in os.walk(conf_path / platform_dir):
			
				for platform_config_file in config_fileList:
					#print("platform_config_file:", platform_config_file)
					if platform_config_file == 'template.json':
						#print("template json:", platform_config_file)
						with open(conf_path / platform_dir / platform_config_file) as platform_config_json_file:
							platform_config_json_data = json.load(platform_config_json_file)
							target_platform_config[platform_dir]['config'] = platform_config_json_data
			
			#
			# Target Platform UAE config templates
			# 
		
			##
			target_platform_config[platform_dir]['uae'] = {}
				
			for platform_dirName, platform_subdirList, platform_fileList in os.walk(conf_path / platform_dir / "uae"):
			
				# Chipset (ocs/aga)
				for chipset_dir in platform_subdirList:
					#print("Chipset:", chipset_dir)
					target_platform_config[platform_dir]['uae'][chipset_dir] = {}
				
					# Type (adf/hdf)
					for type_dirName, type_subdirList, type_fileList in os.walk(conf_path / platform_dir / "uae" / chipset_dir):
						for type_dir in type_subdirList:
							#print("Type:", type_dirName)
							target_platform_config[platform_dir]['uae'][chipset_dir][type_dir] = {}
							
							# Template file - template.uae
							for template_dirName, template_subdirList, template_fileList in os.walk(conf_path / platform_dir / "uae" / chipset_dir / type_dir):
								for uae_file in template_fileList:
									if(uae_file == "template.uae"):
										#print("uae_file", uae_file)
										
										with open(conf_path / platform_dir / "uae" / chipset_dir / type_dir / uae_file) as template_uae_file:
											template_uae_file_lines = template_uae_file.read().splitlines()
											
											for line in template_uae_file_lines:
											
												if "#" in line:		# Comment line
													#print("Comment:", line)
													pass
												else:
													if(line):	# if not empty line
														#print("Config:", line)
														line_split = line.split('=')
														#print("line_split:", line_split)
														target_platform_config[platform_dir]['uae'][chipset_dir][type_dir][line_split[0]] = line_split[1]
								#print()
								break
						#print()
						break
				#print()
				break
		#print()
		break
	
	#print()
	#print("JSON dump - target_platform_config:")
	#print(json.dumps(target_platform_config, indent=4))
	
load_target_platform_config()

'''
print()
print("roms_config:",roms_config)
print()
'''


###
	
#target_platform_directory_separator = target_platform_config[target_platform]['config']['directory_separator']	## The path separator of the TARGET platform

###

#
#
#

# UCG configs

ucg_conf = {}

def load_ucg_conf():
	
	global ucg_conf
	
	ucg_conf_path = Path(cwd) / "conf/config.json"
	
	print()
	print("UCG Configs:")
	print("ucg_conf_path:", ucg_conf_path)
	
	with open(ucg_conf_path) as ucg_conf_json_file:
		ucg_conf_json_data = json.load(ucg_conf_json_file)
		ucg_conf = ucg_conf_json_data

##
##
##

load_ucg_conf()

##
##
##

##
## =====================================================================================================
##

##
##
##

games = {}				# Blank games dictionary (array)
duplicates_count = 0
filename_issues = {}
issues_count = 0;

##
##
##

def generate_games_dictionary():

	##
	## Generate games directory
	##
	
	global duplicates_count
	global issues_count
	
	## Scan dir
	if(ucg_conf['debug']['print_dir_scan']):

		print()
		print("amiga_games_relative_path: ", target_platform_config[target_platform]['config']['amiga_games_relative_path'])

	for dirName, subdirList, fileList in os.walk(ucg_conf['config']['target_games_path']):
	
		## Check for disallowed characters - in directory name
		
		matched_disallowed_characters = {}
		
		for character in ucg_conf['config']['disallowed_characters']:
			pos = dirName.find(character)
			if(pos > 0):
				matched_disallowed_characters[character] = pos
			
		if(matched_disallowed_characters):
			filename_issues[issues_count] = {
				"Dir": str(Path(cwd_parent) / dirName)
				}
			issues_count += 1
		
		##
		
		if(ucg_conf['debug']['print_dir_scan']):
		
			print("[DIR] " + dirName)
		
		for fname in fileList:
			
			filename, file_extension = os.path.splitext(fname)
			
			## Check for disallowed characters - in file name
			
			matched_disallowed_characters = {}
			
			for character in ucg_conf['config']['disallowed_characters']:
				pos = fname.find(character)
				if(pos > 0):
					matched_disallowed_characters[character] = pos
				
			if(matched_disallowed_characters):
				filename_issues[issues_count] = {
					"File": str(Path(cwd_parent) / dirName / fname)
					}
				issues_count += 1
			
			##
			
			if (file_extension == '.zip') or (file_extension == '.adf'):
			
				game_disk = filename.split('__')
				
				#print("JSON dump - game_disk:")
				#print(json.dumps(game_disk, indent=4))
				
				if(len(game_disk) > 1):	## Multi-disk game
				
					game_name = game_disk[0]
					disk_name = game_disk[1]
					
					disk_name_array = disk_name.split('Disk')
					
					#print("JSON dump - disk_name_array:")
					#print(json.dumps(disk_name_array, indent=4))
					
					disk_id = disk_name_array[1]
			
					if(ucg_conf['debug']['print_dir_scan']):
						print('  +---[GAME] ',Fore.GREEN,game_name,Style.RESET_ALL,' (',file_extension,')',sep='')
						print("         +---[",disk_id,"] ",fname,sep='')
					
					if game_name in games.keys(): ## multi-disk game already added
						
						if(dirName == games[game_name]['Dir']):	## File in same dir as matched game - i.e. another game disk
						
							#print("disk_id:",disk_id)
							#print("game_name:",game_name)
							
							## Add the disk
							games[game_name]['Disks'][disk_id] = fname
							
						else:	## In a differrent dir - i.e. a duplicate
							
							if(ucg_conf['debug']['print_dir_scan']):
								print(Fore.RED + "### Duplicate Found ###" + Style.RESET_ALL)
							
							duplicates = {
								duplicates_count: {
									'Dir':	dirName,
									'File':	fname
								}
							}
							
							if "Duplicates" in games[game_name]:
								games[game_name]['Duplicates'].update(duplicates)
							else:
								games[game_name]['Duplicates'] = duplicates
							
							duplicates_count += 1
							
					
					else:	## multi-disk game does not exist in array - i.e first disk
		
						## Creat disks array
						disk_array = {
								disk_id: fname
						}
					
						## Create game array
						game_array = {
							#game_name: {
								'Game': game_name,
								'Dir': dirName,
								'Type': file_extension,
								'Disks': disk_array
							#}
						}
							
						## Add to games array
						#games.update(game_array)
						games[game_name] = game_array
				
				else: ## single-disk game
				
					if(ucg_conf['debug']['print_dir_scan']):
						print('  +---[GAME] ',Fore.GREEN, filename, Style.RESET_ALL,' (',file_extension,')',sep='')
						print("         +---['1'] ",fname,sep='')
						
					if filename in games.keys(): # single-disk game already added - i.e. duplicate
						
						if(ucg_conf['debug']['print_dir_scan']):
							print(Fore.RED + "### Duplicate Found ###" + Style.RESET_ALL)
							
						duplicates = {
							duplicates_count: {
								'Dir':	dirName,
								'File':	fname
							}
						}
						
						if "Duplicates" in games[filename]:
							games[filename]['Duplicates'].update(duplicates)
						else:
							games[filename]['Duplicates'] = duplicates
						
						duplicates_count += 1
						
					else:	# single-disk game not added - i.e. not duplicate
					
						## Create game array
						game_array = {
							'Game': filename,
							'Dir': dirName,
							'Type': file_extension,
							'Disks': {
								'1': fname
							}
						}
					
						## Add to games array
						games[filename] = game_array
				
				if(ucg_conf['debug']['print_dir_scan']):
					print()
				
			if (file_extension == '.hdf'):
				
				if(ucg_conf['debug']['print_dir_scan']):
					print("  +---[GAME] ",Fore.GREEN,filename,Style.RESET_ALL," (",file_extension,")",sep='')
					print("         +---[Disk1]",fname)
				
				if(filename in games.keys()):	## If already exist - i.e. duplicate
					
					if(ucg_conf['debug']['print_dir_scan']):
						print(Fore.RED + "### Duplicate Found ###" + Style.RESET_ALL)
							
					duplicates = {
						duplicates_count: {
							'Dir':	dirName,
							'File':	fname
						}
					}
					
					if "Duplicates" in games[filename]:
						games[filename]['Duplicates'].update(duplicates)
					else:
						games[filename]['Duplicates'] = duplicates
					
					duplicates_count += 1
				
				else:	## Does not exist - i.e. not duplicate
				
					## Creat disks array
					disk_array = {
							'1': fname
					}
					
					## Create game array
					game_array = {
						filename: {
							'Game': filename,
							'Dir': dirName,
							'Type': file_extension,
							'Disks': disk_array
							}
					}
					
					# Add to games array
					games.update(game_array)
		
		if(ucg_conf['debug']['print_dir_scan']):
			print()

def sort_games_disks_order():

	##
	## Sort the disk order for each game
	##
	
	for game_name,game in games.items():
	
		# Only for .adf or .zip games
		if((game['Type'] == '.zip') or (game['Type'] == '.adf')):
		
			# Only if more than one disk
			if(len(game['Disks'].items()) > 1):
			
				# Get disks keys as a list
				disks_keys = list(game['Disks'].keys())
				
				#print()
				#print("JSON dump - disks_keys:")
				#print(json.dumps(disks_keys, indent=4))
				
				
				if disks_keys[0].isalpha():
					sorted_disk_keys = sorted(disks_keys)			# sort keys alphanumerically
					#print("isalpha")
				if disks_keys[0].isdigit():
					sorted_disk_keys = sorted(disks_keys, key=int)	# sort keys numerically
					#print("isdigit")
					
				#print()
				#print("JSON dump - sorted_disk_keys:")
				#print(json.dumps(sorted_disk_keys, indent=4))
				
				# Create new disks dict
				sorted_disk_dict = {}
				
				disk_count = 0
				for disk_id in sorted_disk_keys:
					sorted_disk_dict[disk_count] = game['Disks'][disk_id]
					disk_count += 1
					
				#print()
				#print("JSON dump - sorted_disk_dict:")
				#print(json.dumps(sorted_disk_dict, indent=4))
				
				# Update with the newly sorted disks dict
				game['Disks'] = sorted_disk_dict

def sort_games_dict():
	
	global games
	
	temp_games_dict = {}
	
	for key in sorted(games.keys()):
		temp_games_dict[key] = games[key]
		#print("Game: ", key)
	
	games = temp_games_dict
	
def detect_games_chipset():

	for game_name, game in games.items():
		if("AGA" in game['Game']):
			game_chipset = 'aga'
		else:
			game_chipset = 'ocs'
			
		games[game_name]['Chipset'] = game_chipset

def detect_games_issues():

	global issues_count
	
	##
	## Check for disallowed characters
	##
	
	for game_name, game in games.items():
		matched_disallowed_characters = {}
		
		#print("matched_disallowed_characters: ", ucg_conf['config']['disallowed_characters'])
		
		for character in ucg_conf['config']['disallowed_characters']:
			#print("character:{", character,"}", sep='')
			pos = game['Game'].find(character)
			#print("pos:", pos)
			if(pos > 0):
				matched_disallowed_characters[character] = pos
		
		if(matched_disallowed_characters):
			filename_issues[issues_count] = {
				"Game": game['Game']
				}
			issues_count += 1
		
def show_issues_and_duplicates():

	#
	# Show filename issues
	#

	print()
	print(Fore.RED + Style.BRIGHT, end='')
	print("#")
	print("# Filename issues - disallowed characters!:")
	print("#")
	print(Style.RESET_ALL,end='')
	print()

	print("Disallowed Characters: ", ucg_conf['config']['disallowed_characters'])
	print()
	
	status_message = "Disallowed Characters:\n"
	status_message += str(ucg_conf['config']['disallowed_characters']) + "\n"
	global_widget_list['text_target_platform'].insert('end', status_message)

	status_message = "\nName issues:\n"
	global_widget_list['text_target_platform'].insert('end', status_message)
	
	for filename_id, filename in filename_issues.items():
		print(Fore.RED + Style.BRIGHT, end='')
		print(filename)
		print(Style.RESET_ALL,end='')
		
		status_message = str(filename) + "\n"
		global_widget_list['text_target_platform'].insert('end', status_message)
	#
	# Show duplicates
	#

	if(duplicates_count):
		
		print()
		print(Fore.RED + Style.BRIGHT, end='')
		print("#")
		print("# Duplicates Found!:")
		print("#")
		print()
		
		print(Style.RESET_ALL,end='')
		
		status_message = "\nDuplicates:\n"
		global_widget_list['text_target_platform'].insert('end', status_message)
		
		for game_name,game in games.items():
			if 'Duplicates' in game.keys():
				
				print("[GAME] " + Fore.GREEN + game['Game'] + Style.RESET_ALL)
				print("[DIR] " + game['Dir'])
				print("[DUPLICATES]")
				
				status_message = "\n[GAME] " + game['Game'] + "\n"
				status_message += "[DIR] " + game['Dir'] +  "\n"
				status_message += "[DUPLICATES]\n"
				global_widget_list['text_target_platform'].insert('end', status_message)
				
				for duplicate_id, duplicate in game['Duplicates'].items():

					print("     +---[DIR] " + duplicate['Dir'])
					print("           +---[FILE] " + Fore.RED + Style.BRIGHT + duplicate['File'] + Style.RESET_ALL)
				
					status_message = "     +---[DIR] " + game['Dir'] + "\n"
					status_message += "           +---[FILE] " + duplicate['File'] + "\n"
					global_widget_list['text_target_platform'].insert('end', status_message)
					
				print()
				
				status_message = "\n"
				global_widget_list['text_target_platform'].insert('end', status_message)
				
				

##
##
##

global_widget_list = {}

##
## Create main window
##

window = tk.Tk()
window.title(program + " " + version)

img = tk.PhotoImage("photo", file= Path(cwd) / "img/ucg-logo.png")
window.tk.call('wm','iconphoto',window._w, img)

##
## Menu
##

def menu_restart():
	print("Restarting...")
	os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
	
def menu_exit():
	print("Good bye!")
	sys.exit()
	
# create a toplevel menu
menubar = tk.Menu(window)

filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Restart", command=menu_restart)
filemenu.add_command(label="Exit", command=menu_exit)
menubar.add_cascade(label="Menu", menu=filemenu)

# display the menu
window.config(menu=menubar)

##
##
##

def update_progressbar(value):
	progressbar_start["value"]=value
	progressbar_start.update()
	
def start():
	
	global target_platform
	global games
	
	print()
	print("## ------------------------------------")
	print("## Start!                           ###")
	print("## ------------------------------------")
	print()
	
	update_progressbar(0)
	global_widget_list['text_target_platform'].delete('1.0', 'end')
	
	status_message = "\nStarting...\n"
	global_widget_list['text_target_platform'].insert('end', status_message)
	
	#
	# Clear tabs
	#
	
	#print("global_widget_list:",global_widget_list)
	
	if "tab_game_files" in global_widget_list.keys():
		global_widget_list['tab_control'].forget(global_widget_list['tab_game_files'])
		del global_widget_list['tab_game_files']
	
	if "tab_games_list" in global_widget_list.keys():
		global_widget_list['tab_control'].forget(global_widget_list['tab_games_list'])
		del global_widget_list['tab_games_list']
	
	if "tab_uae_configs" in global_widget_list.keys():
		global_widget_list['tab_control'].forget(global_widget_list['tab_uae_configs'])
		del global_widget_list['tab_uae_configs']
	
	if "tab_snesc" in global_widget_list.keys():
		global_widget_list['tab_control'].forget(global_widget_list['tab_snesc'])
		del global_widget_list['tab_snesc']
	
	status_message = "\nClearing tabs...\n"
	global_widget_list['text_target_platform'].insert('end', status_message)
	update_progressbar(5)
	
	#target_platform = variable_target_platform.get()
	target_platform = entry_target_platform.get()
	print("Games Dir: ", entry_games_path.get())
	
	load_target_platform_config()
	load_ucg_conf()
	#set_base_configs()
	
	ucg_conf['config']['target_games_path'] = entry_games_path.get()
	ucg_conf['config']['target_uae_path'] = entry_uae_path.get()
	
	print("target_platform: ", target_platform)
	print("amiga_uae_relative_path: ", target_platform_config[target_platform]['config']['amiga_uae_relative_path'])
	print("target_games_path: ", ucg_conf['config']['target_games_path'])
	print("target_uae_path: ", ucg_conf['config']['target_uae_path'])
	
	print()
	
	print()
	print("Generating Games Dictionary...")
	print()
	
	status_message = "\nGenerating Games Dictionary...\n"
	global_widget_list['text_target_platform'].insert('end', status_message)
		
	
	update_progressbar(10)
	
	games = {}
	generate_games_dictionary()
	
	
	print()
	print("Sorting Games Disks...")
	print()
	
	status_message = "\nSorting Games Disks...\n"
	global_widget_list['text_target_platform'].insert('end', status_message)
	
	update_progressbar(15)
	sort_games_disks_order()
	
	
	print()
	print("Detecting Games Chipset...")
	print()
	
	status_message = "\nDetecting Games Chipset...\n"
	global_widget_list['text_target_platform'].insert('end', status_message)
	
	update_progressbar(20)
	detect_games_chipset()
	
	print()
	print("Detecting Games Issues...")
	print()
	
	status_message = "\nDetecting Games Issues...\n"
	global_widget_list['text_target_platform'].insert('end', status_message)
	
	update_progressbar(25)
	detect_games_issues()
	
	print()
	print("Sorting Games Order...")
	print()
	
	status_message = "\nSorting Games Order...\n"
	global_widget_list['text_target_platform'].insert('end', status_message)
	
	update_progressbar(30)
	sort_games_dict()
	
	print()
	print("Creating Game Files Tab...")
	print()
	
	status_message = "\nCreating Game Files Tab...\n"
	global_widget_list['text_target_platform'].insert('end', status_message)
	
	update_progressbar(35)
	create_game_files_tab()
	
	print()
	print("Creating Game List Tab...")
	print()
	
	status_message = "\nCreating Game List Tab...\n"
	global_widget_list['text_target_platform'].insert('end', status_message)
	
	update_progressbar(40)
	create_games_list_tab()
	
	print()
	print("Generating UAE Configs...")
	print()
	
	status_message = "\nGenerating UAE Configs...\n"
	global_widget_list['text_target_platform'].insert('end', status_message)
	
	update_progressbar(50)
	create_uae_configs_tab()

	
	if 'snesc_linked_export_games_relative_path' in target_platform_config[target_platform]['config'].keys():
		print()
		print("Creating SNES Classic Tab...")
		print()
		
		status_message = "\nCreating SNES Classic Tab...\n"
		global_widget_list['text_target_platform'].insert('end', status_message)
	
		update_progressbar(70)
		create_snesc_tab()
	
	#else:
	#	global_widget_list['tab_control'].forget(global_widget_list['tab_snesc'])
	
	print()
	print("Issues and duplicates...")
	print()
	
	status_message = "\nIssues and duplicates...\n"
	global_widget_list['text_target_platform'].insert('end', status_message)
	
	update_progressbar(90)
	show_issues_and_duplicates()
	
	##
	## Done!
	##
	
	status_message = "\nDone!\n"
	global_widget_list['text_target_platform'].insert('end', status_message)
	
	update_progressbar(100)
	
	#
	# Switch focus to Game Files tab
	#
	
	#global_widget_list['tab_control'].select(global_widget_list['tab_game_files'])

def create_game_files_tab():

	##
	## Tab: Game Files - tab_game_files
	##
	
	tab_game_files = ttk.Frame(tab_control, name='tab_game_files')
	
	# Add to global widget list
	global_widget_list.update({'tab_game_files': tab_game_files})

	
	tab_control.add(tab_game_files, text='Game Files', image=images['disk_multiple']['image'], compound='left')
	
	## Tree
	tree_game_files = ttk.Treeview(tab_game_files, columns=("type","size"))
	tree_game_files.heading("#0", text="File")
	tree_game_files.heading("type", text="Type")
	tree_game_files.heading("size", text="Size") 

	## Scrollbar
	scrollbar_tree_game_files = ttk.Scrollbar(tree_game_files, command=tree_game_files.yview)
	scrollbar_tree_game_files.pack(side='right', fill='y')
	tree_game_files.configure(yscrollcommand=scrollbar_tree_game_files.set)
	
	##
	
	tree_game_files.delete(*tree_game_files.get_children())

	for dirName, subdirList, fileList in os.walk(ucg_conf['config']['target_games_path']):
		
		if(dirName == ucg_conf['config']['target_games_path']):
			statinfo = os.stat(dirName)
			tree_game_files.insert('', 'end', dirName, text=dirName, values=('[DIR]',''), tags = ('directory',))
		else:
			statinfo = os.stat(dirName)
			tree_game_files.insert(Path(dirName).parent, 'end', dirName, text=dirName, values=('[DIR]',''), tags = ('directory',))

		for fname in fileList:
			
			# fname_tag
			fname_tag = ''
			for issue_key, issue_value in filename_issues.items():
				if str(Path(dirName) / fname) in issue_value.values():
					fname_tag = 'issue'
			
			statinfo = os.stat(Path(dirName) / fname)
			
			filename, file_extension = os.path.splitext(fname)
			
			if(file_extension == ".adf"):
				tree_game_files.insert(dirName, 'end', Path(dirName) / fname, text= fname, values=(file_extension,size(statinfo.st_size)),tags = ('.adf',fname_tag,))
			if(file_extension == ".zip"):
				tree_game_files.insert(dirName, 'end', Path(dirName) / fname, text= fname, values=(file_extension,size(statinfo.st_size)),tags = ('.zip',fname_tag,))
			if(file_extension == ".hdf"):
				tree_game_files.insert(dirName, 'end', Path(dirName) / fname, text= fname, values=(file_extension,size(statinfo.st_size)),tags = ('.hdf',fname_tag,))

	tree_game_files.tag_configure('issue', background='#ffdddd')
	tree_game_files.tag_configure('directory', background='#E8E8E8', image=images['dir']['image'])
	tree_game_files.tag_configure('.adf', image=images['.adf']['image'])
	tree_game_files.tag_configure('.zip', image=images['.zip']['image'])
	tree_game_files.tag_configure('.hdf', image=images['.hdf']['image'])

	tree_game_files.pack(expand='yes', fill='both')

def create_games_list_tab():
	
	##
	## Tab: Games List - tab_games_list
	##
	
	tab_games_list = ttk.Frame(tab_control, name='tab_games_list')
	
	# Add to global widget list
	global_widget_list.update({'tab_games_list': tab_games_list})
	
	tab_control.add(tab_games_list, text='Game List', image=images['joystick']['image'], compound='left')

	## Tree
	tree_game_list = ttk.Treeview(tab_games_list,columns=("type","chipset"))
	tree_game_list.heading("#0", text="Game")
	tree_game_list.heading("type", text="Type")
	tree_game_list.heading("chipset", text="Chipset")

	## Scrollbar
	scrollbar_tree_game_list = ttk.Scrollbar(tab_games_list, command=tree_game_list.yview)
	scrollbar_tree_game_list.pack(side='right', fill='y')
	tree_game_list.configure(yscrollcommand=scrollbar_tree_game_list.set)
	
	#tree_game_list.insert('', 'end', 'Games', text='Games')

	tree_game_list.delete(*tree_game_list.get_children())
	
	for game_name,game in games.items():
		
		# fname_tag
		issues_tag = ''
		for issue_key, issue_value in filename_issues.items():
			#print("issue_key:", issue_key)
			#print("issue_value:", issue_value)
			if game_name in issue_value.values():
				issues_tag = 'issue'
		'''
		print()
		print("issues_tag:",issues_tag)
		print()		
		'''
		
		game_tag = ''

		if((game['Type'] == '.adf')):
			if(len(game['Disks']) == 1):
				game_tag = "disk"
			if(len(game['Disks']) > 1):
				game_tag = "disk_multiple"
		if((game['Type'] == '.zip')):
			if(len(game['Disks']) == 1):
				game_tag = "compress"
			if(len(game['Disks']) > 1):
				game_tag = "compress_multiple"
		if(game['Type'] == '.hdf'):
			game_tag = ".hdf"
						
		#tree_game_list.insert('', 'end', game_name, text=game_name, values=(game['Type'], game['Chipset']), tags = (game_tag,issues_tag,))
		tree_game_list.insert('', 'end', game_name, text=game_name, values=(game['Type'], game['Chipset']), tags = (game_tag,issues_tag,))
		
		for disk_id, disk in game['Disks'].items():
		
			disk_tag =''
			
			#tree_game_list.insert(game_name, 'end', disk, text=disk, tags=(disk_tag,))
			tree_game_list.insert(game_name, 'end', disk, text=disk, tags=(game['Type'],))
		
	tree_game_list.tag_configure('issue', background='#ffdddd')
	tree_game_list.tag_configure('.adf', image=images['.adf']['image'])
	tree_game_list.tag_configure('disk', image=images['disk']['image'])
	tree_game_list.tag_configure('disk_multiple', image=images['disk_multiple']['image'])
	tree_game_list.tag_configure('.zip', image=images['.zip']['image'])
	tree_game_list.tag_configure('compress', image=images['compress']['image'])
	tree_game_list.tag_configure('compress_multiple', image=images['compress_multiple']['image'])
	tree_game_list.tag_configure('.hdf', image=images['.hdf']['image'])
	tree_game_list.tag_configure('drive_disk', image=images['drive_disk']['image'])
	tree_game_list.tag_configure('drive_compress', image=images['drive_compress']['image'])
	tree_game_list.tag_configure('drive', image=images['drive']['image'])

	tree_game_list.pack(expand='yes', fill='both')

def on_uae_config_tree_select(event):

	item_name = event.widget.focus()		## Name of item
	
	if item_name in games.keys():
		global_widget_list['text_uae_config'].delete('1.0', 'end')
		global_widget_list['text_uae_config'].insert('end', games[item_name]['UAE'])

def create_uae_configs_tab():
	
	global games
	global issues_count
	
	target_platform_directory_separator = target_platform_config[target_platform]['config']['directory_separator']	## The path separator of the TARGET platform
	
	##	
	## Create UAE directory
	##
	
	print()
	print("ucg_conf['config']['target_uae_path']:", ucg_conf['config']['target_uae_path'])
	print()
	
	if not os.path.exists(ucg_conf['config']['target_uae_path']):
		os.makedirs(ucg_conf['config']['target_uae_path'])
	
	##
	## Generate UAE configs
	##
	
	for game_name,game in games.items():

		disk_file_count = len(game['Disks'])
		
		if("AGA" in game['Game']):
			chipset = 'aga'
		else:
			chipset = 'ocs'
		
		if((game['Type'] == '.adf') or (game['Type'] == '.zip')):
			game_type = 'adf'
			
		if(game['Type'] == '.hdf'):
			game_type = 'hdf'
		
		##
		##
		##
		
		print ("[GAME] ",Fore.GREEN, game['Game'], Style.RESET_ALL," (", game_type, ") (", chipset, ")",sep='')
		
		'''
		if(matched_disallowed_characters):
			print(Fore.RED + " ### DISALLOWED CHARACTERS ###" + Style.RESET_ALL)
		'''
		
		print ("[DIR] ", game['Dir'], sep='')
		
		print ("[DISKS {",disk_file_count,"}]", sep='')
		for disk_name, disk_value in game['Disks'].items():
			print ("     +-----[", disk_name, "] ", Fore.MAGENTA, disk_value, Style.RESET_ALL, sep='', end='')
		
			#file_path = str(Path(cwd) / game['Dir'] / disk_value)
			file_path = str(Path(game['Dir']) / disk_value)
			
			'''
			print()
			print("game['Dir']: " , game['Dir'])
			print("file_path: " , file_path)
			print()
			'''
			
			if( file_path in filename_issues.values()):
				print(Fore.RED + Style.BRIGHT + " ### DISALLOWED CHARACTERS ###" + Style.RESET_ALL)
			else:
				print()
			
		# Build UAE Config
		uae_file_contents = ""
		print()
		print("[UAE Config]")
		print()
		
		uae_file_contents += "### Generated by UCD (UAE Config Generator) ###\n"
		uae_file_contents += "#target_platform=" + target_platform + "\n"
		uae_file_contents += "#Game=" + game['Game'] + "\n"
		uae_file_contents += "#Type=" + game['Type'] + "\n"
		uae_file_contents += "#Chipset=" + chipset + "\n"
		uae_file_contents += "\n"
		
		for uae_config_key, uae_config_value in target_platform_config[target_platform]['uae'][chipset][game_type].items():
			uae_file_contents += uae_config_key + "=" + uae_config_value + "\n"
		
		## kickstart
		uae_file_contents += "kickstart_rom_file=" + target_platform_config[target_platform]['config']['amiga_games_kickstart_path'] + target_platform_directory_separator + target_platform_config[target_platform]['config']['amiga_games_kickstart_rom'] + "\n"
		
		## rom.key (if set)
		if ('amiga_games_kickstart_rom_key' in target_platform_config[target_platform]['config']):
			if (target_platform_config[target_platform]['config']['amiga_games_kickstart_rom_key'] != ""):
				uae_file_contents += "kickstart_rom_key=" + target_platform_config[target_platform]['config']['amiga_games_kickstart_path'] + target_platform_directory_separator + target_platform_config[target_platform]['config']['amiga_games_kickstart_rom_key'] + "\n"
		
		
		## floppies
		if((game['Type'] == '.adf') or (game['Type'] == '.zip')):
			floppy_id = 0
			for disk, disk_file in game['Disks'].items():
			
				game_dir = game['Dir']
				game_dir_ralative_path = game_dir.replace(ucg_conf['config']['target_games_path'], '')
				game_dir_ralative_path = game_dir_ralative_path.replace("\\", target_platform_directory_separator)
				game_dir_ralative_path = game_dir_ralative_path.replace("/", target_platform_directory_separator)
				final_path = target_platform_config[target_platform]['config']['parent_path'] + target_platform_directory_separator + str(target_platform_config[target_platform]['config']['amiga_games_relative_path']) + game_dir_ralative_path + target_platform_directory_separator + disk_file
				final_path = final_path.replace("\\", target_platform_directory_separator)
				final_path = final_path.replace("/", target_platform_directory_separator)
			
				if(floppy_id < ucg_conf['config']['max_nr_floppies']):
					uae_file_contents += "floppy" + str(floppy_id) + "type=0" + "\n"
					uae_file_contents += "floppy" + str(floppy_id) + "=" + final_path + "\n"
					floppy_id += 1
		
		## harddrive
		if(game['Type'] == '.hdf'):

			## WHDLoad.hdf
			uae_file_contents += "hardfile=" + ucg_conf['config']['base_hardfile_access'] + "," + target_platform_config[target_platform]['config']['amiga_whdload_path'] + target_platform_directory_separator + target_platform_config[target_platform]['config']['amiga_whdload_file'] + "\n"
			
			game_dir = game['Dir']
			game_dir_ralative_path = game_dir.replace(ucg_conf['config']['target_games_path'], '')
			game_dir_ralative_path = game_dir_ralative_path.replace("\\", target_platform_directory_separator)
			game_dir_ralative_path = game_dir_ralative_path.replace("/", target_platform_directory_separator)
			final_path = target_platform_config[target_platform]['config']['parent_path'] + target_platform_directory_separator + str(target_platform_config[target_platform]['config']['amiga_games_relative_path']) + game_dir_ralative_path + target_platform_directory_separator + game['Disks']['1']
			final_path = final_path.replace("\\", target_platform_directory_separator)
			final_path = final_path.replace("/", target_platform_directory_separator)
			
			uae_file_contents += "hardfile=" + ucg_conf['config']['base_hardfile_access'] + "," + final_path + "\n"
			
			'''
			print()
			print("cwd_parent:",cwd_parent)
			print("game['Dir']:",game['Dir'])
			print("relative_path:",relative_path)
			print("final_path:",final_path)
			'''
			print()
			print("game_dir:",game_dir)
			print("ucg_conf['config']['target_games_path']:",ucg_conf['config']['target_games_path'])
			print("target_platform_config[target_platform]['config']['amiga_games_relative_path']:",target_platform_config[target_platform]['config']['amiga_games_relative_path'])
			print("game_dir_ralative_path:",game_dir_ralative_path)
			print("final_path:",final_path)
			print()
			
		print(Fore.YELLOW,end='');
		print(uae_file_contents)
		print(Style.RESET_ALL,end='');
		
		
		games[game_name]['UAE'] = uae_file_contents
		
		## Create UAE file
		if(ucg_conf['config']['generate_uae_configs']):
			print()
			#print("ucg_target_uae_path: ", ucg_target_uae_path)
			uae_file_path = Path(ucg_conf['config']['target_uae_path']) / (game['Game'] + ".uae")
			print(Fore.YELLOW + Style.BRIGHT + "Saved: " + str(uae_file_path) + Style.RESET_ALL)
			uae_file = open(uae_file_path, "w+")
			uae_file.write(uae_file_contents)
			uae_file.close
					
		print()

		
	##
	## Tab: Game Files - tab_game_files
	##
	
	## Tab
	tab_uae_configs = ttk.Frame(tab_control, name='tab_uae_configs')
	tab_control.add(tab_uae_configs, text='UAE Configs', image=images['uae-aga']['image'], compound='left')

	# Add to global widget list
	global_widget_list.update({'tab_uae_configs': tab_uae_configs})
	
	## Frame
	frame_treeview_uae_configs = ttk.Frame(tab_uae_configs, name='frame_treeview_uae_configs')
	frame_treeview_uae_configs.pack(expand='yes', fill='both')
	
	## Tree
	tree_uae_configs = ttk.Treeview(frame_treeview_uae_configs, columns=("type","chipset"))
	tree_uae_configs.heading("#0", text=ucg_conf['config']['target_uae_path'])
	tree_uae_configs.heading("type", text="Game Type")
	tree_uae_configs.heading("chipset", text="Game Chipset")
	
	## Scrollbar
	scrollbar_tree_uae_configs = ttk.Scrollbar(frame_treeview_uae_configs, command=tree_uae_configs.yview)
	scrollbar_tree_uae_configs.pack(side='right', fill='y')
	tree_uae_configs.configure(yscrollcommand= scrollbar_tree_uae_configs.set)
	
	##
	
	tree_uae_configs.delete(*tree_uae_configs.get_children())
	
	for game_name,game in games.items():
		
		game_tag = ''
		
		if((game['Type'] == '.adf')):
			if(len(game['Disks']) == 1):
				game_tag = "disk"
			if(len(game['Disks']) > 1):
				game_tag = "disk_multiple"
		if((game['Type'] == '.zip')):
			if(len(game['Disks']) == 1):
				game_tag = "compress"
			if(len(game['Disks']) > 1):
				game_tag = "compress_multiple"
		if(game['Type'] == '.hdf'):
			game_tag = ".hdf"
		
		issues_tag = ''
		
		for issue_key, issue_value in filename_issues.items():
			#print("issue_key:",issue_key)
			#print("issue_value:",issue_value)
			if game_name in issue_value.values():
				issues_tag = 'issue'
		'''
		print()
		print("issues_tag:",issues_tag)
		print()
		'''
		
		# UAE file
		tree_uae_configs.insert('', 'end', game_name, text=game_name + ".uae", values=(game['Type'], game['Chipset']), tags = ('uae-' + game['Chipset'],issues_tag,))			
		
		# Chipset
		tree_uae_configs.insert(game_name, 'end', game_name + "_" + "Chipset", text="chipset: " + game['Chipset'], tags=(game['Chipset'],))
				
		# WHDLoad.hdf
		if(game['Type'] == '.hdf'):
			tree_uae_configs.insert(game_name, 'end', game_name + "_" + "WHDLoad", text="hardfile: " + target_platform_config[target_platform]['config']['amiga_whdload_file'], tags=('drive',))
		
		for disk_id, disk in game['Disks'].items():
		
			disk_tag =''
			
			if(game['Type'] == '.adf'):
				if(int(disk_id) < ucg_conf['config']['max_nr_floppies']):
					disk_tag = "drive_disk"
					tree_uae_configs.insert(game_name, 'end', disk, text="floppy" + str(disk_id) + ": " + disk, tags=(disk_tag,))
			if(game['Type'] == '.zip'):
				if(int(disk_id) < ucg_conf['config']['max_nr_floppies']):
					disk_tag = "drive_compress"
					tree_uae_configs.insert(game_name, 'end', disk, text="floppy" + str(disk_id) + ": " + disk, tags=(disk_tag,))
			if((game['Type'] == '.hdf')):
				disk_tag = "drive"
				tree_uae_configs.insert(game_name, 'end', disk, text="hardfile: " + disk, tags=(disk_tag,))

	tree_uae_configs.bind("<ButtonRelease-1>", on_uae_config_tree_select)
	
	tree_uae_configs.tag_configure('issue', background='#ffdddd')
	
	tree_uae_configs.tag_configure('.adf', image=images['.adf']['image'])
	tree_uae_configs.tag_configure('disk', image=images['disk']['image'])
	tree_uae_configs.tag_configure('disk_multiple', image=images['disk_multiple']['image'])
	tree_uae_configs.tag_configure('.zip', image=images['.zip']['image'])
	tree_uae_configs.tag_configure('compress', image=images['compress']['image'])
	tree_uae_configs.tag_configure('compress_multiple', image=images['compress_multiple']['image'])
	tree_uae_configs.tag_configure('.hdf', image=images['.hdf']['image'])
	tree_uae_configs.tag_configure('drive_disk', image=images['drive_disk']['image'])
	tree_uae_configs.tag_configure('drive_compress', image=images['drive_compress']['image'])
	tree_uae_configs.tag_configure('drive', image=images['drive']['image'])
	tree_uae_configs.tag_configure('uae-aga', image=images['uae-aga']['image'])
	tree_uae_configs.tag_configure('uae-ocs', image=images['uae-ocs']['image'])
	tree_uae_configs.tag_configure('aga', image=images['aga']['image'])
	tree_uae_configs.tag_configure('ocs', image=images['ocs']['image'])
		
	tree_uae_configs.pack(side='left', expand='yes', fill='both')
	#tree_uae_configs.pack(expand=True, fill='y')
	#tree_uae_configs.grid(row=0, column=0, sticky=NS)
	
		
	
	## Text box
	
	text_uae_config = tk.Text(tab_uae_configs, height=30, width=80, name='text_uae_config')
	
	#text_uae_config.grid(row=0, column=1, sticky=NW)
	text_uae_config.pack(side='right', expand='yes', fill='both')
	contents = "Click an item to view the generated UAE config."
	text_uae_config.insert('end', contents)

	global_widget_list.update({'text_uae_config': text_uae_config})

def create_snesc_tab():

	##
	## Tab: SNES Classic - tab_snesc
	##
	
	tab_snesc = ttk.Frame(tab_control, name='tab_snesc')
	
	# Add to global widget list
	global_widget_list.update({'tab_snesc': tab_snesc})
	
	tab_control.add(tab_snesc, text='SNES Classic', image=images['snesc']['image'], compound='left')
	
	
	## Tree
	tree_snesc = ttk.Treeview(tab_snesc, columns=('src','dst'))
	#tree_snesc.heading("#0", text=ucg_conf['config']['target_uae_path'])
	tree_snesc.heading("src", text="Copy Source")
	tree_snesc.heading("dst", text="Copy Destination")
	
	## Scrollbar
	scrollbar_tree_snesc = ttk.Scrollbar(tab_snesc, command=tree_snesc.yview)
	scrollbar_tree_snesc.pack(side='right', fill='y')
	tree_snesc.configure(yscrollcommand=scrollbar_tree_snesc.set)
	
	#
	# SNES Classic/Mini - Linked Export
	#


	if(ucg_conf['config']['snesc_linked_export_show_uae_games']):
		print()
		print("SNES Classic:\n")
		
		snesc_linked_export_games_path = str(Path(cwd_parent) / target_platform_config[target_platform]['config']['snesc_linked_export_games_relative_path'])
		
		print("snesc_linked_export_games_path: " + snesc_linked_export_games_path)
		
		for dirName, subdirList, fileList in os.walk(snesc_linked_export_games_path):
			
			print("[DIR] " + dirName)
			
			for fname in fileList:
			
				filename, file_extension = os.path.splitext(fname)
			
				if(file_extension == ".uae"):
				
					#tree_snesc.insert(dirName, 'end', fname, text=fname, tags=('uae',))
					tree_snesc.insert('', 'end', fname, text=fname, tags=('issue',))
					
					print("  +---[FILE] " + fname)
					
					if(ucg_conf['config']['snesc_linked_export_match_by'] == "filename"):		## Match by filename
					
						if filename in games.keys():		## If game exists in games dict
							
							game = games[filename]
							
							print("  +---[GAME] " + Fore.GREEN + game['Game'] + Style.RESET_ALL)
							
							game_tag = ''
		
							if((game['Type'] == '.adf')):
								if(len(game['Disks']) == 1):
									game_tag = "disk"
								if(len(game['Disks']) > 1):
									game_tag = "disk_multiple"
							if((game['Type'] == '.zip')):
								if(len(game['Disks']) == 1):
									game_tag = "compress"
								if(len(game['Disks']) > 1):
									game_tag = "compress_multiple"
							if(game['Type'] == '.hdf'):
								game_tag = ".hdf"
							
							'''
							print()
							print("game_tag:",game_tag)
							print()
							'''
							
							tree_snesc.insert(fname, 'end', game['Game'], text=game['Game'], tag=(game_tag,))
							
							tree_snesc.item(fname, tag=('uae-' + game['Chipset'],)) ## Update parent UAE file tags
							
							uae_file_path = str(Path(ucg_conf['config']['target_uae_path']) / (filename + ".uae"))
							
							if(ucg_conf['config']['snesc_linked_export_copy_uae_config']):
							
								print()
								print(Fore.RED,end='');
								print(Style.BRIGHT,end='');
								print("  +---[COPY UAE CONFIG BY FILENAME]")
								print(Style.RESET_ALL,end='');
								
								print(Fore.RED,end='');
								print(Style.BRIGHT,end='');
								print("        +---[SRC] " + str(uae_file_path))
								print("        +---[DST] " + str(Path(dirName) / fname))
								print(Style.RESET_ALL,end='');
								
								try:
									#copyfile(uae_file_path, Path(dirName) / fname)
									copy2(uae_file_path, Path(dirName) / fname)		## copy2() copies with with timestamp
								except IOError as exception:
									print("\tCopy error:",exception)
								finally:
									print("\tCopied OK")
								
								tree_snesc.item(fname, values=(uae_file_path,Path(dirName) / fname))
						
					
					if(ucg_conf['config']['snesc_linked_export_match_by'] == "contents"):		## Match by contents
					
						## Get file contents
						with open(Path(dirName) / fname) as snesc_uae_file:
							snesc_uae_file_lines = snesc_uae_file.read().splitlines()
						
						print()
						print(Fore.YELLOW,end='');
						print(snesc_uae_file_lines[0])	## Header
						print(snesc_uae_file_lines[1])	## Platform
						print(snesc_uae_file_lines[2])	## Game
						print(snesc_uae_file_lines[3])	## Type
						print(snesc_uae_file_lines[4])	## Chipset
						print(Style.RESET_ALL,end='');
						
						contents_game_name = snesc_uae_file_lines[2].split('#Game=')
	
						if(len(contents_game_name) > 1):
							if contents_game_name[1] in games.keys():
								
								print("  +---[GAME] " + Fore.GREEN + contents_game_name[1] + Style.RESET_ALL)
								
								if(ucg_conf['config']['snesc_linked_export_copy_uae_config']):
								
									uae_file_path = str(Path(ucg_conf['config']['target_uae_path']) / (contents_game_name[1] + ".uae"))
								
									print()
									print(Fore.RED,end='');
									print(Style.BRIGHT,end='');
									print("  +---[COPY UAE CONFIG BY CONTENTS]")
									print(Style.RESET_ALL,end='');
									
									print(Fore.RED,end='');
									print(Style.BRIGHT,end='');
									print("        +---[SRC] " + str(uae_file_path))
									print("        +---[DST] " + str(Path(dirName) / fname))
									print(Style.RESET_ALL,end='');
								
									try:
										#copyfile(uae_file_path, Path(dirName) / fname)
										copy2(uae_file_path, Path(dirName) / fname)		## copy2() copies with with timestamp
									except IOError as exception:
										print("\tCopy error:",exception)
									finally:
										print("\tCopied OK")
						
					
			print()
			
			tree_snesc.tag_configure('issue', background='#ffdddd')
			tree_snesc.tag_configure('directory', background='#E8E8E8', image=images['dir']['image'])
			tree_snesc.tag_configure('disk', image=images['disk']['image'])
			tree_snesc.tag_configure('disk_multiple', image=images['disk_multiple']['image'])
			tree_snesc.tag_configure('compress', image=images['compress']['image'])
			tree_snesc.tag_configure('compress_multiple', image=images['compress_multiple']['image'])
			tree_snesc.tag_configure('.hdf', image=images['.hdf']['image'])
			#tree_snesc.tag_configure('uae', image=images['uae']['image'])
			#tree_snesc.tag_configure('uae-grey', background='#FFDDDD', image=images['uae-grey']['image'])
			tree_snesc.tag_configure('uae-aga', image=images['uae-aga']['image'])
			tree_snesc.tag_configure('uae-ocs', image=images['uae-ocs']['image'])
			tree_snesc.pack(expand='yes', fill='both')

def on_option_target_platform_select(value):
	
	print("value:",value)
	
	## Update games and uae path
	
	## Calculate
	ucg_conf['config']['target_games_path'] = str(Path(cwd_parent) / target_platform_config[value]['config']['amiga_games_relative_path'])
	ucg_conf['config']['target_uae_path'] = str(Path(cwd_parent) / target_platform_config[value]['config']['amiga_uae_relative_path'] / value)
	
	## Delete
	global_widget_list['entry_games_path'].delete(0, 'end')
	global_widget_list['entry_uae_path'].delete(0, 'end')
	
	## Update
	global_widget_list['entry_games_path'].insert(0, ucg_conf['config']['target_games_path'])
	global_widget_list['entry_uae_path'].insert(0, ucg_conf['config']['target_uae_path'])

def on_config_tree_select(event):

	item_name = event.widget.focus()		## Name of item
	
	if(item_name != ''):
	
		#print("item_name: ", item_name)
		
		item_list = item_name.split("_")
	
		#print("item_list:",item_list)
		
		##
		## Update text box
		##
		
		if(len(item_list) == 2):
		
			if(item_list[1] == "config"):
				global_widget_list['text_target_platform'].delete('1.0', 'end')
				global_widget_list['text_target_platform'].insert('end', json.dumps(target_platform_config[item_list[0]]['config'], indent=4))
		
		elif(len(item_list) == 4):
		
			global_widget_list['text_target_platform'].delete('1.0', 'end')
			
			'''
			## Update using json format
			global_widget_list['text_target_platform'].insert('end', json.dumps(target_platform_config[item_list[0]]['uae'][item_list[2]][item_list[3]], indent=4))
			'''
			
			'''
			## Update using uae format
			update_text = ""
			for line_index, line_value in target_platform_config[item_list[0]]['uae'][item_list[2]][item_list[3]].items():
				update_text += line_index + "=" + line_value + "\n"
			global_widget_list['text_target_platform'].insert('end', update_text)
			'''
			
			## Updating using actual file
			uae_template_file_path = Path(cwd) / "conf" / "templates" / item_list[0] / "uae" / item_list[2] / item_list[3] / "template.uae"
			with open(uae_template_file_path,'r') as uae_template_file:
				uae_template_file_contents = uae_template_file.read()
			global_widget_list['text_target_platform'].insert('end', uae_template_file_contents)
			
		else:
			global_widget_list['text_target_platform'].delete('1.0', 'end')
			
		##
		## Update platform target,  games and uae path
		##
		
		## Calculate
		ucg_conf['config']['target_games_path'] = str(Path(cwd_parent) / target_platform_config[item_list[0]]['config']['amiga_games_relative_path'])
		ucg_conf['config']['target_uae_path'] = str(Path(cwd_parent) / target_platform_config[item_list[0]]['config']['amiga_uae_relative_path'] / item_list[0])
		
		## Delete
		global_widget_list['entry_target_platform'].delete(0, 'end')
		global_widget_list['entry_games_path'].delete(0, 'end')
		global_widget_list['entry_uae_path'].delete(0, 'end')
		
		## Update
		global_widget_list['entry_target_platform'].insert(0, item_list[0])
		global_widget_list['entry_games_path'].insert(0, ucg_conf['config']['target_games_path'])
		global_widget_list['entry_uae_path'].insert(0, ucg_conf['config']['target_uae_path'])
##
## ----------------------------------------------------------------------------
##



##
## Generate images dictionary
##

images = {
	'ucg': {
		'path': Path(cwd) / "img/ucg-logo.png"
	},
	'uae': {
		'path': Path(cwd) / "img/uae-16x16.png"
	},
	'uae-grey': {
		'path': Path(cwd) / "img/uae-grey-16x16.png"
	},
	'uae-aga': {
		'path': Path(cwd) / "img/uae-aga.png"
	},
	'uae-ocs': {
		'path': Path(cwd) / "img/uae-ocs.png"
	},
	'linux': {
		'path': Path(cwd) / "img/linux.png"
	},
	'windows': {
		'path': Path(cwd) / "img/windows.png"
	},
	'python': {
		'path': Path(cwd) / "img/python-16x16.png"
	},
	'aga': {
		'path': Path(cwd) / "img/aga-16x16.png"
	},
	'ocs': {
		'path': Path(cwd) / "img/ocs-16x16.png"
	},
	'snesc': {
		'path': Path(cwd) / "img/snesc-16x16.png"
	},
	'android': {
		'path': Path(cwd) / "img/android-16x16.png"
	},
	'dir': {
		'path': Path(cwd) / "img/silk/folder.png"
	},
	'.adf': {
		'path': Path(cwd) / "img/silk/disk.png"
	},
	'disk': {
		'path': Path(cwd) / "img/silk/disk.png"
	},
	'disk_multiple': {
		'path': Path(cwd) / "img/silk/disk_multiple.png"
	},
	'.zip': {
		'path': Path(cwd) / "img/silk/compress.png"
	},
	'compress': {
		'path': Path(cwd) / "img/silk/compress.png"
	},
	'.hdf': {
		'path': Path(cwd) / "img/silk/database.png"
	},
	'floppy': {
		'path': Path(cwd) / "img/silk/drive_disk.png"
	},
	'drive_disk': {
		'path': Path(cwd) / "img/silk/drive_disk.png"
	},
	'hardfile': {
		'path': Path(cwd) / "img/silk/drive.png"
	},
	'drive': {
		'path': Path(cwd) / "img/silk/drive.png"
	},
	'cog': {
		'path': Path(cwd) / "img/silk/cog.png"
	},
	'joystick': {
		'path': Path(cwd) / "img/silk/joystick.png"
	},
	'cog_go': {
		'path': Path(cwd) / "img/silk/cog_go.png"
	},
	'compress_multiple': {
		'path': Path(cwd) / "img/silk/custom/compress_multiple.png"
	},
	'drive_compress': {
		'path': Path(cwd) / "img/silk/custom/drive_compress.png"
	},
	'target': {
		'path': Path(cwd) / "img/fugue/target.png"
	},
	'information-white': {
		'path': Path(cwd) / "img/fugue/information-white.png"
	}
}

for image_key, image in images.items():
	images[image_key]['handle'] = Image.open(images[image_key]['path'])
	images[image_key]['image'] = ImageTk.PhotoImage(images[image_key]['handle'])
	
##
## Create Notebook (for tabs)
##

tab_control = ttk.Notebook(window, name='ucg')

# Add to global widget list
global_widget_list.update({'tab_control': tab_control})

##
##
##

##
## Tab: About
##

tab_about = ttk.Frame(tab_control, name='tab_about')
tab_control.add(tab_about, text='About', image=images['information-white']['image'], compound='left')

# Add to global widget list
global_widget_list.update({'tab_about': tab_about})

##
## System
##

label_about_system = ttk.Label(tab_about, text= 'System:')
label_about_system.grid(row=0, column=0, sticky='E')

if(platform.system() == 'Windows'):
	label_about_system_image = ttk.Label(tab_about, image=images['windows']['image'], text='Windows', compound='left')
	label_about_system_image.grid(row=0, column=1, columnspan=2, sticky='w')

if(platform.system() == 'Linux'):
	label_about_system_image = Label(tab_about, image=images['linux']['image'], text='Linux', compound='left')
	label_about_system_image.grid(row=0, column=1,  columnspan=2, sticky='w')

##	
## Python
##

label_about_python_version = ttk.Label(tab_about, text= 'Python:')
label_about_python_version.grid(row=1, column=0, sticky='e')

label_about_python_version_image = ttk.Label(tab_about, justify='left', image=images['python']['image'], text=platform.python_version(), compound='left')
label_about_python_version_image.grid(row=1, column=1, sticky='w')

##
##
##

##
## Tab: Target Platform
##

tab_target_platform = ttk.Frame(tab_control, name='tab_target_platform')
tab_control.add(tab_target_platform, text='Target Platform', image=images['target']['image'], compound='left')

# Add to global widget list
global_widget_list.update({'tab_target_platform': tab_target_platform})




'''
##
## Separator
##

separator_tab_target_platform = ttk.Separator(tab_target_platform, orient="horizontal")
separator_tab_target_platform.grid(row=2, column=0, columnspan=6, sticky="we")
'''


'''
variable_target_platform = StringVar(window)	## Options variable
variable_target_platform.set(target_platform)	
'''

'''
#option_target_platform = OptionMenu(tab_target_platform, variable_target_platform, *platform_list.keys(), command=on_option_target_platform_select)
option_target_platform = OptionMenu(tab_target_platform, variable_target_platform, *target_platform_config.keys(), command=on_option_target_platform_select)
option_target_platform.grid(row=3, column=1, sticky=W)
'''




##
## Tab: Target Platform / Tree
##

tree_target_platform = ttk.Treeview(tab_target_platform, height=5, show="tree")
#tree_target_platform.heading("#0", text=ucg_conf['config']['target_uae_path'])
#tree_target_platform.heading("config_value", text="Config value")
#tree_target_platform.heading("dst", text="Copy Destination")
tree_target_platform.grid(row=4, rowspan=4, column=0, columnspan=4, sticky='w')

## Tab: Target Platform / Tree Scrollbar
scrollbar_tree_target_platform = ttk.Scrollbar(tab_target_platform, command=tree_target_platform.yview)
scrollbar_tree_target_platform.grid(row=4, rowspan=4, column=0, columnspan=4, sticky='nse')
tree_target_platform.configure(yscrollcommand=scrollbar_tree_target_platform.set)

##

for platform_index, platform_value in target_platform_config.items():

	## Add platform node
	tree_target_platform.insert('', 'end', platform_index, text=platform_index, tag=(platform_value['config']['system'],))
	
	## Add config node
	tree_target_platform.insert(platform_index, 'end', platform_index + "_config" , text='config', tag=('cog',))
	
	## Add uae node
	tree_target_platform.insert(platform_index, 'end', platform_index + "_uae" , text='uae', tag=('uae-aga',))
	
	## Add uae - ocs node
	tree_target_platform.insert(platform_index + "_uae", 'end', platform_index + "_uae_ocs" , text='ocs', tag=('ocs',))
	
	## Add uae - ocs - adf node
	tree_target_platform.insert(platform_index + "_uae_ocs", 'end', platform_index + "_uae_ocs_adf" , text='adf', tag=('.adf',))
	
	## Add uae - ocs - hdf node
	tree_target_platform.insert(platform_index + "_uae_ocs", 'end', platform_index + "_uae_ocs_hdf" , text='hdf', tag=('.hdf',))
	
	## Add uae - aga node
	tree_target_platform.insert(platform_index + "_uae", 'end', platform_index + "_uae_aga" , text='aga', tag=('aga',))
	
	## Add uae - aga - adf node
	tree_target_platform.insert(platform_index + "_uae_aga", 'end', platform_index + "_uae_aga_adf" , text='adf', tag=('.adf',))
	
	## Add uae - aga - hdf node
	tree_target_platform.insert(platform_index + "_uae_aga", 'end', platform_index + "_uae_aga_hdf" , text='hdf', tag=('.hdf',))

## Select first in target platform list
tree_target_platform.selection_set(list(target_platform_config.keys())[0])
	
##
## Labels and entries
##
		
## Tab: Target Platform / Target Platform

## Set some defaults configs - to be displayed in GUI on startup
target_platform = list(target_platform_config.keys())[0] ## Set to first in target platform list
ucg_conf['config']['target_games_path'] = str(Path(cwd_parent) / target_platform_config[target_platform]['config']['amiga_games_relative_path'])
ucg_conf['config']['target_uae_path'] = str(Path(cwd_parent) / target_platform_config[target_platform]['config']['amiga_uae_relative_path'] / target_platform)
	
label_target_platform = ttk.Label(tab_target_platform, justify='right', text= 'Target Platform:')
label_target_platform.grid(row=4, column=4, sticky='e')

#entry_target_platform = tk.Entry(tab_target_platform, bd=2, width=50)
entry_target_platform = ttk.Entry(tab_target_platform, width=50)
entry_target_platform.insert(0, target_platform)
entry_target_platform.grid(row=4, column=5, sticky='w')

# Add to global widget list
global_widget_list.update({'entry_target_platform': entry_target_platform})

## Tab: Target Platform / Games Path

label_games_path = ttk.Label(tab_target_platform, justify='right', text= 'Games Path:')
label_games_path.grid(row=5, column=4, sticky='e')

#entry_games_path = tk.Entry(tab_target_platform, bd=2, width=50)
entry_games_path = ttk.Entry(tab_target_platform, width=50)
entry_games_path.insert(0, ucg_conf['config']['target_games_path'])
entry_games_path.grid(row=5, column=5, sticky='w')

# Add to global widget list
global_widget_list.update({'entry_games_path': entry_games_path})

## Tab: Target Platform / UAE Path

label_uae_path = ttk.Label(tab_target_platform, justify='right', text= 'UAE Configs Path:')
label_uae_path.grid(row=6, column=4, sticky='e')

#entry_uae_path = tk.Entry(tab_target_platform, bd=2, width=50)
entry_uae_path = ttk.Entry(tab_target_platform, width=50)
entry_uae_path.insert(0, ucg_conf['config']['target_uae_path'])
entry_uae_path.grid(row=6, column=5, sticky='w')

# Add to global widget list
global_widget_list.update({'entry_uae_path': entry_uae_path})

##
## Tab: Target Platform / Start
##

button_start = ttk.Button(tab_target_platform, text="Start", image=images['cog_go']['image'], command=start, compound='left')
button_start.grid(row=7, column=4, sticky='e')

##
## Tab: Target Platform / Progress Bar
##

progressbar_start = ttk.Progressbar(tab_target_platform,orient="horizontal",length=300,mode="determinate")
progressbar_start.grid(row=7, column=5, sticky='w')

progressbar_currentValue=0
progressbar_maxValue=100

progressbar_start["value"]=progressbar_currentValue
progressbar_start["maximum"]=progressbar_maxValue

##
## Tab: Target Platform / Text box
##
	
text_target_platform = tk.Text(tab_target_platform, height=30, width=80, name='text_target_platform', wrap='word')


text_target_platform.grid(row=8, column=0, columnspan=6, sticky='s')
#text_target_platform.pack(side='right', expand='yes', fill='both')
contents = "Select a target platform and click on the Start button to start analysis and generation.\n"
contents += "Or select a config or template item to view the contents."
text_target_platform.insert('end', contents)

global_widget_list.update({'text_target_platform': text_target_platform})

## Tab: Target Platform / Text Scrollbar
scrollbar_text_target_platform = ttk.Scrollbar(tab_target_platform, command=text_target_platform.yview)
scrollbar_text_target_platform.grid(row=8, column=0, columnspan=6, sticky='nse')
text_target_platform.configure(yscrollcommand=scrollbar_text_target_platform.set)

##
##
##

tree_target_platform.bind("<ButtonRelease-1>", on_config_tree_select)

tree_target_platform.tag_configure('snesc', image=images['snesc']['image'])
tree_target_platform.tag_configure('android', image=images['android']['image'])
tree_target_platform.tag_configure('cog', image=images['cog']['image'])
tree_target_platform.tag_configure('uae', image=images['uae']['image'])
tree_target_platform.tag_configure('aga', image=images['aga']['image'])
tree_target_platform.tag_configure('ocs', image=images['ocs']['image'])
tree_target_platform.tag_configure('uae-aga', image=images['uae-aga']['image'])
tree_target_platform.tag_configure('uae-ocs', image=images['uae-ocs']['image'])
tree_target_platform.tag_configure('.adf', image=images['.adf']['image'])
tree_target_platform.tag_configure('.hdf', image=images['.hdf']['image'])

tab_control.pack(expand=1, fill='both')

window.mainloop()