# UCG (UAE Configuration Generator) v0.1 beta

UCG is a GUI tool developed using **Python 3** that generates UAE configuration files that are used by various UAE based Amiga emulators and game launchers.

The tool creation was inspired by the excellent guides at:

https://www.reddit.com/r/miniSNESmods/comments/8dbqv7/guide_playing_amiga_games_on_the_snes_classic/
http://lindqvist.synology.me/wordpress/?page_id=182

and is to help automate the UAE configuration file creation process, providing a templated method for differrent target platforms.

## Supported Amiga Game File formats

UCG supports UAE configuration for the following Amiga game file formats:

 - ADF (.adf and .zip)
 - HDF (.hdf)
 
### ADF (.adf and .zip) files
 
 **Note:** The .zip game file should only contain a single .adf file within it.
 
 Games that span single and multiple files are supported.
 
 For **multiple** disk game files need to meet the following filename convention:
 
 (Game Name)__Disk(Disk Value)
  
 **Note:** the "__" is a double underscore
  
 Where:
   - (Game Name) is the name of the game. The game files need to have exactly the same (Game Name) in order to be considered the same game.
   - (Disk Value) is the number of the disk for the game.
      - The (Disk Value) can be alphanumeric. But it should either be all numeric, or all alpha.
 
 UCG will sort the all the disks belong to a game in alphanumeric order, with numeric characters first, then alpha characters.

However, UAE emulators typically only support up to a maximum of 4 (four) floppy drives - so onlythe first 4 (four) ADF game disk files (.adf or .zio) will be mapped to floppy drives 0 to 3, respectively.

**Note:** Some Amiga games will only recognise/use the the first floppy drive (DF0:) - so you may still need to use the emulator method to swap out the game disk files.

### HDF (.hdf) files
 
HDF based game files are from WHDLoad based games. Use the following guide to create your WHLoad.hdf and .hdf game files.
 
http://lindqvist.synology.me/wordpress/?page_id=182
 
UCG will allocate the WHDLoad.hdf and .hdf game file as harddrive

## Directory and filename format

UCG will only **check** and **warn** for disallowed characters in a game directory or file.

The list of disallowed characters configured in **conf/conf.json** in the **config** section - the default is:

```json
"disallowed_characters": [" ", "'"],
```

i.e. space and apostrophes

Note: Removing apostrophes may hinder game data scraping, as some games names do have valid use of apostrophes in them.

### Bulk rename tool

A recommended Windows tool for bulk renaming files is **Advanced Renamer**:

https://www.advancedrenamer.com/

**Warning:** Avoid using Advanced Renamer on FAT16/FAT32 partitions - there are issues with 8.3 format filenames related to 'short names' and 'long names'. See the following posts for further details:

https://www.advancedrenamer.com/forum_thread?forum_id=5832
https://superuser.com/questions/1297658/folder-names-become-uppercase-when-syncing-to-fat32-drive

## Installation

Extract the release .zip file to the same directory as your target platform **ROMs** directory.

The UCG directory requires to be in a specific location, relative to where the target game and kickstart files are stored.
 
UCG has been developed assuming that it will be used to generate UAE configuration files for a 'remote' target platform. Typically, the game files would be located on a SD card or USB memory stick. It is intended that the UCG tool is installed in this same location, and executed from there.
 
With that in mind, the recommended and supported file structure should be:

<pre>
<ROOT>
   +---[DIR] UCG
   |       +---[FILE] ucg.py							            # UCG python script
   |       +---[FILE] ucg.exe                        # UCG frozen python executable
   |       +---[DIR] img                             # Images directory used by UCG
   |       `---[DIR] conf                            # Configuration and templates directory used by UCG
   |             +---[FILE] config.json              # Configuration file used by UCG
   |             `---[DIR] templates
   |                   `---[DIR] (target platform name)       # The target platform configuration and templates directory
   |                         +---[FILE] template.json         # The target platform configuration file
   |                         `---[DIR] uae                    # The target platform UAE templates directory
   |                               +---[DIR] aga
   |                               |     +---[DIR] adf
   |                               |     |     `---[FILE] template.uae
   |                               |     `---[DIR] hdf
   |                               |           `---[FILE] template.uae
   |                               `---[DIR] ocs
   |                                     +---[DIR] adf
   |                                     |     `---[FILE] template.uae
   |                                     `---[DIR] hdf
   |                                           `---[FILE] template.uae
   +---[DIR] ROMs								                # Example ROMs directory
   |      `---[DIR] Amiga		              # Example Amiga directory
   |            +---[DIR] Games					     # This is where your ADF and HDF game files should go. Can contain subdirectories.
   |            |     +---[DIR] ADF				  # Example and recommended sub-dir for ADF (.adf and .zip) games. Can contain further subdirectories.
   |            |     `---[DIR] HDF				  # Example and recommended sub-dir for HDF (.hdf) games. Can contain further subdirectories.
   |            +---[DIR] UAE					       # For the generated .uae config files. This directory will get created by the script if it does not exist.
   |                  +---[DIR] (target platform name)   # Each platform will have a subdirectory for its generated UAE config files. Will get created if it does not exist.
   |            +---[DIR] WHDLoad
   |            |     `---[FILE] WHDLoad.hdf		# The WHDLoad.hdf file
   |            `---[DIR] Kickstarts
   |                  +---[FILE] kick31.rom		  # The kickstart file
   |                  `---[FILE] rom.key			  # The rom.key file for Cloanto Amiga Forever kickstart files.
   `---[DIR] linked-export     # Example SNES Classic Hakchi2 CE directory name (for linked export mode)
          `---[DIR] games      # This is where the Hakchi2 CE .uae configs appear (in sub directores for each game).
</pre>

The **ROMs** directory is where you should have your game and kickstart files.

**Note:** Some guides will suggest you to put the kickstart and WHDLoad.hdf files in a specific directory for the target platform emulator used. For example, for Retroarch it is typically suggested to put them in its 'system' directory. However, I would suggest to keep your Amiga game and kickstart files in a similar location relative to the game files, i.e. to group them together inside the ROMs directory.

### Target platform configuration and UAE templates

Some Example target platform comfiguration and UAE templates have been provided for the following:

 - android-uae4arm (Android uae4arm)
 - snesc-puae (SNES Classic Retroarch P-UAE)

The configuration and templates for these target platform is based on the directory structure shown above.

UCG will scan the *UCG/conf/templates* directory. The name of the subdirectory will be used as the target platform name, and the exact directory and file structure is expected to exist - as shown above.

The target platform confuguration must be at:

- conf/templates/(target platform)/template.json 

And the UAE templates are must be at the following locations:

- conf/templates/(target platform)/uae/ocs/adf/template.uae
- conf/templates/(target platform)/uae/ocs/hdf/template.uae
- conf/templates/(target platform)/uae/aga/adf/template.uae
- conf/templates/(target platform)/uae/aga/hdf/template.uae

There are template files in separate **OCS** and **AGA** and **ADF** and **HDF** directories. This intentional and is to allow differrent UAE configurations for those different chipset and game file types. If you don't require for them to be differrent, then just make the template.uae files the same for any or all of the types.

The target platform config and UAE template file is intentially and generially called **template.json** and **template.uae** so that it is easy just to copy an existing target platform directory to make a new one (although, you still need to edit the contents accordingly). 

UCG detects whether an Amiga game chipset is OCS or AGA. This is done by whether is has 'AGA' in the filename or not. The game type is them determined - whether is ADF or HDF. The appropriate UAE template is then used based on these two types.

### Python script or executable?

You can choose to download and run UCG as a python script or as a Windows executable.

#### Run as Python script

To run as a python script you need to have the Python 3 environment and required modules installed.

#### Run as Python executable

The executable will package the Python 3 runtime environment and modules together. So you will not need to have Python 3 installed, but it comes at the expense of a large executable footprint (since it also contains the Python 3 runtime environment and modules).

This only been has been tested on a Windows 10 environment.

## Usage

TO DO...

 - Launch ucg.py / ucg.exe
 - Go to **Target Platforms** tab
   - Can view target Platform configs and UAE template files
 - Select a **Target Platform** from the list
 - Click the **Start** button
 - New tabs will be created for:
   - **Game Files**          *(List of found game files)*
   - **Game List**           *(List of found games)
   - **UAE Configs**         *(List of generated UAE configurations)*
   - **SNESC Classic**       *(If applicable. List of 'linked-exported' games)*
