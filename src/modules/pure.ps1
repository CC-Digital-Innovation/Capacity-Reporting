$MACHINE_IP = $args[0]
$USERNAME = $args[1]
$PASSWORD = $args[2]
$NEWLINE = [System.Environment]::NewLine

$PURE = @(
    $MACHINE_IP
) # Populate this array with DNS names or IP addresses of your Pure arrays
$PWord = ConvertTo-SecureString -String $PASSWORD -AsPlainText -Force

$PureArray = @()
foreach ($name in $PURE) { 
    try { $PureArray += New-PfaArray -EndPoint $name -Username $USERNAME -Password $PWord -IgnoreCertificateError -Verbose -ErrorAction Stop }
    catch { Write-Output "Error accessing $name : $_" }
}
$spacemetrix = $PureArray | Get-PfaArraySpaceMetrics

$totalcapacity = $spacemetrix.capacity/1TB
$snapshots= $spacemetrix.snapshots/1TB
$sharedSpace = $spacemetrix.shared_space/1TB
$volumes = $spacemetrix.volumes/1TB
$usedSpace = $snapshots + $sharedSpace + $volumes

$percentageraw = 1-(($totalcapacity - $usedSpace) / $totalcapacity)
$result = $percentageraw*100
$resultPercent = [math]::Round($result,2)

$totalcap = [math]::Round($totalcapacity, 0)
$totalused = [math]::Round($usedSpace, 3)
$percent = [math]::Round($percentageraw, 4)
#$PureStorageList[$Titles[2]] = $purePercentageUsed - 1

$FreeSpace = $totalcapacity - $usedSpace

$CSV = "Used,Free,Capacity,PercUsed,Used(%)$Newline"
$CSV= $CSV+"$totalused,$FreeSpace,$totalcap,$percent,$resultPercent"

Write-Output $CSV