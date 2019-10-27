<#
    .SYNOPSIS
        A script that setups Internet Connection Sharing for Pwnagotchi.
    
    .DESCRIPTION
        A script that setups Internet Connection Sharing for Pwnagotchi. 

        Note: Internet Connection Sharing on Windows can be a bit unstable on between reboots.
              You might need to run this script occasionally to disable and re-enable Internet Connection Sharing.
    
    .PARAMETER EnableInternetConnectionSharing
        Enable Internet Connection Sharing
    
    .PARAMETER DisableInternetConnectionSharing
        Disable Internet Connection Sharing
    
    .PARAMETER SetPwnagotchiSubnet
        Change the Internet Connection Sharing subnet to the Pwnagotchi subnet. The USB Gadget Interface IP will default to 10.0.0.1.
    
    .PARAMETER ScopeAddress
        Custom ScopeAddress (The IP Address of the USB Gadget Interface.)
    
    .EXAMPLE
        # Enable Internet Connection Sharing
        PS C:\> .\win_connection_share -EnableInternetConnectionSharing

    .EXAMPLE
        # Disable Internet Connection Sharing
        PS C:\> .\win_connection_share -DisableInternetConnectionSharing

    .EXAMPLE
        # Change the regkeys of Internet Connection Sharing to the Pwnagotchi Subnet
        PS C:\> .\win_connection_share -SetPwnagotchiSubnet

    .EXAMPLE
        # Change the regkeys of Internet Connection Sharing to the Pwnagotchi Subnet with a custom ScopeAddress (The IP Address of the USB Gadget Interface.)
        PS C:\> .\win_connection_share -SetPwnagotchiSubnet -ScopeAddress 10.0.0.10
#>

#Requires -Version 5
#Requires -RunAsAdministrator
[Cmdletbinding()]
Param (
    [switch]$EnableInternetConnectionSharing,
    [switch]$DisableInternetConnectionSharing,
    [switch]$SetPwnagotchiSubnet,
    [ipaddress]$ScopeAddress = '10.0.0.1'
)

# Load helper functions
Function Create-HNetObjects {
    <#
    .SYNOPSIS
        A helper function that does the heavy lifting with NetCfg.HNetShare
    
    .DESCRIPTION
        A helper function that does the heavy lifting with NetCfg.HNetShare. This returns a PSObject containing the `INetSharingConfigurationForINetConnection` info of 2 Adapters.
    
    .PARAMETER InternetAdaptor
        The output of Get-NetAdaptor filtered down to the 'main' uplink interface.
    
    .PARAMETER RNDISGadget
        The output of Get-NetAdaptor filtered down to the 'USB Ethernet/RNDIS Gadget' interface.
    
    .EXAMPLE
        PS> $HNetObject = Create-HNetObjects
        PS> $HNetObject
            RNDISIntConfig     InternetIntConfig
            --------------     -----------------
            System.__ComObject System.__ComObject
    #>
    [Cmdletbinding()]
    Param (
        $InternetAdaptor = $(Select-NetAdaptor -Message "Please select your main a ethernet adaptor with internet access that will be used for internet sharing."),
        $RNDISGadget = $(Select-NetAdaptor -Message "Please select your 'USB Ethernet/RNDIS Gadget' adaptor")
    )
    Begin {
        regsvr32.exe /s hnetcfg.dll
        $HNetShare = New-Object -ComObject HNetCfg.HNetShare
    }
    Process {
        if ($HNetShare.EnumEveryConnection -ne $null) {
            $InternetInt       = $HNetShare.EnumEveryConnection | Where-Object { $HNetShare.NetConnectionProps.Invoke($_).Name -eq ($InternetAdaptor).Name }
            $InternetIntConfig = $HNetShare.INetSharingConfigurationForINetConnection.Invoke($InternetInt)
            $RNDISInt          = $HNetShare.EnumEveryConnection | Where-Object { $HNetShare.NetConnectionProps.Invoke($_).Name -eq ($RNDISGadget).Name }
            $RNDISIntConfig    = $HNetShare.INetSharingConfigurationForINetConnection.Invoke($RNDISInt)
        }
    }
    End {
        Return $(New-Object -TypeName PSObject -Property @{InternetIntConfig=$InternetIntConfig;RNDISIntConfig=$RNDISIntConfig;})
    }
}
Function Enable-InternetConnectionSharing {
    <#
    .SYNOPSIS
        Enables internet connection sharing between the 'main' uplink interface and the 'USB Ethernet/RNDIS Gadget' interface.
    
    .DESCRIPTION
        Enables internet connection sharing between the 'main' uplink interface and the 'USB Ethernet/RNDIS Gadget' interface.
    
    .EXAMPLE
        PS> Enable-InternetConnectionSharing
    
    #>
    [Cmdletbinding()]
    $HNetObject = Create-HNetObjects
    $HNetObject.InternetIntConfig.EnableSharing(0)
    $HNetObject.RNDISIntConfig.EnableSharing(1)
    Write-Output "[x] Enabled Internet Connection Sharing."
}
Function Disable-InternetConnectionSharing {
    <#
    .SYNOPSIS
        Disables internet connection sharing between the 'main' uplink interface and the 'USB Ethernet/RNDIS Gadget' interface.
    
    .DESCRIPTION
        Disables internet connection sharing between the 'main' uplink interface and the 'USB Ethernet/RNDIS Gadget' interface.

    .EXAMPLE
        PS> Disable-InternetConnectionSharing
    
    #>
    [Cmdletbinding()]
    $HNetObject = $(Create-HNetObjects)
    $HNetObject.InternetIntConfig.DisableSharing()
    $HNetObject.RNDISIntConfig.DisableSharing()
    Write-Output "[x] Disabled Internet Connection Sharing."
}
Function Test-PwnagotchiSubnet {
    <#
    .SYNOPSIS
        Tests the registry for the correct ScopeAddress.
    
    .DESCRIPTION
        Tests the registry for the correct ScopeAddress. By default windows uses a 192.168.137.x subnet for Internet Connection Sharing. This value can be changed
        in the registry.
    
    .EXAMPLE
        PS> Test-PwnagotchiSubnet
        [!] By default Internet Connection Sharing uses a 192.168.137.x subnet. Run Set-PwnagotchiSubnet to ensure you and your little friend are on the same subnet.
    #>
    [Cmdletbinding()]
    $RegKeys = Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters -ErrorAction Stop
    If ($RegKeys.ScopeAddress -notmatch '10.0.0.') {
        Write-Error "By default Internet Connection Sharing uses a 192.168.137.x subnet. Run Set-PwnagotchiSubnet to ensure you and your little friend are on the same subnet." -ErrorAction Stop
    }
    If ($RegKeys.ScopeAddressBackup -notmatch '10.0.0.') {
        Write-Error "By default Internet Connection Sharing uses a 192.168.137.x subnet. Run Set-PwnagotchiSubnet to ensure you and your little friend are on the same subnet." -ErrorAction Stop
    } 
}
Function Set-PwnagotchiSubnet {
    <#
    .SYNOPSIS
        Set the registry for the correct ScopeAddress.
    
    .DESCRIPTION
        Set the registry for the correct ScopeAddress. By default windows uses a 192.168.137.x subnet for Internet Connection Sharing. This value can be changed
        in the registry. By default it will be changed to 10.0.0.1
    
    .PARAMETER ScopeAddress
        The IP address the USB Gadget interface should use.
    
    .EXAMPLE
    Set-PwnagotchiSubnet
    
    #>
    [Cmdletbinding()]
    Param (
        $ScopeAddress = '10.0.0.1'
    )
    Try {
        [void]([ipaddress]$ScopeAddress)
        [void]([byte[]] $ScopeAddress.split('.'))
    } Catch {
        Write-Error "$ScopeAddress is not a valid IP."
    }
    Try {
        Set-ItemProperty -Name ScopeAddress       -Path "HKLM:\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\" -Value $ScopeAddress -ErrorAction Stop
        Set-ItemProperty -Name ScopeAddressBackup -Path "HKLM:\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\" -Value $ScopeAddress -ErrorAction Stop
        Write-Warning "The Internet Connection Sharing subnet has been updated. A reboot of windows is required !"
    } Catch {
        $PSCmdlet.ThrowTerminatingError($PSItem)
    }
 
}

# Main Function
Function Setup-PwnagotchiNetwork {
    <#
    .SYNOPSIS
        Function to setup networking.
    
    .DESCRIPTION
        Function to setup networking. Main function calls helpers functions.
    
    .PARAMETER EnableInternetConnectionSharing
        Enable Internet Connection Sharing
    
    .PARAMETER DisableInternetConnectionSharing
        Disable Internet Connection Sharing
    
    .PARAMETER SetPwnagotchiSubnet
        Change the Internet Connection Sharing subnet to the Pwnagotchi. Defaults to 10.0.0.1.
    
    .PARAMETER ScopeAddress
        Custom ScopeAddress (the ICS ip address)
    
    .EXAMPLE
        PS> Setup-PwnagotchiNetwork -EnableInternetConnectionSharing
    
    #>
    
    Param (
        [switch]$EnableInternetConnectionSharing,
        [switch]$DisableInternetConnectionSharing,
        [switch]$SetPwnagotchiSubnet,
        $ScopeAddress = '10.0.0.1'
    )
    Begin {
        Try {
            Write-Debug "Begin"
            $ErrorSplat=@{ErrorAction="stop"}
            Write-Debug "Testing subnet"
            Try {
                Test-PwnagotchiSubnet @ErrorSplat
            } Catch {
                If ($SetPwnagotchiSubnet) {
                    Write-Debug "Setting subnet"
                    Set-PwnagotchiSubnet -ScopeAddress $ScopeAddress @ErrorSplat
                } Else {
                    Write-Error "By default Internet Connection Sharing uses a 192.168.137.x subnet. Run this script with the -SetPwnagotchiSubnet to setup the network." -ErrorAction Stop
                }
            }
        } Catch {
            $PSCmdlet.ThrowTerminatingError($PSItem)
        }
    }
    Process {
        Write-Debug "Process"
        Try {
            If ($EnableInternetConnectionSharing) {
                Write-Debug "Enable network Sharing"
                Enable-InternetConnectionSharing @ErrorSplat
            } ElseIf ($DisableInternetConnectionSharing) {
                Write-Debug "Disable network Sharing"
                Disable-InternetConnectionSharing @ErrorSplat
            }
        } Catch {
            $PSCmdlet.ThrowTerminatingError($PSItem)
        }
    }
    End {
        Write-Debug "End"
        Try {
            # Nothing to return.
        } Catch {
            $PSCmdlet.ThrowTerminatingError($PSItem)
        }
    }
}
Function Select-NetAdaptor {
    <#
    .SYNOPSIS
        A menu function to select the correct network adaptors.
    
    .DESCRIPTION
        A menu function to select the correct network adaptors.
    
    .PARAMETER Message
        Message that will be displayed during the question.
    
    #>
    
    Param (
        $Message
    )
    $Adaptors = Get-NetAdapter | Where-Object {$_.MediaConnectionState -eq 'Connected'} | Sort-Object LinkSpeed -Descending
    do { 
        Write-Host $Message
        $index = 1
        foreach ($Adaptor in $Adaptors) {
            Write-Host "[$index] $($Adaptor.Name), $($Adaptor.InterfaceDescription)"
            $index++
        }   
        $Selection = Read-Host "Number"
    } until ($Adaptors[$selection-1])
     Return $Adaptors[$selection-1]
}
# Dynamically create params for Setup-PwnagotchiNetwork function based of param input of script.
Setup-PwnagotchiNetwork @psBoundParameters
