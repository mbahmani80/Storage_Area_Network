#!/bin/bash - 
#===============================================================================
#
#          FILE: Drive_Cage_Management_and_Physical_Disk_Management.sh
# 
#         USAGE: ./Drive_Cage_Management_and_Physical_Disk_Management.sh 
# 
#        AUTHOR: Mahdi Bahmani (), 
#  ORGANIZATION: 
#       CREATED: 02/18/2022 11:53
#      REVISION:  ---
#===============================================================================

"Drive Cage Management"
# How to locate a particular drive cage
3par01 cli% locatecage

# How to set parameters for a drive cage
3par01 cli% setcage

# Displays drive cage information
3par01 cli% showcage

# Display block mapping info for vvs/lds/pds
3par01 cli% showblock 

# Display logical disks (ld) information
3par01 cli% showld

# Perform validity checks of data on logical disks
3par01 cli% checkld

# Display LD to PD chunklet mapping
3par01 cli% showldch

# Display LD to VV mapping
3par01 cli% showldmap

"Physical Disk Management"
# How to admit one or all physical disks to enable their use
3par01 cli% admitpd

# How to perform surface admit one or all physical disks to enable their use
3par01 cli% checkpd

# How to spin a physical disk up or down
3par01 cli% controlpd

# How to dismiss one or more physical disks from use
3par01 cli% dismisspd

# How to move data from specified PD to a temp location selected by the system
3par01 cli% movepd

# How to perform surface admit one or all physical disks to enable their use
3par01 cli% setpd

# Show status of selected chunklets of physical disks
3par01 cli% showpdch

# Show PD to VV mapping
3par01 cli% showpdvv

# Display estimated free space
3par01 cli% showspace

# Display spare and relocated chunklets
3par01 cli% showspare

