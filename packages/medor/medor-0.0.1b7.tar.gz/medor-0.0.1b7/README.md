# 🐕 medor

<p align="center">
  <img src="https://raw.githubusercontent.com/balestek/medor/master/media/medor.png">
</p>

What _medor_'s master can say about him:
> _medor_ is a good dog. Provided you send him far enough, he can come back with a juicy bone 🦴

Medor is an OSINT (Open Source Intelligence) tool that enables you to discover the IP address of a WordPress site, even if it's obscured by a WAF (Web Application Firewall) or located within the darknet (onion services).
It requests xmlrpc.php to get the IP behind the WAF thanks to a webhook provider.

<p align="center">
  <img width="600px" src="https://raw.githubusercontent.com/balestek/medor/master/media/medor.py.png">
</p>

It requires several kibbles to work:
+ a WordPress website with an unsecured xmlrpc.php
+ a post from the WordPress website (not a page!)

_medor_ comes with few features:
+ [X] it works with the domain, the website url or a wp post
+ [x] it can find a blog post with WordPress REST API or the feed
+ [X] it updates and rotates user-agents per request
+ [x] a proxy can be used
+ [X] tor support for .onion and as a proxy
+ [x] it can check if a website is built with WordPress
+ [X] option to customize the xmlrpc response webhook URL
+ [ ] _todo : an optional flask server to handle the xmlrpc.php response_
+ [ ] _todo : use list of proxies with random selection per request_
+ [ ] _todo : check an imported list of domains, hosts or url_

## Installation

### pipx
```bash
pipx install medor
```

### pipenv
```bash
pipenv install medor
```

### pip
```bash
pip install medor
```

## Usage



### Basic usage

The command to find the IP address associated with a particular item is `find`, followed by the item you want to investigate (such as a WordPress domain, website URL, or post URL), and the type of the item (`-t` or `--item-type=`, followed by `domain`, `site`, or `post`). The default item type is `domain`.

#### With a domain
For example, to find the IP address associated with the domain `example.com`, you would use the following command:

```bash
medor find website.com # Default item-type is domain, no need to specify it
# or
medor find website.com --item-type=domain
# or
medor find website.com -t domain
```
#### With a website url

```bash
medor find https://www.website.com --item-type=site
# or
medor find https://www.website.com -t site
```

#### With a post url (not a page url)

```bash
medor find https://www.website.com/a-blog-post/ --item-type=post
# or
medor find https://www.website.com/a-blog-post/ -t post
```

### Proxy

#### With a single proxy

A proxy can be useful.

Proxy format should be protocol://user.password@IP:port if you use authentication or 
protocol://IP:port if not. The optional argument is `--proxy=yourproxy` or `-p yourproxy`.

Allowed protocols : 
- http
- https
- socks5(h). _medor_ provides socks5h by default, so you have to use socks5:// and not socks5h://.

```bash
medor find website.com -p http://user.password@255.255.255.255:8080
# or
medor find https://www.website.com --item-type=site --proxy=socks5://user.password@255.255.255.255:6154
```

### Webhook

By default, _medor_ uses a new webhook from webhook.site ([see credits](#external-webhook-service)) but you can use another service or your own with the option `--webhook=` or `-w` followed by the webhook URL.

```bash
medor find website.com --webhook=https://website.com/webhook/kjqh4sfkq4sj5h5f
# or
medor find https://www.website.com -t site -w https://website.com/webhook/kjqh4sfkq4sj5h5f
```

### Darknet / Onion Services

First, you need to install the Tor daemon, also known as little-t Tor, and set up _medor_ to work with it (see below).

To investigate a .onion website, the process is similar to that for a normal website, but you need to include the `-o` or `--onion` option. Note that it does not work with the `--proxy=` option.

After tor starts, _medor_ requests a new tor identity.

The settings for Tor are as fol
lows: the tor port is 52158 and the controller port is 9051.

```bash
medor find rtfjdnrppk7yj0424wa5i1hc6chq4nj6p3w7tu2q5qh47fmf6pi3.onion -o
# or
medor find http://rtfjdnrppk7yj0424wa5i1hc3chq4nj6p3w7tu2q5qh47fmf6pi3.onion --item-type=site --onion
```

#### Install tor

#### Windows

1. Download Tor

Download the Tor Expert Bundle for your Windows architecture from the following link: https://www.torproject.org/download/tor/.

2. Extract the archive

Extract the archive to a convenient location on your computer, such as `C:\tor\`.

3. Register your settings in _medor_

```bash
medor tor_setup
```

First you will be prompted a new password to connect _medor_ to tor. 
The password is only needed here. You don't have to remember it.

Then you will be prompted to enter the full path of the tor.exe you extracted in the previous step (e.g. `C:\tor\tor.exe`)

You're ready to use _medor_ to investigate .onion WordPress websites.

##### Linux

##### 1. Set tor repo and install tor

You need to set the tor package repository to obtain the latest version. This is important for security reasons.

Instructions for installing Tor can be found here: 
https://community.torproject.org/onion-services/setup/install/

After Tor installation, test it by opening a terminal and using the command `tor`. If Tor launches correctly, close the terminal.
##### 2. Register your settings in _medor_

```bash
medor tor_setup
```
First, you will be prompted to enter a new password to connect _medor_ to Tor. This password is only required at this stage and does not need to be memorized.

Next, you will be asked to input the full path of the tor binary that you installed in the previous step. For example, for Ubuntu/Debian, it could be `/usr/bin/tor`, or simply `tor` works as well.

Now, you're ready to use _medor_ to investigate .onion WordPress websites.

### Add-on

#### WP Check

_medor_ can check if a website is built with WordPress. It can be easily checked manually, but it can be useful for next _medor_ features. It checks 11 signatures. It's not 100% accurate, there can be false positives (in case of redirections for example).

The argument is `wp_check` and it works with the website url only (e.g. https://www.website.com). Proxy and onion options are available as well.

```bash
medor wp_check https://www.website.com
# or
medor wp_check https://www.website.com -p socks5://user.password@255.255.255.255:6884
# or
medor wp_check http://rtfjdnrppk7yj0424wa5i1hc3chq4nj6p3w7tu2q5qh47fmf6pi3.onion -onion
```

### Credits

Strongly [inspired by Dan Nemec's post](https://blog.nem.ec/2020/01/22/discover-cloudflare-wordpress-ip/).

#### Requirements

```
httpx and httpx[socks]
brotlipy
stem
halo
colorama
docopt
lxml
beautifulsoup4
validators
pwinput
```

#### External webhook service

[![https://webhook.site](https://raw.githubusercontent.com/balestek/medor/master/media/Webhook.site.png "https://webhook.site")](https://webhook.site)


_medor_ utilizes the excellent webhook service provided by [Simon Fredsted's webhook.site](https://webhook.site). If you require a webhook service with a multitude of features, consider using it.

#### License
GPLv3
