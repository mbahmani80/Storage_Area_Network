#!/bin/bash - 
#=======================================================================
#
#          FILE:  01_Brocade-Initial-Configuration.sh 
#               
# 
#   DESCRIPTION: Brocade SAN Switches Initial Configurations
#                  
#        AUTHOR: Mahdi Bahmani 
#  ORGANIZATION: www.itstorage.net 
#       CREATED: 2020/02/28 20:00:00
#	LAST CHANGE: 2020/03/31 02:48:10
#      REVISION: 1.0
#=======================================================================

#-----------------------------------------------------------------------
1-Change Default Passwords
#-----------------------------------------------------------------------
2- Clear CFG Configuration
    FC_switch_B_1:admin> cfgdisable
    FC_switch_B_1:admin> cfgclear
    FC_switch_B_1:admin> cfgsave

	
DS_300B1:admin> cfgdisable
You are about to disable zoning configuration. This
action will disable any previous zoning configuration enabled.
Do you want to disable zoning configuration? (yes, y, no, n): [no] yes
Updating flash ...
Effective configuration is empty. "No Access" default zone mode is ON.
DS_300B1:admin> cfgclear
The Clear All action will clear all Aliases, Zones, FA Zones
and configurations in the Defined configuration.
Run cfgSave to commit the transaction or cfgTransAbort to
cancel the transaction.
Do you really want to clear all configurations?  (yes, y, no, n): [no] yes
DS_300B1:admin> cfgsave
You are about to save the Defined zoning configuration. This
action will only save the changes on Defined configuration.
Do you want to save the Defined zoning configuration only?  (yes, y, no, n): [no] yes
Updating flash ...
DS_300B1:admin> cfgshow
Defined configuration:

Effective configuration:
No Effective configuration: (No Access)


DS_300B1:admin>
swd77:admin> switchDisable
swd77:admin> switchcfgpersistentdisable

#-----------------------------------------------------------------------------
3-Set the general switch settings to default: configdefault
FC_switch_A_1:admin> configdefault

#-----------------------------------------------------------------------------
4-Configuring the basic switch settings
DS_300B1:admin> switchcfgpersistentdisable
Switch s persistent state set to 'disabled'

#-----------------------------------------------------------------------------
5-Check License
#Activate Licensed Features
> licenseshow
> licenseadd
> licenseremove
"for Directors"
> licenseslotcfg
#-----------------------------------------------------------------------------
6-Set Hostname
#Set the Switch Name
> switchname
> fabricshow
#-----------------------------------------------------------------------------
date "0201160022"
7-Set Date/Time
DS_300B1:admin> date "0131143222"
Mon Jul  2 16:32:00 UTC 2018
DS_300B1:admin>
# Time zone
SANSW1up22:admin> tsTimeZone --interactive
SANSW1up22:admin> reboot
> tsclockserver
LOCL
> tsclockserver 192.168.40.32
> tsclockserver
"mmddhhmmvv"
"Month day hour minutes year"
> date "0516073406"
"Set TimeZone"
> tsclockserver LOCL
or
> tsclockserver -3
#-----------------------------------------------------------------------------
8-Disable All Ports
DS_300B1:admin> portdisable 0-23
#-----------------------------------------------------------------------------
9-Configure the port speed
DS_300B1:admin> portcfgspeed -i 0-23 8
#-----------------------------------------------------------------------------
10-Set Trunk ports
DS_300B1:admin> portcfgtrunkport  20 1
DS_300B1:admin> portcfgtrunkport  21 1
DS_300B1:admin> portcfgtrunkport  22 1
DS_300B1:admin> portcfgtrunkport  23 1
#-----------------------------------------------------------------------------
11-Change Domain ID
DS_300B1:admin> switchcfgpersistentdisable
DS_300B1:admin> configure
#-----------------------------------------------------------------------------
12-Disable Default Zoneset
#-----------------------------------------------------------------------------
13-Set Login Banner
DS_300B1:admin> bannershow
=================================================================================
                                      ATTENTION:
It is recommended that you change the default passwords for all the switch accounts.
Refer to the product release notes and administrators guide if you need further information.
============================================================================================

DS_300B1:admin> bannerset "Hi"
DS_300B1:admin> bannershow
Hi

#-----------------------------------------------------------------------------
14-#Set syslog Server
> syslogdipshow
> syslogdipadd 10.255.248.2
> syslogdipshow
> syslogdfacility
> syslogdfacility -l 6
> syslogdipremove 10.255.248.3
> syslogdipshow
#-----------------------------------------------------------------------------
15-Set SNMP
snmpconfig --set snmpv1
#-----------------------------------------------------------------------------
16-Set Timeout
DS_300B1:admin> timeout 5
IDLE Timeout Changed to 5 minutes
The modified IDLE Timeout will be in effect after NEXT login
DS_300B1:admin>
#------------------------------------------------------------------------------
DS_300B1:admin> switchcfgpersistentenable
Switchs persistent state set to 'enabled'
DS_300B1:admin>
#------------------------------------------------------------------------------
17-Create Aliases
switchshow
nsshow
alicreate server1_HBA1, ""
alicreate StorageA_SPB_Port1, ""
alishow
#------------------------------------------------------------------------------
19-defzone --noaccess
#------------------------------------------------------------------------------
DS_300B1:admin> defzone --noaccess
You are about to set the Default Zone access mode to No Access
Do you want to set the Default Zone access mode to No Access ? (yes, y, no, n):                                                                [no] yes

#------------------------------------------------------------------------------
#Windows
C:\Users\ArtMan>"C:\Program Files (x86)\Java\jre7\bin\javaws.exe"  http://192.168.2.240/switchExplorer_installed.html

C:\Users\ArtMan>


#Linux
alias sansw1='/usr/lib/jvm/jre1.8.0_161/bin/./javaws http://172.27.8.237/switchExplorer_installed.html'


SANSW2:admin> switchshow 
