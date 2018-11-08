#-------------------IMPORTS------------------
#sok, itt nem használt de esetleg fontosnak bizonyuló modult is importáltam
import discord, logging, json, asyncio, time, random, aiohttp, re, datetime, traceback, os, sys, math, asyncpg
from time import gmtime
from discord.ext import commands
from functions import edit_json, read_json

#-------------------DATA---------------------
#-------------Változók-------------
#a bot tulajdonosának ID-ja, több parancshoz is jól jön, akár ha azt szeretnénk, hogy a parancsot csak a tulajdonos használjon
owner = ["361534796830081024"]
#más felhasználók ID-ja is megadható és használható ezzel a módszerrel
Jani = ["000000000000000000"]
#discord.py beépített osztályok definiálása a kezelhetősg érdekében, bár én lenttebb mindegyikat újra definiáltam
message = discord.Message
server = discord.Server
member = discord.Member
user = discord.User
permissions = discord.Permissions
#ez a bot EGY discord szerverre lett készítve, így a szervert definiáltam
PRServer = bot.get_server("370269066864361472")
#----------------------------------

#későbbi parancsokhoz a bot és a prefix definiálása
bot = commands.Bot(command_prefix='-', description=None)
#az alapértelmezett "help" parancs eltűntetése, hogy elkészíthessük a sajátunkat
bot.remove_command("help")
#a kiterjesztések lekérése
startup_extensions = ["YouTube"]
#a pontos idő lekéréséhez használt kód:
"""timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())"""

#-------------------SETUP--------------------
#online státusz
@bot.event
async def on_ready():
    #a megfelelő működés visszaigazolásához használjuk a `print()` funkciót
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    #a bot "game" státuszának beállítása
    await bot.change_presence(game=discord.Game(name='Újraindítva'))

#egy error definiálása az egyértelműbb kezelésért
class NoPermError(Exception):
    pass

#a kiterjesztések kezelése, a jelenlegi kódban nem használt, majd a megfelelő működés visszaigazolásához használjuk a `print()` funkciót
"""@bot.command()
async def load(extension_name : str):
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))

@bot.command()
async def unload(extension_name : str):
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))"""

#----------------COMMANDS--------------------
#egyes változók parancsonként újra definiálva vannak a könnyebb másolás érdekében
#pár parancson az egyes lépések külön-külön magyarázva vannak 

#--Moderátor parancsok definiálása--
#unban discord parancs, nem helyes használat(tulajdonságok (property) hiánya) kezelése
@bot.command(pass_context=True)
@commands.has_permissions(ban_members=True)
async def unban(ctx, user : discord.User=None, *, Reason=None):
    if user is None:
        await bot.reply("**The usage is `-unban {member} {Reason}`**")
    elif Reason is None:
        await bot.reply("**The usage is `-unban {member} {Reason}`**")
    else:
        if user.id == ctx.message.author.id:
            await bot.say("**You can't moderate yourself**")
        else:
            banneds = await bot.get_bans(ctx.message.server)
            if user not in banneds:
                bot.say("**The mentioned user aren't in the banneds' list, please mention a banned user!**")
            else:
                room = ctx.message.channel
                await bot.unban(ctx.message.server, user)
                LogRoom = bot.get_channel(id="401752340366884885")
                await bot.say(f"**{user.mention} got unbanned by {ctx.message.author.mention} for __{Reason}__\nSee the logs in {LogRoom.mention}**")
                em = discord.Embed(title="UNBAN", description=None, colour=0xe91e63)
                em.add_field(name="User", value=f"{user.mention}")
                em.add_field(name="Moderator", value=f"{ctx.message.author}")
                em.add_field(name="Reason", value=f"{Reason}")
                em.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
                timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                em.set_footer(text=timer)
                await bot.send_message(LogRoom, embed=em)
                Private = await bot.start_private_message(user)
                await bot.send_message(Private, f"**`Server: {PRserver}`\nYou got unbanned from {PRserver}**")

#MAGYARÁZAT
#a context haszálata, a program tudtára adjuk hogy "ugorja át" a `ctx` property-t
@bot.command(pass_context=True)
#a `@commands.has_permissions()` dekor segítségével megadjuk hogy melyik `discord.Permission`-nal rendelkező `Member` használhatja a parancsot
@commands.has_permissions(ban_members=True)
#a definíció kezdete, a tulajdonságok megadás a `None` használata a később lekezelhetőségért (hogyha hiányozna egy property)
#a * szimbólum utáni első property-t a program az utolsónak veszi, ezzel lehetővé teszi, hogy a felhasználó több szót is megadjon (mert az összes property max. 1 szóból állhat vagy " szimbólumot kell használni)
async def ban(ctx, user : discord.User=None, Day : int=None, *, Reason=None):
    #a property-k hiányának lekezelése
    if user is None:
        await bot.reply("**The usage is `-ban {member} {0 - 7 amount of days to delete his messages} {Reason}`**")
    elif Reason is None:
        await bot.reply("**The usage is `-ban {member} {0 - 7 amount of days to delete his messages} {Reason}`**")
    elif Day is None:
        await bot.reply("**The usage is `-ban {member} {0 - 7 amount of days to delete his messages} {Reason}`**")
    else:
        #ellenörzi, hogy a parancs használója nem egyezik a moderálni kívánt felhasználóval
        if user.id == ctx.message.author.id:
            await bot.say("**You can't moderate yourself**")
        #ha nem: a "kick" parancs végrehajtása extrákkal kiegészítve
        else:
            #a szoba definiálása melyebe a felhasználó a parancsot írta
            room = ctx.message.channel
            #maga a `ban()` funkció használata
            await bot.ban(user, delete_message_days=Day)
            #Extrák:
            #egy "Logroom" szoba definiálása melybe a bot kiírja a moderáció adatait
            LogRoom = bot.get_channel(id="401752340366884885")
            #a bot kiírja abba a szobába a lenti üzenetet melybe a felhaználó írta a parancsot
            await bot.say(f"**{user.mention} got banned by {ctx.message.author.mention} for __{Reason}__\nSee the logs in {LogRoom.mention}**")
            #egy `discord.Embed` létrehozása majd a "Logroom"-ba történő kiírása
            em = discord.Embed(title="BAN", description=None, colour=0xad1457)
            em.add_field(name="User", value=f"{user.mention}")
            em.add_field(name="Moderator", value=f"{ctx.message.author}")
            em.add_field(name="Reason", value=f"{Reason}")
            em.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
            #a pontos idő megadása, hogy mikor történt a moderáció
            timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
            em.set_footer(text=timer)
            #az üzenet elküldése
            await bot.send_message(LogRoom, embed=em)
            #privát beszélgetés megkezdése a felhasználóval, hogy értesítsük a moderációról
            Private = await bot.start_private_message(user)
            await bot.send_message(Private, f"**`Server: {PRserver}`\nYou got banned from {PRserver}**")
            #definíció vége

#kick discord parancs
@bot.command(pass_context=True)
@commands.has_permissions(kick_members=True)
async def kick(ctx, user : discord.User=None, *, Reason=None):
    if user is None:
        await bot.reply("**The usage is `-kick {member} {Reason}`**")
    elif Reason is None:
        await bot.reply("**The usage is `-kick {member} {Reason}`**")
    else:
        if user.id == ctx.message.author.id:
            await bot.say("**You can't moderate yourself**")
        else:
            room = ctx.message.channel
            await bot.kick(user)
            LogRoom = bot.get_channel(id="401752340366884885")
            await bot.say(f"**{user.mention} got Kicked by {ctx.message.author.mention} for __{Reason}__\nSee the logs in {LogRoom.mention}**")
            em = discord.Embed(title="KICK", description=None, colour=0xe74c3c)
            em.add_field(name="User", value=f"{user.mention}")
            em.add_field(name="Moderator", value=f"{ctx.message.author}")
            em.add_field(name="Reason", value=f"{Reason}")
            em.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
            timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
            em.set_footer(text=timer)
            await bot.send_message(LogRoom, embed=em)
            Private = await bot.start_private_message(user)
            await bot.send_message(Private, f"**`Server: {PRserver}`\nYou got kicked from {PRserver}**")

#MAGYARÁZAT
@bot.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def mute(ctx, user : discord.User=None, duration : int=None, *, Reason=None):
    if user is None:
        await bot.reply("**The usage is `-mute {member} {duration(in sec)} {Reason}`**")
    elif Reason is None:
        await bot.reply("**The usage is `-mute {member} {duration(in sec)} {Reason}`**")
    elif duration is None:
        await bot.reply("**The usage is `-mute {member} {duration(in sec)} {Reason}`**")
    else:
        if user.id == ctx.message.author.id:
            await bot.say("**You can't moderate yourself**")
        else:
            LogRoom = bot.get_channel(id="401752340366884885")
            room = ctx.message.channel
            #egy "Muted" discord role megadása, melynek a "Send Messages" tulajdonsága False
            MutedRole = discord.utils.get(ctx.message.server.roles, name="Muted")
            #a role hozzáadása a felhasználóhoz
            await bot.add_roles(user, MutedRole)
            await bot.say(f"**{user.mention} got Muted (for {duration} sec) by {ctx.message.author.mention} for __{Reason}__\nSee the logs in {LogRoom.mention}**")
            em = discord.Embed(title="MUTE", description=None, colour=0x11806a)
            em.add_field(name="User", value=f"{user.mention}")
            em.add_field(name="Moderator", value=f"{ctx.message.author}")
            em.add_field(name="Reason", value=f"{Reason}")
            em.add_field(name="Duration", value=f"{duration} sec")
            em.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
            timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
            em.set_footer(text=timer)
            await bot.send_message(LogRoom, embed=em)
            Private = await bot.start_private_message(user)
            await bot.send_message(Private, f"**`Server: {PRserver}`\nYou, {user.mention} got muted!**")
            #az `asyncio.sleep()` funkció használata a felhasználó által megadott `duration` property-vel
            #ennyi ideig lesz a felhasználó beszédképtelen
            await asyncio.sleep(duration)
            #majd a role eltávolítása
            await bot.remove_roles(user, MutedRole)
            em = discord.Embed(title="UNMUTE", description=None, colour=0x1abc9c)
            em.add_field(name="User", value=f"{user.mention}")
            em.add_field(name="Moderator", value=f"{ctx.message.author}")
            em.add_field(name="Reason", value="Time is up...")
            em.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
            timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
            em.set_footer(text=timer)
            await bot.send_message(LogRoom, embed=em)
            Private = await bot.start_private_message(user)
            await bot.send_message(Private, f"**`Server: {PRserver}`\nYou got unmuted**")

@bot.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, user : discord.User=None, *, Reason=None):
    if user is None:
        await bot.reply("**The usage is `-unmute {member} {Reason}`**")
    elif Reason is None:
        await bot.reply("**The usage is `-unmute {member} {Reason}`**")
    else:
        if user.id == ctx.message.author.id:
            await bot.say("**You can't moderate yourself**")
        else:
            LogRoom = bot.get_channel(id="401752340366884885")
            room = ctx.message.channel
            MutedRole = discord.utils.get(ctx.message.server.roles, name="Muted")
            await bot.remove_roles(user, MutedRole)
            await bot.say(f"**{user.mention} got UnMuted by {ctx.message.author.mention} for __{Reason}__\nSee the logs in {LogRoom.mention}**")
            em = discord.Embed(title="UNMUTE", description=None, colour=0x1abc9c)
            em.add_field(name="User", value=f"{user.mention}")
            em.add_field(name="Moderator", value=f"{ctx.message.author}")
            em.add_field(name="Reason", value=f"{Reason}")
            em.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
            timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
            em.set_footer(text=timer)
            await bot.send_message(LogRoom, embed=em)
            Private = await bot.start_private_message(user)
            await bot.send_message(Private, f"**`Server: {PRserver}`\nYou got unmuted*")

#MAGYARÁZAT
#a discord "lock" parancsal egy szobát tudunk lezárni így csak az Adminisztrátorok tudnak hozzáférni    
@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True)
async def lock(ctx, duration : int=None, *, Reason=None):
    if Reason is None:
        await bot.reply("**The usage is `-lock {duration (in sec)} {Reason}`**")
    elif duration is None:
        await bot.reply("**The usage is `-lock {duration (in sec)} {Reason}`**")
    else:
        #egy minden felhasználó tulajdonába lévő role megadása
        Registered = discord.utils.get(ctx.message.server.roles, name="Registered")
        #egy `discord.PermissionOverwrite()` készítése a szoba hozzáféréseinek változtatásához
        overwrite = discord.PermissionOverwrite()
        #a "Send Messages" permission False-ra állítása
        overwrite.send_messages = False
        #használat:
        await bot.edit_channel_permissions(ctx.message.channel, Registered, overwrite)
        await bot.send_message(ctx.message.channel, f"**{ctx.message.channel.mention} is now locked for __{Reason}__**")
        LogRoom = bot.get_channel(id="401752340366884885")
        em = discord.Embed(title="LOCK", description=None, colour=0x1f8b4c)
        em.add_field(name="Channel", value=f"{ctx.message.channel.mention}")
        em.add_field(name="Moderator", value=f"{ctx.message.author}")
        em.add_field(name="Reason", value=f"{Reason}")
        em.add_field(name="Duration", value=f"{duration} sec")
        em.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
        timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        em.set_footer(text=timer)
        await bot.send_message(LogRoom, embed=em)
        await asyncio.sleep(duration)
        #a megadott idő lejárta után a hozzáférések visszaállítása
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = True
        await bot.edit_channel_permissions(ctx.message.channel, Registered, overwrite)
        await bot.send_message(ctx.message.channel, f"**{ctx.message.channel.mention} is unlocked for __{Reason}__**")
        LogRoom = bot.get_channel(id="401752340366884885")
        em = discord.Embed(title="UNLOCK", description=None, colour=0x2ecc71)
        em.add_field(name="Channel", value=f"{ctx.message.channel.mention}")
        em.add_field(name="Moderator", value=f"{ctx.message.author}")
        em.add_field(name="Reason", value=f"{Reason}")
        em.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
        timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        em.set_footer(text=timer)
        await bot.send_message(LogRoom, embed=em)

#a discord "unlock" paranccsal a "lock" parancs határideje előtt is visszaállíthatjuk a hozzáfáráseket
@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, *, Reason=None):
    if Reason is None:
        await bot.reply("**The usage is `-unlock {Reason}`**")
    else:
        Registered = discord.utils.get(ctx.message.server.roles, name="Registered")
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = True
        await bot.edit_channel_permissions(ctx.message.channel, Registered, overwrite)
        await bot.send_message(ctx.message.channel, f"**{ctx.message.channel.mention} is now unlocked for __{Reason}__**")
        LogRoom = bot.get_channel(id="401752340366884885")
        em = discord.Embed(title="UNLOCK", description=None, colour=0x2ecc71)
        em.add_field(name="Channel", value=f"{ctx.message.channel.mention}")
        em.add_field(name="Moderator", value=f"{ctx.message.author}")
        em.add_field(name="Reason", value=f"{Reason}")
        em.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
        timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        em.set_footer(text=timer)
        await bot.send_message(LogRoom, embed=em)
    
#MAGYARÁZAT
#a "clear" paranccsal egyes üzeneteket törölhetünk, az alábbi egy kidolgozozz példa
@bot.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def clear(ctx, number : int=None):
    if number is None:
        await bot.reply("**The usage is `-clear {number of messages to delete}`**")
    else:
        #egy változó definiálása, mivel az első szám a 0 a python nyelvben is ezért a felhasználó által megadott törölni kívánt üzenetek mennyiségéhez eggyel többet kell számítanunk
        number += 1
        #a `purge_from()` funkció használata több üzenet törséhez a "deleted" változóban
        deleted = await bot.purge_from(ctx.message.channel, limit=number)
        #a "num" változó látrehozása az output számára
        num = number - 1
        #Egyéb, embed készítése
        LogRoom = bot.get_channel(id="401752340366884885")
        em = discord.Embed(title=None, description=f'{ctx.message.author} deleted __{num}__ messages', colour=0x3498db)
        em.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
        em.add_field(name="Channel", value=f"{ctx.message.channel.mention}")
        timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        em.set_footer(text=timer)
        msg = await bot.send_message(ctx.message.channel, embed=em)
        await bot.send_message(LogRoom, embed=em)
        await asyncio.sleep(4)
        await bot.delete_message(msg)
        #definíció vége
#----------------------------------
#---------Egyéb Parancsok----------

#a `send_typing()` funkció bemutatása, mellyel nem küld a bot üzenetet, de a discord "typing" indikátora megjelenik
@bot.command(pass_context=True)
async def typing(ctx):
    await bot.send_typing(ctx.message.channel)

#az embed `set_thumbnail()` funkciójának bemutatása
@bot.command(pass_context=True)
async def whoami(ctx):
    colours = [0x11806a, 0x1abc9c, 0x2ecc71, 0x1f8b4c, 0x3498db, 0x206694, 0x9b59b6, 0x71368a, 0xe91e63, 0xad1457, 0xf1c40f, 0xc27c0e, 0xe67e22, 0xa84300, 0xe74c3c, 0x992d22, 0x95a5a6, 0x607d8b, 0x979c9f, 0x546e7a]
    col = random.choice(colours)
    em = discord.Embed(title="WHO AM I?", description=f"**\n{ctx.message.author}**", colour=col)
    em.set_thumbnail(url=ctx.message.author.avatar_url)
    await bot.send_message(ctx.message.channel, embed=em)

#a property-k használata, és típusaikbak megadása
@bot.command(pass_context=True)
async def slap(ctx, member : discord.Member=None, *, Reason=None):
    if member is None:
        await bot.reply("**The usage is `-slap {member} {Reason}`**")
    else:
        await bot.say(f"**{ctx.message.author} slaped {member.mention} for __{Reason}__**")

#a ping lekérése. Fontos, hogy ezzel a paranccsal a felhasználó NEM a bot pingjét kapja meg, hanem a sajátját!
#ping lekérése és az `edit_message()` bemutatása
#a parancs egy üzenetet küld el a "msg" változóban majd a megváltoztatja az üzenetet (edit) és leméri az ehhez szükséges időt hozzávetőlegesen 
@bot.command(pass_context=True)
async def ping(ctx):
    #python funkció
    before = time.monotonic()
    #embed készítése
    embed = discord.Embed(description=":ping_pong: **...**", colour=0x3498db)
    #embed elküldése üzenetben a "msg" változóban
    msg = await bot.say(embed=embed)
    #a ping a másodperc ezredében való megadása (Ms)
    ping = (time.monotonic() - before) * 1000
    pinges = int(ping)
    #kapottt ping érték értelmezhetőbbé tétele a felhasználó számára
    if 999 > pinges > 400:
        mesg = "That's a lot!"
    elif pinges > 1000:
        mesg = "Realy sloooooow!"
    elif 399 > pinges > 141:
        mesg = "Ahhh, not good!"
    elif pinges < 140:
        mesg = "It's Good"
    #újjab embed készítése az `edit_message` funkció számára
    em = discord.Embed(title=None, description=f":ping_pong: Seems like `{pinges}` Ms\n{mesg}", colour=0x3498db)
    em.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
    timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
    em.set_footer(text=timer)
    #a funkció az előbb elküldött "msg" üzenet "embed" nevű embed-ét megváltoztatja az újjab "em" nevű embed-re
    await bot.edit_message(msg, embed=em)

#a "roll" parancs a két megadott sszám közötti egész számokból választ egyet
#`edit_message()` használata
@bot.command(pass_context=True)
async def roll(ctx, x : int=None, y : int=None):
    if x is None:
        await bot.reply("**The usage is `-roll {number} {number}`**")
    elif y is None:
        await bot.reply("**The usage is `-roll {number} {number}`**")
    else:
        msg = random.randint(x, y)
        text = await bot.send_message(ctx.message.channel, "**Hmmm...**")
        await asyncio.sleep(3)
        await bot.edit_message(text, f"**My choose: {msg}**")

#egyszerűbb múveletek
#`edit_message()`, `asyncio.sleep()`, `reply()` használata
#a `reply()` funkció gyorsabb mint a `send_message()`, mert nincs szükségünk a szoba megadására és csak annyiban tér el a `say()`-től, hogy a bot az üzenete elé a parancsot hívó felhasználó nevét illeszti mentionban
#kivonás
@bot.command(pass_context=True)
async def sub(ctx, x : int=None, y : int=None):
    if x is None:
        await bot.reply("**The usage is `-sub {number} {number}`**")
    elif y is None:
        await bot.reply("**The usage is `-sub {number} {number}`**")
    else:
        msg = x - y
        text = await bot.send_message(ctx.message.channel, "**Hmmm...**")
        await asyncio.sleep(3)
        await bot.edit_message(text, f"**The result: {msg}**")

#szorzás  
@bot.command(pass_context=True)
async def mul(ctx, x : int=None, y : int=None):
    if x is None:
        await bot.reply("**The usage is `-mul {number} {number}`**")
    elif y is None:
        await bot.reply("**The usage is `-mul {number} {number}`**")
    else:
        msg = x * y
        text = await bot.send_message(ctx.message.channel, "**Hmmm...**")
        await asyncio.sleep(3)
        await bot.edit_message(text, f"**The result: {msg}**")

#osztás    
@bot.command(pass_context=True)
async def div(ctx, x : int=None, y : int=None):
    if x is None:
        await bot.reply("**The usage is `-div {number} {number}`**")
    elif y is None:
        await bot.reply("**The usage is `-div {number} {number}`**")
    else:
        msg = x / y
        text = await bot.send_message(ctx.message.channel, "**Hmmm...**")
        await asyncio.sleep(3)
        await bot.edit_message(text, f"**The result: {msg}**")

#hatványozás, x-t y-ra emeli   
@bot.command(pass_context=True)
async def exp(ctx, x : int=None, y : int=None):
    if x is None:
        await bot.reply("**The usage is `-exp {number} {number}`**")
    elif y is None:
        await bot.reply("**The usage is `-exp {number} {number}`**")
    else:
        msg = x ** y
        text = await bot.send_message(ctx.message.channel, "**Hmmm...**")
        await asyncio.sleep(3)
        await bot.edit_message(text, f"**The result: {msg}**")

#összeadás    
@bot.command(pass_context=True)
async def add(ctx, x : int=None, y : int=None):
    if x is None:
        await bot.reply("**The usage is `-add {number} {number}`**")
    elif y is None:
        await bot.reply("**The usage is `-add {number} {number}`**")
    else:
        msg = x + y
        text = await bot.send_message(ctx.message.channel, "**Hmmm...**")
        await asyncio.sleep(3)
        await bot.edit_message(text, f"**The result: {msg}**")

#A discord botoknak, mint a discord felhasználóknak van egy Game tulajdonságuk, mely a jelenleg játszott játékot mutatja ki
#ám botoknál ide akármit kiírhatunk, a szöveg a bot neve alatt fog megjelenni
#az `on_event`-ben már megadtunk egy Game-t a `change_presence` funkcióval, ez a parancs felülírja azt
#`say` funkció használata
@bot.command()
async def game(*, play=None):
    if play is None:
        await bot.reply("**The usage is `-game {Something to set as a game}`**")
    else:
        await bot.change_presence(game=discord.Game(name=play))
        em = discord.Embed(title="Game Status", description=f"Game status changed to __{play}__!", colour=0x3498db)
        #a bot az üzenetet automatikusan a jelenlegi szobába küldi
        await bot.say(embed=em)

#a `change_nickname` funkció bemutatása, mellyel a felhasználó megváltoztathatja saját felhasználónevét
@bot.command(pass_context=True)
async def nick(ctx, *, name=None):
    if name is None:
        await bot.reply("**The usage is `r-name {Something to set as your name}` ty.**")
    else:
        await bot.change_nickname(ctx.message.author, name)
        em = discord.Embed(title="Nickname", description=f"{ctx.message.author}'s nick set to __{name}__!", colour=0x3498db)
        await bot.say(embed=em)

#elágazások bemutatása
#a "suggest" parancs megfelelő üzenetet küld a megfelelő szobába
@bot.command(pass_context=True)
async def suggest(ctx, pref=None, *, text=None):
    if pref is None:
        await bot.reply("**The usage is `-suggest {prefix (Q, S, C, B)} {text}`**")
    elif text is None:
        await bot.reply("**The usage is `-suggest {prefix (Q, S, C, B)} {text}`**")
    else:
        try:
            if pref is "S":
                msg = "SUGGESTION"
            if pref is "Q":
                msg = "QUESTION"
            if pref is "C":
                msg = "COMMAND SUGGESTION"
            if pref is "B":
                msg = "BUGS"
            else:
                bot.say("**Please use a valid prefix! The available prefixes: __Q__, __S__, __C__, __B__**")
        finally:
            colours = [0x11806a, 0x1abc9c, 0x2ecc71, 0x1f8b4c, 0x3498db, 0x206694, 0x9b59b6, 0x71368a, 0xe91e63, 0xad1457, 0xf1c40f, 0xc27c0e, 0xe67e22, 0xa84300, 0xe74c3c, 0x992d22, 0x95a5a6, 0x607d8b, 0x979c9f, 0x546e7a]
            col = random.choice(colours)
            em = discord.Embed(title=f"{msg}", description=f"**From {ctx.message.author.mention}**\n⋙ {text}", colour=col)
            em.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
            timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
            em.set_footer(text=timer)
            channel = bot.get_channel(id="444837114258128916")
            room = bot.get_channel(id="444837114258128916")
            await bot.send_message(ctx.message.channel, f"**:white_check_mark: Sent in {channel.mention}**")
            mesg = await bot.send_message(room, embed=em)
            if pref is "S":
                await bot.add_reaction(mesg, "👍")
                await bot.add_reaction(mesg, "👎")
            if pref is "C":
                await bot.add_reaction(mesg, "👍")
                await bot.add_reaction(mesg, "👎")
            
#a definícióban használható property-kkel végezhető logikai kifejezések
#len() python funkció
#for loop
@bot.command(pass_context=True)
async def poll(ctx, options: str=None, *, question=None):
    if options is None:
        await bot.reply("**The usage is `r-poll {options (2-10)} {Question or Suggestion}` ty.**")
    elif question is None:
        await bot.reply("**The usage is `r-poll {options (2-10)} {Question or Suggestion}` ty.**")
    else:
        if len(options) <= 1:
            await bot.say('You need more than one option to make a poll!')
            return
        if len(options) > 10:
            await bot.say('You cannot make a poll for more than 10 things!')
            return
        if len(options) == 2:
            reactions = ['👍', '👎']
        else:
            reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
        description = []
        for x, option in enumerate(options):
            description += '\n {} {}'.format(reactions[x], option)
        embed = discord.Embed(title=question, description=''.join(description), colour=0x3498db)
        react_message = await bot.say(embed=embed)
        for reaction in reactions[:len(options)]:
            await bot.add_reaction(react_message, reaction)
        await bot.edit_message(react_message, embed=embed)

#egy `listen()` létrehozása mely annyiban tér el az `event`-től hogy `listen()` funkciót akármennyit megadhatunk, míg `event`-t csak egyszer hozhazunk létre
#beépített eventek használata: on_member_join(), on_server_role_create(), on_server_role_delete(), on_channel_create(), on_channel_delete, on_member_remove
#az alábbi eventekkel a magadott "voice" típusú szobákat használjuk output ként
@bot.listen()
async def on_member_join(member):
    botserver = bot.get_server(id="370269066864361472")
    membersroom = bot.get_channel(id="460397271788421120")
    await bot.edit_channel(membersroom, name=f"👥Members: {len(botserver.members)}")
    room = bot.get_channel(id="370269066864361476")
    em = discord.Embed(title=f"__{member.name}__ Joined!", description=f"**Welcome {member.mention}, have a great time here!**", colour=0x3498db)
    await bot.send_message(room, embed=em)

@bot.event
async def on_server_role_create(role):
    botserver = bot.get_server(id="370269066864361472")
    rolesroom = bot.get_channel(id="460457033129263145")
    await bot.edit_channel(rolesroom, name=f"🌵Roles: {len(botserver.roles)}")  

@bot.event
async def on_server_role_delete(role):
    botserver = bot.get_server(id="370269066864361472")
    rolesroom = bot.get_channel(id="460457033129263145")
    await bot.edit_channel(rolesroom, name=f"🌵Roles: {len(botserver.roles)}")  

@bot.event
async def on_channel_create(channel):
    botserver = bot.get_server(id="370269066864361472")
    channelsroom = bot.get_channel(id="460397552379101184")
    await bot.edit_channel(channelsroom, name=f"🌐Channels: {len(botserver.channels)}")

@bot.event
async def on_channel_delete(channel):
    botserver = bot.get_server(id="370269066864361472")
    channelsroom = bot.get_channel(id="460397552379101184")
    await bot.edit_channel(channelsroom, name=f"🌐Channels: {len(botserver.channels)}")
    
@bot.listen()
async def on_member_remove(member):
    botserver = bot.get_server(id="370269066864361472")
    membersroom = bot.get_channel(id="460397271788421120")
    await bot.edit_channel(membersroom, name=f"👥Members: {len(botserver.members)}")
    room2 = bot.get_channel(id="453598661306482688")
    await bot.send_message(room2, f"**{member} left without saying anything...**")

#a "say" paranccsal a bot megismétli a felhasználó által megadott szöveget
#* szimbólum bemutatása
#a felhasználó akármennyi szót írhat a parancsba a bot mindet ki fogja jelezni
@bot.command(pass_context=True)
async def say(ctx, *, words=None):
    if words is None:
        await bot.reply("**The usage is `r-say {Something}` ty.**")
    else:
        await bot.say(f"**{words}**")

#mivel eltűntettük a beépített "help" parancsot ezért most elkészíthetünk egy sajátot
#az eredeto "help" parancs automatikusan egy stringbe teszi a definiált parancsokat, de csak szimplán egymás alá írva
#(külön díszítővel megadható leírás a parancsokhoz)
#valamint a help parancs nem érzékeli az on_message event (lenttebb bemutatva) által létrehozott triggereket!
#a saját "help" parancsot úgy díszítjük, ahogy szeretnénk
@bot.command(pass_context=True)
async def help():        
    emb = discord.Embed(title='MY COMMANDS:', description="", colour=0x3498db)
    emb.add_field(name='--------------------', value=':small_blue_diamond: -typing\n'
                            ':white_small_square: -whoami\n'
                            ':small_blue_diamond: -slap\n'
                            ':white_small_square: -help\n'
                            ':small_blue_diamond: -ping\n'
                            ':white_small_square: -roll\n'
                            ':small_blue_diamond: -add\n'
                            ':white_small_square: -suv\n'
                            ':small_blue_diamond: -mul\n'
                            ':white_small_square: -div\n'
                            ':small_blue_diamond: -exp\n'
                            ':white_small_square: -game\n'
                            ':small_blue_diamond: -nick\n'
                            ':white_small_square: -suggest\n'
                            ':small_blue_diamond: -poll\n'
                            ':white_small_square: -say\n', inline=False)
    await bot.send_message(ctx.message.channel, embed=emb)


#on_message event bemutatása
#az on_message is discord parancsok létrehozására szolgál, de ezt "primitívebb" parancsok létrehozására használjuk
#ez az event úgy működik mind minden event, triggerelni kell
#Ez az ő esetében akkor történik ha a megadott "string"-t tartalmazza egy elküldött üzenet
#még nem is muszály a prefixet hozzátenni, a megadott "string" akármi lehet, ezzel akár létrehozhatunk másodlagos prefixeket is
#persze csak látszólagosan
#a discord.py beépített eventjeit az "async" előjellel használjuk
#a fenti parancsokban context-t használtunk de itt ezt a "message" property helyettesíti
#Fontos: on_message eventtel csak property nélküli parancsok hozhatók létre! Esetleg egy property-s parancsok, de sokkal időigényesebb!
#property-vel rendelkező parancsra példát is láthatunk
@bot.event
async def on_message(message):
    #az `if message.content()` funkcióval azt nézzük hogy az üzenet tartalmazza-e a szövegünket
    #a `startswith()` funkciót hozzákapcsolva már azt is nézi az elágazás, hogy a megadott szöveg az üzenet elejév van-e
    #ez a parancs kiírja a pontos időt
    #amint láthatjuk ilyen property nélküli sima outputos parancsokat sokkal gyorsabban készíthetünk on_message eventtel
    if message.content.startswith("-time"):
        timer = time.strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        #a ctx helyett mindehol a "message" változó használjuk
        await bot.send_message(message.channel, f"**{message.author.mention}, the time is __{timer}__**")
    #on_message használatával is létrehozhatunk embed-t
    if message.content.startswith("-embed"):
        em = discord.Embed(title="Embed", description=None, colour=0x3498db)
        em.add_field(name="I'm an embed!", value="--------")
        await bot.send_message(message.channel, embed=em)
    #az `upper()` funkcióval megadhatjuk hogy a kis- és nagybetűs változatát is észlelje a szövegnek
    #a parancs trigger-edik a "-amiowner?" szöveggel is és a "-AMioWneR?" szöveggel is
    #fontos `upper()` használatával a szöveget nagy betűkkel kell írni
    #`lower()` használatával ez nem szükséges de a példában nem ezt mutattam be
    #ízelítő a discord emojik-ből
    if message.content.upper().startswith('-AMIOWNER?'):
        if message.author.id in owner:
            #a discord emojikat ugyanúgy használjuk a kódolásban mint discord felhasználóként, `:emoji_name:`
            #miután a bot elküldi az üzenetet ":white_check_mark" stringként a discord automatikusan észleli és átjavítja ✅-ra
            await bot.send_message(message.channel, ':white_check_mark: **You are the Owner**')
        else:
            await bot.send_message(message.channel, ':negative_squared_cross_mark: **You aren\'t the Owner.**')
    #discord emojik, szétbontott parancsokban, mindent a lehető legtöbbszőr leírva
    if message.content.startswith('-bigdigits'):
        await bot.send_message(message.channel, ':globe_with_meridians: **DIGITS:\n'
                               '-Zero, One, Two, Three, Four, Five, Six, Seven, Eight, Nine\n'
                               'Type `r-digits {0-9}` for the digits**')
    if message.content.startswith('-digits 0'):
        await bot.send_message(message.channel, ':radio_button: **Zero:**')
        await bot.send_message(message.channel, ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n" 
                                    ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                                    ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                                    ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                                    ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                                    ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                                    ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:")
    if message.content.startswith('-digits 1'):
        await bot.send_message(message.channel, ':radio_button: **One:**')
        await bot.send_message(message.channel, ":black_circle::black_circle::large_blue_circle::black_circle::black_circle:\n"
                                ":black_circle::large_blue_circle::large_blue_circle::black_circle::black_circle:\n"
                                ":black_circle::black_circle::large_blue_circle::black_circle::black_circle:\n"
                                ":black_circle::black_circle::large_blue_circle::black_circle::black_circle:\n"
                                ":black_circle::black_circle::large_blue_circle::black_circle::black_circle:\n"
                                ":black_circle::black_circle::large_blue_circle::black_circle::black_circle:\n"
                                ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n")
    if message.content.startswith('-digits 2'):
        await bot.send_message(message.channel, ':radio_button: **Two:**')
        await bot.send_message(message.channel, ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":black_circle::black_circle::black_circle::large_blue_circle::black_circle:\n"
                               ":black_circle::black_circle::large_blue_circle::black_circle::black_circle:\n"
                               ":black_circle::large_blue_circle::black_circle::black_circle::black_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::black_circle:\n"
                               ":large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle:")
    if message.content.startswith('-digits 3'):
        await bot.send_message(message.channel, ':radio_button: **Three:**')
        await bot.send_message(message.channel, ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":black_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":black_circle::black_circle::large_blue_circle::large_blue_circle::large_blue_circle:\n"
                               ":black_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:")
    if message.content.startswith('-digits 4'):
        await bot.send_message(message.channel, ':radio_button: **Four:**')
        await bot.send_message(message.channel, ":black_circle::black_circle::black_circle::large_blue_circle::black_circle:\n"
                               ":black_circle::black_circle::large_blue_circle::large_blue_circle::black_circle:\n"
                               ":black_circle::large_blue_circle::black_circle::large_blue_circle::black_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::large_blue_circle::black_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::large_blue_circle::black_circle:\n"
                               ":large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle:\n"
                               ":black_circle::black_circle::black_circle::large_blue_circle::black_circle:")
    if message.content.startswith('-digits 5'):
        await bot.send_message(message.channel, ':radio_button: **Five:**')
        await bot.send_message(message.channel, ":large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::black_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::black_circle:\n"
                               ":large_blue_circle::large_blue_circle::large_blue_circle::black_circle::black_circle:\n"
                               ":black_circle::black_circle::black_circle::large_blue_circle::black_circle:\n" 
                               ":black_circle::black_circle::black_circle::large_blue_circle::black_circle:\n"
                               ":large_blue_circle::large_blue_circle::large_blue_circle::black_circle::black_circle:")
    if message.content.startswith('-digits 6'):
        await bot.send_message(message.channel, ':radio_button: **Six:**')
        await bot.send_message(message.channel, ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::black_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::black_circle:\n"
                               ":large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:")
    if message.content.startswith('-digits 7'):
        await bot.send_message(message.channel, ':radio_button: **Seven:**')
        await bot.send_message(message.channel, ":black_circle::black_circle::black_circle::black_circle::black_circle:\n"
                               ":large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle:\n"
                               ":black_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":black_circle::black_circle::black_circle::large_blue_circle::black_circle:\n"
                               ":black_circle::black_circle::large_blue_circle::black_circle::black_circle:\n"
                               ":black_circle::large_blue_circle::black_circle::black_circle::black_circle:\n"
                               ":black_circle::large_blue_circle::black_circle::black_circle::black_circle:")
    if message.content.startswith('-digits 8'):
        await bot.send_message(message.channel, ':radio_button: **Eight:**')
        await bot.send_message(message.channel, ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:")
    if message.content.startswith('-digits 9'):
        await bot.send_message(message.channel, ':radio_button: **Nine:**')
        await bot.send_message(message.channel, ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle:\n"
                               ":black_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":black_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                               ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:")
    #a python random moduljának `choice()` függvényének egybeágyazásos bemutatása
    if message.content.startswith('-lenny'):
        ears = ['q{}p', 'ʢ{}ʡ', '⸮{}?', 'ʕ{}ʔ', 'ᖗ{}ᖘ', 'ᕦ{}ᕥ', 'ᕦ({})ᕥ', 'ᕙ({})ᕗ', 'ᘳ{}ᘰ', 'ᕮ{}ᕭ', 'ᕳ{}ᕲ', '({})', '[{}]', '୧{}୨', '୨{}୧', '⤜({})⤏', '☞{}☞', 'ᑫ{}ᑷ', 'ᑴ{}ᑷ', 'ヽ({})ﾉ', '乁({})ㄏ', '└[{}]┘', '(づ{})づ', '(ง{})ง', '|{}|']
        eyes = ['⌐■{}■', ' ͠°{} °', '⇀{}↼', '´• {} •`', '´{}`', '`{}´', 'ó{}ò', 'ò{}ó', '>{}<', 'Ƹ̵̡ {}Ʒ', 'ᗒ{}ᗕ', '⪧{}⪦', '⪦{}⪧', '⪩{}⪨', '⪨{}⪩', '⪰{}⪯', '⫑{}⫒', '⨴{}⨵', "⩿{}⪀", "⩾{}⩽", "⩺{}⩹", "⩹{}⩺", "◥▶{}◀◤", "≋{}≋", "૦ઁ{}૦ઁ", "  ͯ{}  ͯ", "  ̿{}  ̿", "  ͌{}  ͌", "ළ{}ළ", "◉{}◉", "☉{}☉", "・{}・", "▰{}▰", "ᵔ{}ᵔ", "□{}□", "☼{}☼", "*{}*", "⚆{}⚆", "⊜{}⊜", ">{}>", "❍{}❍", "￣{}￣", "─{}─", "✿{}✿", "•{}•", "T{}T", "^{}^", "ⱺ{}ⱺ", "@{}@", "ȍ{}ȍ", "x{}x", "-{}-", "${}$", "Ȍ{}Ȍ", "ʘ{}ʘ", "Ꝋ{}Ꝋ", "๏{}๏", "■{}■", "◕{}◕", "◔{}◔", "✧{}✧", "♥{}♥", " ͡°{} ͡°", "¬{}¬", " º {} º ", "⍜{}⍜", "⍤{}⍤", "ᴗ{}ᴗ", "ಠ{}ಠ", "σ{}σ"]
        mouth = ['v', 'ᴥ', 'ᗝ', 'Ѡ', 'ᗜ', 'Ꮂ', 'ヮ', '╭͜ʖ╮', ' ͟ل͜', ' ͜ʖ', ' ͟ʖ', ' ʖ̯', 'ω', '³', ' ε ', '﹏', 'ل͜', '╭╮', '‿‿', '▾', '‸', 'Д', '∀', '!', '人', '.', 'ロ', '_', '෴', 'ѽ', 'ഌ', '⏏', 'ツ', '益']
        #így a stringünk nem egymásután pakolt fülekből, szemekből és szájakból fog állni, hanem egy teljes "lenny" arcként
        lenny = random.choice(ears).format(random.choice(eyes)).format(random.choice(mouth))
        await bot.send_message(message.channel, "**A wild Lenny has appeard:**\n\n\t" + lenny)
    #a fenti bigdigit-ek használata, itt is külön-külön mindent újra leírtam, a parancs jóval egyszerűbben elkészíthető változókkal
    if message.content.startswith('-leave'):
        em5 = discord.Embed(title=":warning: WARNING :warning:", description="THE BOT WILL LEAVE THE SERVER IN:\n"
                            ":large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n"
                            ":large_blue_circle::black_circle::black_circle::black_circle::black_circle:\n"
                            ":large_blue_circle::black_circle::black_circle::black_circle::black_circle:\n"
                            ":large_blue_circle::large_blue_circle::large_blue_circle::black_circle::black_circle:\n"
                            ":black_circle::black_circle::black_circle::large_blue_circle::black_circle:\n" 
                            ":black_circle::black_circle::black_circle::large_blue_circle::black_circle:\n"
                            ":large_blue_circle::large_blue_circle::large_blue_circle::black_circle::black_circle:", colour=0x3498db)
        msg = await bot.send_message(message.channel, embed=em5)
        await asyncio.sleep(1)
        em4 = discord.Embed(title=":warning: WARNING :warning:", description="THE BOT WILL LEAVE THE SERVER IN:\n"
                            ":black_circle::black_circle::black_circle::large_blue_circle::black_circle:\n"
                            ":black_circle::black_circle::large_blue_circle::large_blue_circle::black_circle:\n"
                            ":black_circle::large_blue_circle::black_circle::large_blue_circle::black_circle:\n"
                            ":large_blue_circle::black_circle::black_circle::large_blue_circle::black_circle:\n"
                            ":large_blue_circle::black_circle::black_circle::large_blue_circle::black_circle:\n"
                            ":large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle:\n"
                            ":black_circle::black_circle::black_circle::large_blue_circle::black_circle:", colour=0x3498db)
        await bot.edit_message(msg,  embed=em4)
        await asyncio.sleep(1)
        em3 = discord.Embed(title=":warning: WARNING :warning:", description="THE BOT WILL LEAVE THE SERVER IN:\n"
                            ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n"
                            ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                            ":black_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                            ":black_circle::black_circle::large_blue_circle::large_blue_circle::large_blue_circle:\n"
                            ":black_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                            ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                            ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:", colour=0x3498db)
        await bot.edit_message(msg,  embed=em3)
        await asyncio.sleep(1)
        em2 = discord.Embed(title=":warning: WARNING :warning:", description="THE BOT WILL LEAVE THE SERVER IN:\n"
                            ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n"
                            ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                            ":black_circle::black_circle::black_circle::large_blue_circle::black_circle:\n"
                            ":black_circle::black_circle::large_blue_circle::black_circle::black_circle:\n"
                            ":black_circle::large_blue_circle::black_circle::black_circle::black_circle:\n"
                            ":large_blue_circle::black_circle::black_circle::black_circle::black_circle:\n"
                            ":large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle::large_blue_circle:", colour=0x3498db)
        await bot.edit_message(msg,  embed=em2)
        await asyncio.sleep(1)
        em1 = discord.Embed(title=":warning: WARNING :warning:", description="THE BOT WILL LEAVE THE SERVER IN:\n"
                            ":black_circle::black_circle::large_blue_circle::black_circle::black_circle:\n"
                            ":black_circle::large_blue_circle::large_blue_circle::black_circle::black_circle:\n"
                            ":black_circle::black_circle::large_blue_circle::black_circle::black_circle:\n"
                            ":black_circle::black_circle::large_blue_circle::black_circle::black_circle:\n"
                            ":black_circle::black_circle::large_blue_circle::black_circle::black_circle:\n"
                            ":black_circle::black_circle::large_blue_circle::black_circle::black_circle:\n"
                            ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n", colour=0x3498db)
        await bot.edit_message(msg,  embed=em1)
        await asyncio.sleep(1)
        em0 = discord.Embed(title=":warning: WARNING :warning:", description="THE BOT WILL LEAVE THE SERVER IN:\n"
                            ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:\n" 
                            ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                            ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                            ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                            ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                            ":large_blue_circle::black_circle::black_circle::black_circle::large_blue_circle:\n"
                            ":black_circle::large_blue_circle::large_blue_circle::large_blue_circle::black_circle:", colour=0x3498db)
        await bot.edit_message(msg,  embed=em0)
        await asyncio.sleep(1)
        em = discord.Embed(title="It was a joke :)", colour=0x3498db)
        await bot.edit_message(msg,  embed=em)
    #a discordnak van egy úgynevezett "Syntax Code" markdown típusa, a használata botoknál is ugyanúgy alkalmazható:
    
    #```Syntax neve
    #szöveg
    #```
    
    #"Syntac neve": a Syntax Code markdown-nak sokféle fajtája van általában programozási nyelvek: css, html, js, py, md, diff de akár el is maradhat
    if message.content.startswith('-bot'):
        em = discord.Embed(description= "```html\n"
                                "<head>\n"
                                "<h1>Html style</h1>
                                "</head>", colour=0x3498db)
        await bot.send_message(message.channel, embed=em)
    #FONTOS!
    #az újjabb discord.py - a Python 3.0 utáni - verziókban, on_message használata után az aláábi kód beillesztése kötelező!!
    #ha nem tennénk meg ezt, a többi definiált parancsaink nem működnének!
    await bot.process_commands(message)

#Végül a "token" váltózóban biztonságosan lekérjük az egyedi DISCORD_TOKEN-t amivel a botot definiáljuk, a discord tokent kiadni tilos!
#az online felhőalapú platformoknak van egy "Keys" füle ahol beállíthatjuk a DISCORD_TOKENT-t a discord tokenünkre
token = os.environ.get('DISCORD_TOKEN')
#a `run()` függvénnyel elindítjuk a botot és befejezzük a munkánkat 
bot.run(token)

#A Discord Bot készítésének ez csak a programozási része volt a Discord App létrehozásának lépéseit a README-ben írtam le
