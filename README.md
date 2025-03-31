# bridgeipelago

Discord bridge for Archipelago in python

[Discord Link](https://discord.gg/5v9P3qNPXp)

## Setup:
See the [SETUP GUIDE](docs/setup.md)

## Funtionality:

### Core
This bot will monitor and track progress as you play through your Archipelago run.
This allows for some fun stats to be collected, logging from the bot on item checks that are found, and death notices from DeathLink players.

When a check is found or a deathlink is received, it'll output the check in a discord channel.

```
Examples:
An item for yourself:
> Quasky_SM64 found their Power Star
> Check: LLL: Boil the Big Bully

An item for someone else:
> Quasky_SM64 sent Lens of Truth to Quasky_OOT
> Check: LLL: Bully the Bullies

When someone with deathlink dies, it'll shame them in this channel.
> Deathlink received from: Quasky_OOT
```

What this bot will NOT do:
 - DM / ping you without consent
 - Find items for you
 - Give hints
 - Find the reason the children of this world have forgotten the meaning of Christmas

---
### Ketchmeup
You can also ask the bot to DM you all the items you've gained since last asking him.
(See the registration below)

**IMPORTANT NOTES:**
- This will send you EVERYTHING you've registered for since last asking. So even as you're playing and someone sends you an item, it'll still appear in the queue to be sent to you. (as the bot has no idea if you're playing or not)
- The bot will NOT log items you give to your own game. You're expected to remember what you find for yourself
- However the bot only understands slots. So if you're playing two games, the bot just assumes the other game is someone else and logs it. While ignoring the checks from your own game.

```
Example:
You         || Item                         || Sender      || Location
Quasky_OOT2 || Piece of Heart               || Quasky_OOT4 || Gerudo Training Ground Near Scarecrow Chest
Quasky_OOT2 || Rupees (20)                  || Quasky_OOT4 || Ganons Castle Shadow Trial Front Chest
Quasky_OOT2 || Bow                          || Quasky_OOT4 || Ganons Tower Boss Key Chest
Quasky_OOT2 || Gold Skulltula Token         || Quasky_OOT4 || Sheik at Colossus
Quasky_OOT2 || Rupees (200)                 || Quasky_OOT4 || KF Midos Bottom Left Chest
Quasky_OOT2 || Gold Skulltula Token         || Quasky_OOT4 || KF Shop Item 6
```
Hopefully that makes sense.

---
---

## Commands

|Player Commands|Description|
|---|---|
|$register \<slot>|Adds the slot provided to the user's registration file
|$clearreg|Clears the user's registration file|
|$ketchmeup|DMs the user all checks in their ItemQueue file, used to catch you up on missed checks|
|$groupcheck \<slot>|DMs the user all checks in the slot's ItemQueue file, used to catch up on group games|
|$hints|DMs the hinted items for a player's registered slots|
|$deathcount|Scans the deathlog and tallies up the current deathcount for each slot|
|$checkcount|Fetches the current Arch server's progress in simple txt format|

|Debug Commands|Description|
|---|---|
|$ArchInfo|\[CONSOLE] General bot details for debugging .env tables^|

**\[^] DebugMode only commands**

**\[^] DebugMode can expose unintended system information. Use with care.**

## Configs
|Key|Description|
|---|---|
|**Discord Config**||
|DiscordToken|Your Discord Bot's token|
|DiscordBroadcastChannel|Discord Channel ID for live-check purposes|
|DiscordAlertUserID|Discord User/Group ID for yelling about issues%|
|DiscordDebugChannel|Discord channel ID for debug purposes|
|**Archipelago Config**||
|ArchipelagoServer|The URL of the Archipelago server you'd like to connect to|
|ArchipelagoPort|The port of the Archipelago server you'd like to connect to|
|ArchipelagoBotSlot|The name of the slot you'd like the bot to use when connecting to archipelago|
|ArchipelagoTrackerURL|URL of the tracker you'd like to query|
|ArchipelagoServerURL|URL of the server you'd like to query|
|**Item Filter Config**||
|BotItemSpoilTraps|The Bot will spoil traps by posting them in chat and ketchmeup&|
|BotItemFilterLevel|Sets the bot filter level 0 - 1 - 2, to exclude items from discord posts&|
||All items are still be queued for ketchmeup|
||2 - Only Logical Progression Items|
||1 - Logical + Useful items|
||0 - Logical + Useful + Normal items|
|**Advanced Config**||
|LoggingDirectory|Directory of the bot's own logs*|
|PlayerRegistrationDirectory|Directory of the Player Registration Mappings*|
|PlayerItemQueueDirectory|Directory that stores player item queues*|
|ArchipelagoDataDirectory|Directory for the Archipelago data packages*|
|JoinMessage|A custom join message (console only) for the bot|
|AutomaticSetup|Automaticly starts background processes when bot is turned on|
|DebugMode|Enables extra debug chat/bot options^|

**\[%] For group IDs, ensure the '&' character is at the beggining of the ID**

**\[&] Items will still be logged in the BotLog**

**\[*] Ensure directories end in a /**

**\[*] These should be four diffrent directories, all these logs in the same place will break the bot.**

**\[^] DebugMode can expose unintended system information. Use with care.**


---
---

### Special Thanks

Thank you to the people who encourged me to pour my time into this bot. Specificaly the Zajcats.

Thank you to Rainwave Discord community to help with a private beta and bugfixing.

Thank you to the Archipelago Community for making an amazing platform for the world to use.
