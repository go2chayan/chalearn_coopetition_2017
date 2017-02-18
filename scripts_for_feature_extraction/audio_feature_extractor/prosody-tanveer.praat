##############################################
####### Coded by M. Iftekhar Tanveer #########
############ go2chayan@gmail.com  ############
##############################################
form this form gets command line text arguments
word filename "somename"
endform
#echo the command line arguments were 'filename$'

if (fileReadable (filename$))
#echo file 'filename$' is readable
else
#echo file 'filename$' is not readable
endif

Read from file... 'filename$'

soundname$ = selected$("Sound")

################## Extract Pitch ##########################
To Pitch (ac)... 0 75 3 "no" 0.03 0.45 0.01 0.35 0.14 600
select Pitch 'soundname$'
Save as text file: "output.pitch"

#################### Intensity Analysis ###################
select Sound 'soundname$'
To Intensity... 100 0.01 yes
Save as text file: "output.loud"

#################### Formant Analysis #####################
select Sound 'soundname$'
To Formant (burg): 0, 5, 5500, 0.025, 50
Save as text file: "output.formant"
