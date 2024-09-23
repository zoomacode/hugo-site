---
title: "Want to be connected? Think twice."
date: 2024-03-02T13:19:20-07:00
draft: false
author: Anton Golubtsov
summary:
tags:
    - thoughts
    - big brother
    - resilience
---

_In the last few years companies try to connect everything to the internet and make everything be software defined from door bells, and photo cameras to cars. There are a few bad things about it._

These days every teeny-tiny piece of technology tries to be connected to the internet. This is usually sold by large, and not some large companies as some sort of convince so you can control everything from everywhere. The approach has its pluses but it also has its minuses. The shiny technological all connected future does not seem to me as appealing as we are told.

Availability. The idea of IoT or everything needs to be connected to the internet goes to the extreme when a simple device or functionality which usually does not require access to the internet becomes 100% dependent on the internet availability or availability of an external service. You can lose all your smart home infrastructure with a failure of a single data center a thousand miles away from you like it happened to the Ring doorbells when one of AWS regions went down. In my place I have a few Alexa, Ring cameras, and smart plugs all them are useless without the internet.

If all those small devices of your are not a large concern since they just adds a bit of inconvenience when they are broken. Then a car which loses its navigation without the internet when you are driving through unfamiliar country is much less of the fun. Believe me, my Tesla is not very fun to drive when you go to a national park with very patchy internet availability. My previous not so smart Subaru was much better on that front with connection to the internet but with offline maps and a satellite radio.

Privacy and Security. Your always connected device is another vector of attack on your privacy or home infrastructure. If major brands take security and privacy more seriously, then smaller or noname brands are less cautious in that regard. Here are two examples ~[Wyze cameras leak footage to strangers for 2nd time in 5 months](https://arstechnica.com/gadgets/2024/02/wyze-cameras-gave-13000-people-unauthorized-views-of-strangers-homes/)~ and ~[Vulnerabilities on Bosch Rexroth Nutrunners May Be Abused to Stop Production Lines, Tamper with Safety-Critical Tightenings](https://www.nozominetworks.com/blog/vulnerabilities-on-bosch-rexroth-nutrunners)~. Besides an always connected device and be a proxy for other attacks. I bought that smart plugs from small brands routinely receive security updates like in this case: ~[PSA: time to recycle your old Wemo smart plugs](https://www.theverge.com/2023/5/16/23725290/wemo-smart-plug-v2-smart-home-security-vulnerability)~. There are ways to isolate those devices and reduce the blast radius but most of the people are not aware of those.

An illusion of ownership. All devices which 100% relies on the accessibility of the internet for their smartness are just partly yours. You can lost your devices as soon as the internet is down, or somebody decides that you are no longer their beloved customer and your account must be locked. Or if the manufacturer decides to discontinue the product you use bought.

WiFi slowdown and security concerns. This is probably the least of the concerns but the more wifi devices you have the more radio interference they create and the slower your wifi. Also if you don’t use WiFi 6 and higher, your wifi gets a little bit slower with every added devices due to WiFi 5 round robin nature of data transfer process. In addition to that WiFi 5 and lower essentially broadcasts data so any connected device can listen all traffic going from and to all devices even if you blocked cross device communication by the firewall. See: [Wifi 5 vs. Wifi 6: Understanding the 10 Key Differences](https://www.spiceworks.com/tech/networking/articles/wifi-five-vs-wifi-six/).

What can we do about it? If you are considering buying a new device try to use by those which does not require the internet for all tier functionality like devices connected to a local smart home hub. If you already have devices which require functionality then try to migrate the least trust worthy ones to a dedicated wifi network, many wifi routers allow to create multiple networks. Also try to limit cross device communication, for example, the devices on that new wifi network should not be able to talk to devices on other networks or between each other. There are of course exceptions. For instructions try to teach for “IoT WiFi Setup” or “IoT dedicated WiFi” on YouTube.

_Originally posted here:_ https://antongolubtsov.substack.com/p/want-to-be-connected-think-twice
