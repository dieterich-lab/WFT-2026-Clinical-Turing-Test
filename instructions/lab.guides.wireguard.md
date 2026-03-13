# Wireguard VPN

We use wireguard as our VPN service such taht we can connect to our cluster from everywhere. Please follow the below guidelines to install wireguard on your device. During the process you have to contact our Sysadmin  <harald.wilhelmi@uni-heidelberg.de> once to get the IP adress for your wireguard configuration.

## Overview

To access the internal network of AG Dieterich remotely a VPN (virtual private network) must be setup. This is a encrypted connection between two systems, which feels as if both systems are a connected to the same local network.

This document describes a so called "road warrior" setup, where one side is a single computer (e.g. your laptop) and the other side is a firewall granting access to a whole network - in our case the Slurm cluster and the related systems.
Edit this section

## Client Setup

General Hints

The WireGuard configuration always falls into two parts:

* interface: Your local WireGuard interface. All your data goes here.
* peer: The remote partner - in our case the firewalls in AZ3.

Each of these two sides has a key pair. That consists of:

* Private Key, which is kept secret - even from the other side (GUI: only visible if you "edit" the tunnel)
* Public key, which is used to identify the party on the other end of the tunnel (GUI: shown if look at the tunnel without editing)

So there are two key pairs with four keys in total - don't mix them up.

## GUI Setup (Windows, Mac-OS)

* Download the Installer for your OS from <https://www.wireguard.com/install/>
* Check the installer with your virus scanner (e.g. usually Windows Defender).
* Run the installer
* In the WireGuard App (started also by the installer), Tunnel tab, right-click in the empty panel on the left side and select "add empty tunnel" (tbc - German: "Einen leeren Tunnel hinzufügen").
* Give the new tunnel a name an save it.
* Send the your public key displayed to Harald.
* Get an IP address from <harald.wilhelmi@uni-heidelberg.de>
* Edit the tunnel so that it looks like this. Don't change the PublicKey or Endpoint in the Peer part:

```
    [Interface]
    PrivateKey = <do NOT change>
    Address = <IP address from Harald>
    ListenPort = 51820
    MTU = 1280
    DNS = 10.250.140.21

    [Peer]
    PublicKey = hP45m/EB6vd8kuU9ii1VdyZCrJ5XZ1XPPcT5eVfkHUI=
    Endpoint = 129.206.148.250:51820
    AllowedIPs = 129.206.148.251/32,10.250.135.0/24,10.250.140.0/24,10.250.100.0/24
```

* Save
* Select the Tunnel and press the "Activate" button.

Use the WireGuard App to activate/deactivate the tunnel as needed.

<!--
## Command Line (Linux)

### Basic Setup

* Install WireGuard (see https://www.wireguard.com/install/) and the package ifupdown.
* Generate a secret key in a temporary file and get the public key:

```
    $ umask 077
    $ wg genkey > secret_key.txt
    $ wg pubkey < secret_key.txt
```

* Send the **public** key to Harald.
* Get your IP from Harald.
* Create a configuration file for your WireGuard interface /etc/wireguard/interface_wg0.conf:

```
    # AG Dieterich

    [Interface]
    PrivateKey = <your secret key goes here>
    ListenPort = 51820

    [Peer]
    PublicKey = hP45m/EB6vd8kuU9ii1VdyZCrJ5XZ1XPPcT5eVfkHUI=
    Endpoint = 129.206.148.250:51820
    AllowedIPs = 129.206.148.251/32,10.250.135.0/24,10.250.140.0/24,10.250.100.0/24
```

* Define a interface with right properties.
    * For Debian or Ubuntu you may just add the following lines to /etc/network/interfaces, inserting your IP at the right spot:

```
        iface wg0 inet static
                address <your IP goes here>/24
                mtu 1280
                pre-up ip link add wg0 type wireguard
                pre-up wg setconf wg0 /etc/wireguard/interface_wg0.conf
                post-up ip route add 129.206.148.251/32 dev wg0 metric 900
                post-up ip route add 10.250.135.0/24 dev wg0 metric 900
                post-up ip route add 10.250.140.0/24 dev wg0 metric 900
                post-up ip route add 10.250.100.0/24 dev wg0 metric 900
                post-down ip link del wg0
```

    * If your ISP is Vodafone check check the known issues - you may have to add a MTU setting here.
* Start that interface (on some Ubuntus ifup is in /sbin instead of /usr/sbin ...):

```
    $ sudo /usr/sbin/ifup wg0
```

You may either automatically start the interface at boot time (e.g. by adding the line 'auto wg0' to /etc/network/interfaces). For improved security just start the interface when needed:

```
$ sudo /usr/sbin/ifup wg0   # or /sbin/ifup on some systems
$ ssh <your LDAP user>@10.250.135.104
...
$ sudo /usr/sbin/ifdown wg0
```

## Configuring DNS

The '.internal' domains will not work with the setup as shown above. As a quick workaround/test you may install 'host' command (package bind9-host) and do the lookup manually, e.g.:

```
$ host jenkins.internal 10.250.140.21
Using domain server:
Name: 10.250.140.21
Address: 10.250.140.21#53
Aliases: 

jenkins.internal has address 10.250.135.21
```

To finally fix the issue you need to ensure that your /etc/resolv.conf looks like this while using WireGuard:

```
search dieterichlab.org internal
nameserver 10.250.140.21
```

Unfortunately the file is generated by e.g. Network Manager or System-D. As a result manual modifications will be overwritten. So far we have identified the following case:

* **systemd-resolved**: If your system has /usr/bin/resolvectl installed, you are using systemd-resolved and you can use this command to configure name resolution on your tunnel interface. Juat add this line to your interface configuration just after the other 'post-up' statements (needs verification!):

```
        post-up resolvectl dns wg0 10.250.140.21
```

* **NetworkManager**: Most Linux systems use NetworkManager - in doubt check if the command nmcli exists. In this case you may use this script and install it as e.g. /usr/local/bin/switch_dieterichlab_dns:

```
    #!/usr/bin/sh

    prefix=''
    network_device=$(nmcli | grep interface: | cut -d ':' -f 2 | tr -d ' \t' | head -1)

    case $1 in
        on) ;;
        off) prefix='-' ;;
        *)
            myself=$(basename $0)
            echo "Usage: $myself on|off" >&2
            exit
            ;;
    esac

    nmcli dev modify $network_device ${prefix}ipv4.dns 10.250.140.21
```

    Don't forget to make it executable:

```
    chmod 755 /usr/local/bin/switch_dieterichlab_dns
```

    Now you can add this lines to your interface definition in /etc/network/interfaces just after the other 'post-up' lines:

```
            post-up /usr/local/bin/switch_dieterichlab_dns on
            pre-down /usr/local/bin/switch_dieterichlab_dns off
```

## Variants

The suggested configurations above configure the port used on your side (ListenPort = 51820). This fixes the port to be used on your side. In general this is not necessary. Sometimes it helps to have a fixed port for debugging or defining firewall rules. Feel free to drop this line or adapt it to your needs.

If you are working behind a firewall, the firewall needs to allow UDP traffic from your system, your port to 129.206.148.250, port 51820 and back. NAT (aka IP Masquerading) does not matter, even if this remaps the port number.

However address collisions between the local network addresses on your side and ob the server side must be avoided (for most people only 10.250.135.0/24 matters). You may strip the "AllowedIps" to just the IPs you really need. In the Linux case don't forget to also adapt the "ip route" commands accordingly.

## Troubleshooting Hints

Top Configuration Mistakes

1. Confuse the public key in the configuration! Double check that the key in [peer] section is the right one: hP45m/EB6vd8kuU9ii1VdyZCrJ5XZ1XPPcT5eVfkHUI=
2. Trying to route to the firewall through the tunnel. Check:

```
    $ ip r g 129.206.148.250
```

    If that reports your WireGuard interface (wg0), make sure that this IP is excluded from your tunnel routing and the AllowedIPs. On Windows and Mac-OS only check the AllowedIPs.

3. "X.internal" does not work with WireGuard

To resolve the ".internal" domain one needs to use our internal DNS server 10.250.140.21. Presently that service is new and little experience exists how to do this exactly.
The following cases are known to exist:

* **WireGuard GUI**: If you are using a GUI to start/stop your WireGuard tunnel just try to add the DNS line to your configuration as schon in GUI setup example.
* **Command line setup**: Basically you need to use the above DNS server while the tunnel is up and reset the settings when the tunnel goes down. This could be done by patching the /etc/resolv.conf
    manually. Unfortunately this changes will be overwritten automatically sooner or later. See the remarks above.

Tracking down issues:

* Try the 'host' or 'nslookup' command to try to access the name server, e.g.:

```
    host -v cluster.internal
```

    * Is 10.250.140.21 reported as name server? If not the configuration that tries to set the name server did not work. Check e.g. the DNS line in your WireGuard configuration.
    * The server 10.250.140.21 is reported, but the request timeouts: Check if your AllowedIPs configuration item has 10.250.140.0/24. In the command line case also check the for it in the 'post-up ip route' statements.
    * If you get the correct response by this check, consider the possibility that there is a caching issue with your software:
        * Browsers cache DNS. In case of Firefox the cache can be cleared by entering about:networking#dns as URL and selecting the right button.
        * Other software may need a restart to pick up the change.
        * On Linux a number of services act as caches for DNS. This includes at least systemd-resovled and nscd. Each of them has it's own method to clear the case.

## Known issues

Connections may break after inactivity

WireGuard itself is self-healing and able to roam. If you are behind a NAT firewall ("IP masquerading") the that firewall may "forget" after some time of inactivity how to translate your IP and ports when talking to the our firewall. As a result the our firewall may fail to send data back to you. Once you use the tunnel again, it will be immediately revived, but maybe to late to prevent a timeout. To avoid this issue, one may add this option:

```
[peer]
...
PersistentKeepalive = 600
```

The precise settings depend on the firewall and the application.

### Mac-OS: Unwanted extra default route appears in the routing table and blocks access to external sites

As a workaround above remarks about the Mac-OS setup and remove any unneeded entries in the 'allowed ips'.

### Mac-OS: Interface breaks if it is taken down via the Network panel instead of the WIreGuard App

As a workaround reboot and don't do it again.

### MTU size issues with some provioders (Kabel Deutschland?)

(This workaround is now part of the recommended default configuration.)

There is a theory that in some setups (Kabel Deutschland as ISP?) there may be a problem that large packages are dropped. Such problems may be avoided by enforcing a lower MTU (maximum transfer unit = package size). Depending on the client you use that setting must be supplied at various spots:

* Basic wg command (as suggested above for for Linux systems): Add "mtu 1280" to the interface definition in /etc/network.
* wg-quick command and most likely the GUIs: Add "MTU = 1280" to the '[interface] section of the configuration.

Minor mistakes with this setting can lead to wg0 device, for which both 'ifup' and 'ifdown' will fail. In this situation just delete the device:

```
sudo ip link delete wg0
```

### Check the Tunnel Status

To check the tunnel status do this:

```
$ sudo wg
interface: wg0
  public key: ...
  private key: (hidden)
  listening port: 51820

peer: hP45m/EB6vd8kuU9ii1VdyZCrJ5XZ1XPPcT5eVfkHUI=
  endpoint: 129.206.148.250:51820
  allowed ips: 172.23.13.0/24, 10.0.10.0/24, 129.206.148.0/24
  latest handshake: 18 seconds ago
  transfer: 693.34 KiB received, 7.42 MiB sent
```

If no interface is displayed, the tunnel is not started. If the 'latest handshake' line is missing WireGuard failed to talk with our firewall.

### Check Network Connection

On Linux and some other you can install traceroute. Depending on the version of the command the following options may not be available or or named different. We want to use UDP packages (-U) on port 51820 (-p 51820) and supress name resolution (-n):

```
traceroute -n -U --mtu -p 51820 129.206.148.250
```

This will give you a list of gateways your packages pass through successfully. This list may be empty ("1 * * *") in serval cases:

* There is no gateway because you are in Heidelberg, AZ3, connected to the URZ net
* You by-pass all gateways because you are also using IPSec (Cisco Connect Anyware) - don't do this.
* Your firewall ("personal firewall"on your machine or just the next hop) catches the packages and drops them.
* Otherwise you will see the gateways the packages pass through before they hit some firewall.

### Check Routing with Linux

You may also check over which interface WireGuard tries to connect the server. In Linux this can be done with "ip route get":

```
$ ip r g 129.206.148.250
129.206.148.250 dev enx747827ea92e1 src 129.206.148.65 uid 1000 
    cache 
```

For obvious reasons WireGuard should not try to route the traffic for the tunnel end point through the tunnel. Other traffic should go that way:

```
$ host cluster.internal
cluster.internal is an alias for slurm-c-mk1-1a.internal.
slurm-c-mk1-1a.internal has address 10.250.135.104
$ ip r g 10.250.135.104
10.250.135.104 via 10.250.100.1 dev enx747827ea92e1 src 10.250.100.45 uid 1000 
    cache 
```

### Check routing with Other Operating Systems
On other operating systems you may check the routing table:

```
$ netstat -rn
```

Now meditate deeply:

* The route with the longest prefix match wins (129.206.148.250/32 is better than 129.206.148.0/24)
* If multiple route for the same destination exist, the one with the lowest cost (metric) is preferred.

### Advanced Uses

#### Piercing Firewalls

Our VPN allows also to route traffic to external addresses through the tunnel.
Sometimes that may be used to bypass poorly configured firewalls. To do so, try that:

* Check if WireGuard works from your current network location (e.g. start it and try to connect to the cluster).
    * If that does not work - bad luck - forget it. Else continue.
* Identify the IP addresses you want to access through the tunnel. E.g. email via URZ:

```
        $ host imap.urz.uni-heidelberg.de
        imap.urz.uni-heidelberg.de has address 129.206.100.176
        imap.urz.uni-heidelberg.de has address 129.206.100.98
        $ host mail.urz.uni-heidelberg.de
        mail.urz.uni-heidelberg.de is an alias for mail01.uni-heidelberg.de.
        mail01.uni-heidelberg.de has address 129.206.100.252
```

    * So it is 129.206.100.0/24!
* Add that to AllowedIPs of your tunnel and - if you don't have a GUI - to your routing configuration.
* Stop/start the tunnel.
--->
