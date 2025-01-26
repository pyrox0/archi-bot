#Bridgeipelago v0.x
#A project made with love from the Zajcats

#Core Dependencies
from discord.ext import tasks
import discord
import http.client
import time
import os
import glob
from dotenv import load_dotenv
import numpy as np
import random
import json

#Scrape Dependencies
import requests
from bs4 import BeautifulSoup

#Graphing Dependencies
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

#.env Config Setup + Metadata
load_dotenv()
DiscordToken = os.getenv('DiscordToken')
DiscordBroadcastChannel = int(os.getenv('DiscordBroadcastChannel'))
DiscordAlertUserID = os.getenv('DiscordAlertUserID')
ArchHost = os.getenv('ArchipelagoServer')
ArchPort = os.getenv('ArchipelagoPort')
ArchLogFiles = os.getcwd() + os.getenv('ArchipelagoClientLogs')
ArchTrackerURL = os.getenv('ArchipelagoTrackerURL')
ArchServerURL = os.getenv('ArchipelagoServerURL')
LoggingDirectory = os.getcwd() + os.getenv('LoggingDirectory')
RegistrationDirectory = os.getcwd() + os.getenv('PlayerRegistrationDirectory')
ItemQueueDirectory = os.getcwd() + os.getenv('PlayerItemQueueDirectory')
JoinMessage = os.getenv('JoinMessage')
DebugMode = os.getenv('DebugMode')
DiscordDebugChannel = int(os.getenv('DiscordDebugChannel'))
AutomaticSetup = os.getenv('AutomaticSetup')

# Metadata
ArchInfo = ArchHost + ':' + ArchPort
OutputFileLocation = LoggingDirectory + 'BotLog.txt'
DeathFileLocation = LoggingDirectory + 'DeathLog.txt'
DeathTimecodeLocation = LoggingDirectory + 'DeathTimecode.txt'
DeathPlotLocation = LoggingDirectory + 'DeathPlot.png'
CheckPlotLocation = LoggingDirectory + 'CheckPlot.png'


# Global Variable Declaration
ActivePlayers = []

## Active Player Population
page = requests.get(ArchTrackerURL)
soup = BeautifulSoup(page.content, "html.parser")
tables = soup.find("table",id="checks-table")
for slots in tables.find_all('tbody'):
    rows = slots.find_all('tr')
for row in rows:
    ActivePlayers.append((row.find_all('td')[1].text).strip())

# Archipleago Log File Assocication
ArchLogFiles = ArchLogFiles + "*.txt"
list_of_files = glob.glob(ArchLogFiles)
latest_file = max(list_of_files, key=os.path.getmtime)

# Discord Bot Initialization
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

#Logfile Initialization. We need to make sure the log files exist before we start writing to them.
l = open(DeathFileLocation, "a")
l.close()

l = open(OutputFileLocation, "a")
l.close()

l = open(DeathTimecodeLocation, "a")
l.close()


@client.event
async def on_ready():
    print(JoinMessage," - ", client.user)
    global ChannelLock
    ChannelLock = client.get_channel(DiscordBroadcastChannel)
    await ChannelLock.send('Bot connected. Battle control - Online.')
    global DebugLock
    DebugLock = client.get_channel(DiscordDebugChannel)
    await DebugLock.send('Bot connected. Debug control - Online.')
    if AutomaticSetup == 'true':
        await SetupFileRead()

@client.event
async def on_message(message):
    try:
        if message.author == client.user:
            return
        
        #Universal special character replacment.
        message.content = message.content.replace("’","'")

        DebugMode = os.getenv('DebugMode')
        if(DebugMode == "true"):
            print(message.content, " - ", message.author, " - ", message.channel)

        #=== CORE COMMANDS ===#
        # Starts background processes
        if message.content.startswith('$connect'):
            await SetupFileRead()

        # Stops background processes
        if message.content.startswith('$disconnect'):
            await message.channel.send('Channel disconnected. Battle control - Offline.')
            background_task.cancel()
            reassurance.cancel()

        #=== PLAYER COMMANDS ===#
        # Registers user for a alot in Archipelago
        if message.content.startswith('$register'):
            ArchSlot = message.content
            ArchSlot = ArchSlot.replace("$register ","")
            Sender = str(message.author)
            RegistrationFile = RegistrationDirectory + Sender + ".csv"
            RegistrationContent = ArchSlot + "\n"

            # Generate the Registration File if it doesn't exist
            o = open(RegistrationFile, "a")
            o.close()

            # Get contents of the registration file and save it to 'line'
            o = open(RegistrationFile, "r")
            line = o.read()
            o.close()

            # Check the registration file for ArchSlot, if they are not registered; do so. If they already are; tell them.
            if not ArchSlot in line:
                await message.channel.send("Registering " + Sender + " for slot " + ArchSlot)
                o = open(RegistrationFile, "a")
                o.write(RegistrationContent)
                o.close()
            else:
                await message.channel.send("You're already registered for that slot.")

        # Clears registration file for user
        if message.content.startswith('$clearreg'):
            Sender = str(message.author)
            RegistrationFile = RegistrationDirectory + Sender + ".csv"
            os.remove(RegistrationFile)

        # Opens a discord DM with the user, and fires off the Katchmeup process
        if message.content.startswith('$ketchmeup'):
            if (message.author).dm_channel == "None":
                print("No DM channel")
                print(message.author.dm_channel)
                await message.author.dm_channel.send("A NEW FIGHTER APPROCHING!!")
            else:
                await message.author.create_dm()
                await KetchupUser(message.author)

        if message.content.startswith('$groupcheck'):
                await message.author.create_dm()
                await GroupCheck(message.author, message.content)

        if message.content.startswith('$hints'):
            await message.author.create_dm()
            await HintList(message.author)

        # Runs the deathcounter message process
        if message.content.startswith('$deathcount'):
            await CountDeaths()

        if message.content.startswith('$checkcount'):
            await CheckCount()

        if message.content.startswith('$checkgraph'):
            await CheckGraph()

        #=== SPECIAL COMMANDS ===#
        # Sometimes we all need to hear it :)
        if message.content.startswith('$ILoveYou'):
            await message.channel.send("Thank you.  You make a difference in this world. :)")

        # Ping! Pong!
        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

        # Provides debug paths
        if message.content.startswith('$ArchInfo'):
            DebugMode = os.getenv('DebugMode')
            if(DebugMode == "true"):
                print(DiscordBroadcastChannel)
                print(DiscordAlertUserID)
                print(ArchInfo)
                print(ArchTrackerURL)
                print(ArchServerURL)
                print(ArchLogFiles)
                print(latest_file)
                print(OutputFileLocation)
                print(DeathFileLocation)
                print(DeathTimecodeLocation)
                print(RegistrationDirectory)
                print(ItemQueueDirectory)
                print(JoinMessage)
                print(DiscordDebugChannel)
                print(AutomaticSetup)
                print(DebugMode)
                print(ChannelLock)
                print(DebugLock)
            else:
                await message.channel.send("Debug Mode is disabled.")

    except:
        await DebugLock.send('ERROR IN CORE_MESSAGE_READ')

# Sets up the pointer for the logfile, then starts background processes.
async def SetupFileRead():
    try:
        with open(latest_file, 'r') as fp:
            global EndOfFile
            EndOfFile = len(fp.readlines())
            print('Total Number of lines:', EndOfFile)  
        background_task.start()
        reassurance.start()
        #KeepAlive.start()
        CheckArchHost.start()
    except:
        await DebugLock.send('ERROR IN SETUPFILEREAD')

@tasks.loop(seconds=5400)
async def KeepAlive():
    serverpage = requests.get(ArchServerURL)
    print("PING PONG Server")


# Because Quasky is paranoid, reassures you that the bot is running.
@tasks.loop(seconds=np.random.randint(60,300))
async def reassurance():
    quotes = [
    "I'm being a good boy over here!",
    "Don't worry dad, I'm still workin' away!",
    "I'M WORKING, GOSH",
    "The birds planted a bomb in the forest...",
    "I still hear the voices...they never leave.",
    "Yep, still working!",
    "God died in 1737, we've been on our own ever since.",
    "I've got this! Working away!",
    "*Bzzzt* WORKING *Bzzzt*"
    ]
    print(random.choice(quotes))


# Main background loop
## Scans the log file every two seconds and processes recceived item checks
@tasks.loop(seconds=2)
async def background_task():
    try:
        global EndOfFile
        with open(latest_file,"r") as f:
            for _ in range(EndOfFile):
               next(f)
            for line in f:

                #If the line doesn't begin with a [ then skip it! It's just a trace or something we don't need/care about
                if not line[0] == "[":
                    continue

                #Gathers The timestamp for logging
                timecodecore = line.split("]: ")[0]
                timecodecore = timecodecore.split("at ")[1]
                #Breaks time away from date
                timecodedate = timecodecore.split(" ")[0]
                timecodetime = timecodecore.split(" ")[1]

                #Breaks apart datestamp
                timecode_year = timecodedate.split("-")[0]
                timecode_month = timecodedate.split("-")[1]
                timecode_day = timecodedate.split("-")[2]

                #Breaks apart timestamp
                timecodetime = timecodetime.split(",")[0]
                timecode_hours = timecodetime.split(":")[0]
                timecode_min = timecodetime.split(":")[1]
                timecode_sec = timecodetime.split(":")[2]

                #Buids the timecode
                timecode = timecode_day +"||"+ timecode_month +"||"+ timecode_year +"||"+ timecode_hours +"||"+ timecode_min +"||"+ timecode_sec

                # For item checks, the log file will output a "FileLog" string that is parced for content (Thanks P2Ready)
                if "FileLog" in line:

                    #Splits the check from the Timecode string
                    entry = line.split("]: ")[1]
                    print(entry)

                    #Let's massage that there string
                    ### This already needs a rework, but it works if strings behave nicely ###
                    if "sent" in entry:
                        sender = entry.split(" sent ")[0]
                        entry = entry.split(" sent ")[1] # issue if sender name has "sent" substring
                        check_temp = entry.split(" (")[-1] # issue if check name has " ("
                        check = check_temp.split(")")[0]
                        name_temp = entry.split(" to ")[-1] # issue if check has word "to"
                        name = name_temp.split(" (")[0]
                        item = entry.split(" to ")[0]
                        await ChannelLock.send(
                            "```Recipient: " + name +
                            "\nItem: " + item +
                            "\nSender: " + sender +
                            "\nCheck: " + check + "```"
                            )
                        #Sends sent item to the item queue
                        await SendItemToQueue(name,item,sender,check)

                        #Sends ItemCheck to log
                        ItemCheck = name  +"||"+ sender +"||"+ item +"||"+ check
                        LogOutput = timecode +"||"+ ItemCheck +"\n"
                        o = open(OutputFileLocation, "a")
                        o.write(LogOutput)
                        o.close()

                    if "found their" in entry:
                        await ChannelLock.send("```"+entry+"```")
                        #Sends self-check to log
                        LogOutput = timecode +"||"+ entry
                        o = open(OutputFileLocation, "a")
                        o.write(LogOutput)
                        o.close()


                # Deathlink messages are gathered and stored in the deathlog for shame purposes.
                if "DeathLink:" in line:
                    d = open(DeathTimecodeLocation, "r")
                    DLtimecode = d.read()
                    d.close()

                    if DLtimecode == timecode:
                        print("skipping death!")
                        await DebugLock.send('skipping double death!')
                    else:
                        deathentry = line.split("]: ")[1]
                        await ChannelLock.send("**"+ deathentry + "**")

                        for slot in ActivePlayers:
                            if slot in deathentry:
                                deathentry = slot + "\n"

                        #temp Deathlog for Terraria
                        if "Mami Papi don't fite" in line or "Scycral Arch2" in line or "Muscle Mommy" in line or "Mami Papi" in line:
                            deathentry = "from IRL Fishing\n"

                        #write deathlink to log
                        DeathLogOutput = timecode +"||"+ deathentry
                        o = open(DeathFileLocation, "a")
                        o.write(DeathLogOutput)
                        o.close()

                        d = open(DeathTimecodeLocation, "w")
                        d.write(timecode)
                        d.close()

        # Now we scan to the end of the file and store it so we know how far we've read thus far
        with open(latest_file, 'r') as fp:
            EndOfFile = len(fp.readlines())
    except Exception as e:
        dbmessage = "```ERROR IN BACKGROUND_TASK\n" + str(e) + "```"
        await DebugLock.send(dbmessage)

# When the user asks, catch them up on checks they're registered for
## Yoinks their registration file, scans through it, then find the related ItemQueue file to scan through 
async def KetchupUser(DMauthor):
    try:
        RegistrationFile = RegistrationDirectory + DMauthor.name + ".csv"
        if not os.path.isfile(RegistrationFile):
            await DMauthor.dm_channel.send("You've not registered for a slot : (")
        else:
            r = open(RegistrationFile,"r")
            RegistrationLines = r.readlines()
            r.close()
            for reglines in RegistrationLines:
                ItemQueueFile = ItemQueueDirectory + reglines.strip() + ".csv"
                if not os.path.isfile(ItemQueueFile):
                    await DMauthor.dm_channel.send("There are no items for " + reglines.strip() + " :/")
                    continue
                k = open(ItemQueueFile, "r")
                ItemQueueLines = k.readlines()
                k.close()
                os.remove(ItemQueueFile)

                YouWidth = 0
                ItemWidth = 0
                SenderWidth = 0
                YouArray = [0]
                ItemArray = [0]
                SenderArray = [0]

                for line in ItemQueueLines:
                    YouArray.append(len(line.split("||")[0]))
                    ItemArray.append(len(line.split("||")[1]))
                    SenderArray.append(len(line.split("||")[2]))
                
                YouArray.sort(reverse=True)
                ItemArray.sort(reverse=True)
                SenderArray.sort(reverse=True)

                YouWidth = YouArray[0]
                ItemWidth = ItemArray[0]
                SenderWidth = SenderArray[0]

                You = "You"
                Item = "Item"
                Sender = "Sender"
                Location = "Location"

                ketchupmessage = "```" + You.ljust(YouWidth) + " || " + Item.ljust(ItemWidth) + " || " + Sender.ljust(SenderWidth) + " || " + Location + "\n"
                for line in ItemQueueLines:
                    You = line.split("||")[0].strip()
                    Item = line.split("||")[1].strip()
                    Sender = line.split("||")[2].strip()
                    Location = line.split("||")[3].strip()
                    ketchupmessage = ketchupmessage + You.ljust(YouWidth) + " || " + Item.ljust(ItemWidth) + " || " + Sender.ljust(SenderWidth) + " || " + Location + "\n"
                    
                    if len(ketchupmessage) > 1900:
                        ketchupmessage = ketchupmessage + "```"
                        await DMauthor.dm_channel.send(ketchupmessage)
                        ketchupmessage = "```"
                ketchupmessage = ketchupmessage + "```"
                await DMauthor.dm_channel.send(ketchupmessage)

    except:
        await DebugLock.send('ERROR IN KETCHMEUP')

# When the user asks, catch them up on the specified game
## Yoinks the specified ItemQueue file, scans through it, then sends the contents to the user
## Does NOT delete the file, as it's assumed the other users will want to read the file as well
async def GroupCheck(DMauthor, message):
    try:
        game = message.split('$groupcheck ')
        ItemQueueFile = ItemQueueDirectory + game[1] + ".csv"
        if not os.path.isfile(ItemQueueFile):
            await DMauthor.dm_channel.send("There are no items for " + game[1] + " :/")
        else:
            k = open(ItemQueueFile, "r")
            ItemQueueLines = k.readlines()
            k.close()

            ketchupmessage = "```You || Item || Sender || Location \n"
            for line in ItemQueueLines:
                ketchupmessage = ketchupmessage + line
                if len(ketchupmessage) > 1900:
                    ketchupmessage = ketchupmessage + "```"
                    await DMauthor.dm_channel.send(ketchupmessage)
                    ketchupmessage = "```"
            ketchupmessage = ketchupmessage + "```"
            await DMauthor.dm_channel.send(ketchupmessage)
    except:
        await DebugLock.send('ERROR IN GROUPCHECK')

# Sends the received item check to the ItemQueue for the slot in question.
async def SendItemToQueue(Recipient, Item, Sender, Check):
    try:
        ItemQueueFile = ItemQueueDirectory + Recipient + ".csv"
        i = open(ItemQueueFile, "a")
        ItemWrite = Recipient + "||" + Item + "||" + Sender + "||" + Check +"\n"
        i.write(ItemWrite)
        i.close()
    except:
        await DebugLock.send('ERROR IN SENDITEMTOQUEUE')

# Counts the number of deaths written to the deathlog and outputs it in bulk to the connected discord channel
async def CountDeaths():
    try:
        d = open(DeathFileLocation,"r")
        DeathLines = d.readlines()
        d.close()
        deathdict = {}
        for deathline in DeathLines:
            DeathUser = deathline.split("||")[6]
            DeathUser = DeathUser.split("\n")[0]

            if not DeathUser in deathdict:
                deathdict[DeathUser] = 1
            else:
                deathdict[DeathUser] = deathdict[DeathUser] + 1

        deathdict = {key: value for key, value in sorted(deathdict.items())}
        deathnames = []
        deathcounts = []
        message = "**Death Counter:**\n```"
        deathkeys = deathdict.keys()
        for key in deathkeys:
            deathnames.append(str(key))
            deathcounts.append(int(deathdict[key]))
            message = message + "\n" + str(key) + ": " + str(deathdict[key])
        message = message + '```'
        await ChannelLock.send(message)

        ### PLOTTING CODE ###
        with plt.xkcd():

            # Change length of plot long axis based on player count
            if len(deathnames) >= 20:
                long_axis=32
            elif len(deathnames) >= 5:
                long_axis=16
            else:
                long_axis=8

            # Initialize Plot
            fig = plt.figure(figsize=(long_axis,8))
            ax = fig.add_subplot(111)

            # Index the players in order
            player_index = np.arange(0,len(deathnames),1)

            # Plot count vs. player index
            plot = ax.bar(player_index,deathcounts,color='darkorange')

            # Change "index" label to corresponding player name
            ax.set_xticks(player_index)
            ax.set_xticklabels(deathnames,fontsize=20,rotation=-45,ha='left',rotation_mode="anchor")

            # Set y-axis limits to make sure the biggest bar has space for label above it
            ax.set_ylim(0,max(deathcounts)*1.1)

            # Set y-axis to have integer labels, since this is integer data
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.tick_params(axis='y', labelsize=20)

            # Add labels above bars
            ax.bar_label(plot,fontsize=20) 

            # Plot Title
            ax.set_title('Death Counts',fontsize=28)

        # Save image and send - any existing plot will be overwritten
        plt.savefig(DeathPlotLocation, bbox_inches="tight")
        await ChannelLock.send(file=discord.File(DeathPlotLocation))
    except:
        await DebugLock.send('ERROR DEATHCOUNT')
    
async def CheckCount():
    try:
        page = requests.get(ArchTrackerURL)
        soup = BeautifulSoup(page.content, "html.parser")

        #Yoinks table rows from the checks table
        tables = soup.find("table",id="checks-table")
        for slots in tables.find_all('tbody'):
            rows = slots.find_all('tr')

        SlotWidth = 0
        GameWidth = 0
        StatusWidth = 0
        ChecksWidth = 0
        SlotArray = [0]
        GameArray = [0]
        StatusArray = [0]
        ChecksArray = [0]

        #Moves through rows for data
        for row in rows:
            slot = (row.find_all('td')[1].text).strip()
            game = (row.find_all('td')[2].text).strip()
            status = (row.find_all('td')[3].text).strip()
            checks = (row.find_all('td')[4].text).strip()
            
            SlotArray.append(len(slot))
            GameArray.append(len(game))
            StatusArray.append(len(status))
            ChecksArray.append(len(checks))

        SlotArray.sort(reverse=True)
        GameArray.sort(reverse=True)
        StatusArray.sort(reverse=True)
        ChecksArray.sort(reverse=True)

        SlotWidth = SlotArray[0]
        GameWidth = GameArray[0]
        StatusWidth = StatusArray[0]
        ChecksWidth = ChecksArray[0]

        slot = "Slot"
        game = "Game"
        status = "Status"
        checks = "Checks"
        percent = "%"

        #Preps check message
        checkmessage = "```" + slot.ljust(SlotWidth) + " || " + game.ljust(GameWidth) + " || " + checks.ljust(ChecksWidth) + " || " + percent +"\n"

        for row in rows:
            slot = (row.find_all('td')[1].text).strip()
            game = (row.find_all('td')[2].text).strip()
            status = (row.find_all('td')[3].text).strip()
            checks = (row.find_all('td')[4].text).strip()
            percent = (row.find_all('td')[5].text).strip()
            checkmessage = checkmessage + slot.ljust(SlotWidth) + " || " + game.ljust(GameWidth) + " || " + checks.ljust(ChecksWidth) + " || " + percent + "\n"

        #Finishes the check message
        checkmessage = checkmessage + "```"
        await ChannelLock.send(checkmessage)
    except:
        await DebugLock.send('ERROR IN CHECKCOUNT')

async def CheckGraph():
    try:
        page = requests.get(ArchTrackerURL)
        soup = BeautifulSoup(page.content, "html.parser")

        #Yoinks table rows from the checks table
        tables = soup.find("table",id="checks-table")
        for slots in tables.find_all('tbody'):
            rows = slots.find_all('tr')

        GameState = {}
        #Moves through rows for data
        for row in rows:
            slot = (row.find_all('td')[1].text).strip()
            game = (row.find_all('td')[2].text).strip()
            status = (row.find_all('td')[3].text).strip()
            checks = (row.find_all('td')[4].text).strip()
            percent = (row.find_all('td')[5].text).strip()
            GameState[slot] = percent
        
        GameState = {key: value for key, value in sorted(GameState.items())}
        GameNames = []
        GameCounts = []
        deathkeys = GameState.keys()
        for key in deathkeys:
            GameNames.append(str(key))
            GameCounts.append(float(GameState[key]))

        ### PLOTTING CODE ###
        with plt.xkcd():

            # Change length of plot long axis based on player count
            if len(GameNames) >= 20:
                long_axis=32
            elif len(GameNames) >= 5:
                long_axis=16
            else:
                long_axis=8

            # Initialize Plot
            fig = plt.figure(figsize=(long_axis,8))
            ax = fig.add_subplot(111)

            # Index the players in order
            player_index = np.arange(0,len(GameNames),1)

            # Plot count vs. player index
            plot = ax.bar(player_index,GameCounts,color='darkorange')

            # Change "index" label to corresponding player name
            ax.set_xticks(player_index)
            ax.set_xticklabels(GameNames,fontsize=20,rotation=-45,ha='left',rotation_mode="anchor")

            # Set y-axis limits to make sure the biggest bar has space for label above it
            ax.set_ylim(0,max(GameCounts)*1.1)

            # Set y-axis to have integer labels, since this is integer data
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.tick_params(axis='y', labelsize=20)

            # Add labels above bars
            ax.bar_label(plot,fontsize=20) 

            # Plot Title
            ax.set_title('Completion Percentage',fontsize=28)

        # Save image and send - any existing plot will be overwritten
        plt.savefig(CheckPlotLocation, bbox_inches="tight")
        await ChannelLock.send(file=discord.File(CheckPlotLocation))

    except:
        await DebugLock.send('ERROR IN CHECKGRAPH')

async def HintList(player):
    try:
        page = requests.get(ArchTrackerURL)
        soup = BeautifulSoup(page.content, "html.parser")

        #Yoinks table rows from the checks table
        tables = soup.find("table",id="hints-table")
        for slots in tables.find_all('tbody'):
            rows = slots.find_all('tr')


        RegistrationFile = RegistrationDirectory + player.name + ".csv"
        if not os.path.isfile(RegistrationFile):
            await player.dm_channel.send("You've not registered for a slot : (")
        else:
            r = open(RegistrationFile,"r")
            RegistrationLines = r.readlines()
            r.close()
            for reglines in RegistrationLines:

                message = "**Here are all of the hints assigned to "+ reglines.strip() +":**"
                await player.dm_channel.send(message)

                FinderWidth = 0
                ReceiverWidth = 0
                ItemWidth = 0
                LocationWidth = 0
                GameWidth = 0
                EntrenceWidth = 0
                FinderArray = [0]
                ReceiverArray = [0]
                ItemArray = [0]
                LocationArray = [0]
                GameArray = [0]
                EntrenceArray = [0]

                #Moves through rows for data
                for row in rows:
                    found = (row.find_all('td')[6].text).strip()
                    if(found == "✔"):
                        continue
                    
                    finder = (row.find_all('td')[0].text).strip()
                    receiver = (row.find_all('td')[1].text).strip()
                    item = (row.find_all('td')[2].text).strip()
                    location = (row.find_all('td')[3].text).strip()
                    game = (row.find_all('td')[4].text).strip()
                    entrence = (row.find_all('td')[5].text).strip()

                    if(reglines.strip() == finder):
                        FinderArray.append(len(finder))
                        ReceiverArray.append(len(receiver))
                        ItemArray.append(len(item))
                        LocationArray.append(len(location))
                        GameArray.append(len(game))
                        EntrenceArray.append(len(entrence))

                FinderArray.sort(reverse=True)
                ReceiverArray.sort(reverse=True)
                ItemArray.sort(reverse=True)
                LocationArray.sort(reverse=True)
                GameArray.sort(reverse=True)
                EntrenceArray.sort(reverse=True)

                FinderWidth = FinderArray[0]
                ReceiverWidth = ReceiverArray[0]
                ItemWidth = ItemArray[0]
                LocationWidth = LocationArray[0]
                GameWidth = GameArray[0]
                EntrenceWidth = EntrenceArray[0]

                finder = "Finder"
                receiver = "Receiver"
                item = "Item"
                location = "Location"
                game = "Game"
                entrence = "Entrance"

                #Preps check message
                checkmessage = "```" + finder.ljust(FinderWidth) + " || " + receiver.ljust(ReceiverWidth) + " || " + item.ljust(ItemWidth) + " || " + location.ljust(LocationWidth) + " || " + game.ljust(GameWidth) + " || " + entrence +"\n"
                for row in rows:
                    found = (row.find_all('td')[6].text).strip()
                    if(found == "✔"):
                        continue

                    finder = (row.find_all('td')[0].text).strip()
                    receiver = (row.find_all('td')[1].text).strip()
                    item = (row.find_all('td')[2].text).strip()
                    location = (row.find_all('td')[3].text).strip()
                    game = (row.find_all('td')[4].text).strip()
                    entrence = (row.find_all('td')[5].text).strip()

                    if(reglines.strip() == finder):
                        checkmessage = checkmessage + finder.ljust(FinderWidth) + " || " + receiver.ljust(ReceiverWidth) + " || " + item.ljust(ItemWidth) + " || " + location.ljust(LocationWidth) + " || " + game.ljust(GameWidth) + " || " + entrence +"\n"

                    if len(checkmessage) > 1500:
                        checkmessage = checkmessage + "```"
                        await player.dm_channel.send(checkmessage)
                        checkmessage = "```"

                # Caps off the message
                checkmessage = checkmessage + "```"
                await player.dm_channel.send(checkmessage)

    except:
        await DebugLock.send('ERROR IN HINTLIST')

@tasks.loop(seconds=120)
async def CheckArchHost():
    try:
        ArchRoomID = ArchServerURL.split("/")
        RoomAPI = "https://archipelago.gg/api/room_status/"+ArchRoomID[4]
        RoomPage = requests.get(RoomAPI)
        RoomData = json.loads(RoomPage.content)

        cond = str(RoomData["last_port"])
        if(cond == ArchPort):
            print("Port Check Passed")
        else:
            print("Port Check Failed")
            print(RoomData["last_port"])
            print(ArchPort)
            message = "Port Check Failed <@"+DiscordAlertUserID+">"
            await ChannelLock.send(message)
            await DebugLock.send(message)

    except:
        await DebugLock.send('ERROR IN CHECKARCHHOST')


client.run(DiscordToken)





