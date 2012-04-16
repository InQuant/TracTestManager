==============
TC CAD-Actions
==============

1.1 MultiWhereUsed Report
=========================

Show the where used report for multiple EPMDocs.  Select two parts in the CS and
WS list view and display there where used reports in one report form.

Create new workspace
  Navigate to product container  P1271_ru-300 Create a new workspace (workspace
  activated) Workspace name: test_cadactions"
  
  Workspace created

Browse CS
  Navigate to CS Folder: `/ P1271_ru-300 / s_vehicle_linkage_devices /
  sf_gangways_facilities / 11_uebergang-druckertuechtigt`
  
  Folder contents displayed

Select two parts
  Select: `00000701625_b_befestigung_skel.prt 20070628H30_-_PRT0154.PRT`

  two objects marked in list

Exec where used report
  Menu: File -> Where Used 
  
  a new tab will be openened and two tables with the where used structure is shown

Add to WS
  Close the report form and add the 2 marked parts to the workspace created 
  
  The two parts will be listed in the WS

Select
  Select the two parts in the WS list view
  
  two objects marked in list

Exec where used report 
  Menu: File -> Where Used
  
  a new tab will be openened and two tables with the where used structure is
  shown


========================
1.2 Multi Related CADDoc
========================

Report shows the related CAD Doc report for multiple EPMDocs.  Select two parts
in the CS and WS list view and display there related CADDoc reports in one
report form." 

Browse CS
  Navigate to CS Folder: `/ P1271_ru-300 / s_vehicle_linkage_devices /
  sf_gangways_facilities / 11_uebergang-druckertuechtigt`
  
  Folder contents displayed

Select two parts
  "Select: `00000701625_b_befestigung_skel.prt 20070628H30_-_PRT0154.PRT`
  
  two objects marked in list

Exec where used report
  Menu: File -> Related CAD Documents 
  
  a new tab will be openened and six  tables (three per part) is shown

Switch to WS
  Close the report form and switch to WS view from 1.1
  
  The two parts will be listed in the WS

Select
  Select the two parts in the WS list view
  
  two objects marked in list

Exec where used report
  Menu: File -> Related CAD Documents 
  
  a new tab will be openened and six  tables (three per part) is shown

1.3 Multi Set State
===================

Set the lifecycle state of multiple EPMs in a structure view.  Find an assembly
an download it and use the structure view to set the lc state of multiple
objects." 

Find asm and add to WS
  Search for 00000701625_n_befest_klemm.asm and add it to WS test_cadactions

  asm with related parts will be displayed in WS view

Switch to info page structure view
  Click the info icon of the asm and switch to structure view on info page
  
  The asm structure is displayed

Select
  Select the two parts in the structure view: `a6k03330591_-_ensat_m8_307.prt
  00000427616_v_m8x20.prt`
  
  two objects marked in list

Exec Multi Set State
  Use the Toolbar icon: Multi Set State to set the state of the two parts.
  
  The Set State form with the two parts in a structure icon view in Number column ist shown.

Cancel
  Cancel the Set State Form 

1.4 WS Revise menu removed
========================== 

Check if the WS Revise is removed   

Switch to WS
  Switch to WS view of WS test_cadactions

  WS list view is displayed

Check menu and toolbar
  the Revise action should not be present in the workspace (AB icon in workspace
  toolbar, File->New->Revison menu)

  no menu and not toolbar icon

