#Check if CSV exists and exits if not
$path = "./Users.csv"
if(![System.IO.File]::Exists($path)){
    Exit
}

#imports CSV
$file = Import-CSV $path -Delimiter ","

#Constants and Init Variables
Import-Module ActiveDirectory
[int]$inc = 0
$array = @()
$space = " "
$domain = "[enterdomainsuffixhere ie: @chs.org"
# Get Date String for Description
$date = Get-Date -format y
$dateMonth = $date.SubString(0,3)
$dateYear = Get-Date -f yyyy
[string]$descriptionDate = $dateMonth + $space + $dateYear
$dash = "-"
[string]$DescriptionFull = $descriptionDate + $space + $dash + $space

#import file, iterate through columns and assign properties to soon to be AD User Object
$file | 
ForEach-Object {
    $prop = @{
        name              = $_.first_name + ' ' + $_.middle_initial + ' ' + $_.last_name
        SamAccountName    = $_.first_name.SubString(0, 1) + $_.last_name
        path              = "OU=OU=Schools,DC=YOURDC,DC=domain"
        UserPrincipalName = $_.first_name.SubString(0, 1) + $_.last_name + $domain
        initials          = $_.middle_initial
        AccountPassword   = (ConvertTo-SecureString "Temp123!" -AsPlainText -Force)
        Enabled           = $true
        email = $_.email
        title = 'Student Teacher'
        office = $_.email
        GivenName = $_.first_name
        Surname = $_.last_name
        DisplayName = $_.first_name + ' ' + $_.middle_initial + ' ' + $_.last_name
        Department = $_.school
        AccountExpirationDate = $_.enddate
        Description = $DescriptionFull + $_.school.ToUpper() + " Student Teacher"
        firstlast         = $_.first_name + ' ' + $_.last_name
    }
    #append all objects to an array for use later
    $array += ($prop)
    
}

#take the array of soon to be AD user objects and ensure their AD SamAccountName is unique
#otherwise append incrementing numbers until it is unique and post it to SamAccountName
$array |
ForEach-Object {
    [string]$username = $_.SamAccountName
    if (Get-ADuser -Filter {SamAccountName -eq $username})
{    
    do {
        $inc ++
        $username = $_.SamAccountName + [string]$inc
    } 
    until (-not (Get-ADuser -Filter {SamAccountName -eq $username}))
    $_.SamAccountName = $username
    $_.UserPrincipalName = $username + $domain
    $inc = 0
}
}

#Create AD Accounts ------------------------------------------------------------------------------------

#Group Variable for assignment later
$Groups = @("Super Staff", "Mega Staff, ADGroupName")

#Take the array of soon to be AD user objects, generate their personalized password, and create the accounts.
$array |
ForEach-Object {
        #password - edit generation as you see fit
         $capital = $_.Surname.SubString(0,1).ToUpper()
         $partial = $_.Surname.SubString(1).ToLower()
         $passName = $capital + $partial
         $passgen = $passName
         $_.AccountPassword = (ConvertTo-SecureString $passgen -AsPlainText -Force)

         #If-Else statement that simply ensures proper spacing in DisplayName and Name based on Middle Initial or lack thereof
         if(-not ($_.initials)){
            New-ADUser -name $_.firstlast -SamAccountName $_.SamAccountName -path $_.path -UserPrincipalName $_.UserPrincipalName.ToLower() -Initials $_.initials -AccountPassword $_.AccountPassword -Enabled $true -Email $_.UserPrincipalName.ToLower() -title 'Student Teacher' -office $_.email.ToLower() -GivenName $_.GivenName -Surname $_.Surname -DisplayName $_.firstlast -Department $_.Department -Description $_.Description -AccountExpirationDate $_.AccountExpirationDate
         }
         else
         {
            New-ADUser -name $_.name -SamAccountName $_.SamAccountName -path $_.path -UserPrincipalName $_.UserPrincipalName.ToLower() -Initials $_.initials -AccountPassword $_.AccountPassword -Enabled $true -Email $_.UserPrincipalName.ToLower() -title 'Student Teacher' -office $_.email.ToLower() -GivenName $_.GivenName -Surname $_.Surname -DisplayName $_.DisplayName -Department $_.Department -Description $_.Description -AccountExpirationDate $_.AccountExpirationDate
         }

         #Assign proper groups to each AD user
         ForEach ($Group in $Groups)
         {
            Add-ADGroupMember -Identity $Group -Members $_.SamAccountName
         }
}
#Removes the original CSV so continually running script doesn't keep trying to import existing users
Remove-Item -Path $path -Force





