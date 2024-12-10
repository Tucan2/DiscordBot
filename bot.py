from discord import Interaction, Intents, File
import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv
from PIL import Image
import easyocr

import plotly.graph_objects as go 
import scipy.stats as sci

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

bot_intents = Intents.default()
bot_intents.message_content = True

bot = commands.Bot(command_prefix = '!', intents = bot_intents) # Can change the command_prefix, this is just what goes in front of a command like !ping

@bot.event
async def on_ready():
    print("Bot is ready")

    @bot.command()
    async def ping(ctx):
        print("Ping called")
        await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

    @bot.command()
    async def imgtxt(ctx):
        print("Image reader called")
        message = ctx.message
        if valid_image_url(message.content):
            await download_image(attachment.url, "image", attachment.filename)

        for attachment in message.attachments:
            if valid_image_url(attachment.filename):
                await download_image(attachment.url, "image", attachment.filename)

        new_name = ""

        if(attachment.filename[-4:-1] == ".pn"):
            img_png = Image.open("image/" + attachment.filename[0:len(attachment.filename)]) 

            rgb_img = img_png.convert('RGB')

            new_name = "image/" + attachment.filename[0:len(attachment.filename) - 3] + ".jpg"
  
            rgb_img.save(new_name)

            os.remove("image/" + attachment.filename)

        reader = easyocr.Reader(['en'])

        result = reader.readtext(new_name)

        os.remove("image/" + new_name)

        for detection in result:
            await ctx.send(detection[1])
                
    def valid_image_url(url):
        image_extensions = ['png', 'jpg', 'jpeg']
        for image_extension in image_extensions:
            if url.endswith('.' + image_extension):
                return True
        return False

    def graphHelper(ctx):
        message = ctx.message.content 
        graphNameIndex = message.find('name')
        graphName = ""
        if (graphNameIndex >= 0):
            graphName = message[graphNameIndex: len(message)]
            graphNameIndex1 = graphName.find(':')
            graphNameIndex2 = graphName.find(',')
            graphName = graphName[graphNameIndex1+1:graphNameIndex2]

        xaxisName = message.find('xaxis')
        xAxis = ""
        if (xaxisName >= 0):
            xAxis = message[xaxisName: len(message)]
            xAxis1 = xAxis.find(':')
            xAxis2 = xAxis.find(',')
            xAxis = xAxis[xAxis1+1:xAxis2]  

        yaxisName = message.find('yaxis')
        yAxis = ""
        if (yaxisName >= 0):
            yAxis = message[yaxisName: len(message)]
            yAxis1 = yAxis.find(':')
            yAxis2 = yAxis.find(',')
            yAxis = yAxis[yAxis1+1:yAxis2]                 

        xIndex1 = message.find('[')
        xIndex2 = message.find(']')

        xString = message[xIndex1:xIndex2+1]

        x = []
        i = 0
        while i < len(xString):
            a = 0
            aUsed = False
            try:
                j = i
                while j < len(xString):
                    if (xString[j] == "-"):
                        j = j + 1
                    else:
                        a = int(xString[i:j+1])
                        aUsed = True
                        j = j + 1
            except:
                if(aUsed):
                    x.append(a)
                i = i + 1
            
        message = message[xIndex2 + 1: len(message)]

        yIndex1 = message.find('[')
        yIndex2 = message.find(']')

        yString = message[yIndex1:yIndex2+1]

        y = []
        i = 0
        while i < len(yString):
            a = 0
            aUsed = False
            try:
                j = i
                while j < len(yString):
                    if (yString[j] == "-"):
                        j = j + 1
                    else:
                        a = int(yString[i:j+1])
                        aUsed = True
                        j = j + 1
            except:
                if(aUsed):
                    y.append(a)
                i = i + 1

        x2 = []
        i = 0 
        while i < len(x):
            if (i%2 == 0):
                x2.append(x[i])

            i = i + 1

        y2 = []
        i = 0
        while i < len(y):
            if (i%2 == 0):
                y2.append(y[i])

            i = i + 1
        
        return(x2, y2, graphName, xAxis, yAxis)

    async def download_image(url, images_path, filename):
        async with aiohttp.ClientSession().get(url) as resp:
                if resp.status == 200:
                    image_name = os.path.basename(filename)
                    with open(os.path.join(images_path, image_name), "wb") as f:
                        f.write(await resp.read())

    @bot.command()
    async def graph(ctx):
        print("Graph called")
        try:
            x, y, graphName, xAxis, yAxis = graphHelper(ctx)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x, y=y, name = "Graph"))


            fig.update_layout(
                font=dict(
                    family="LEMON MILK",
                    size=18,
                    color="Black"
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                template='plotly_white', 
                title=graphName, 
                xaxis_title=xAxis, 
                yaxis_title=yAxis
            )
            fig.update_yaxes(showgrid=True,
                            gridcolor="lightgrey",
                            linecolor="black",
                            tickcolor="black",
                            tickfont=dict(color="black", size=10),
                            title_font = {"size": 22, "color": "black"},
                            title_standoff = 15,
            )
            fig.update_xaxes(linecolor="black",
                            tickfont=dict(color="black", size=10),
                            title_font = {"size": 22, "color": "black"},
                            title_standoff = 15
            )

            fig.write_image("graph.png")
            

            path = "graph.png"
            file = discord.File(path, filename="graph.png")

            await ctx.send("Here's your graph:", file=file)
            os.remove(path)
        except:
            print("ERROR")
            await ctx.send("Data is not in correct format")

    @bot.command()
    async def webpage(ctx):
        import urllib.request

        url = ctx.message.content
        url = url[9:len(url)]

        try:
            # Open the URL and read its content
            response = urllib.request.urlopen(url)
            
            # Read the content of the response
            data = response.read()
            
            # Decode the data (if it's in bytes) to a string
            html_content = data.decode('utf-8')
            
            with open("Output.txt", "w") as text_file:
                text_file.write(html_content)

            path = "Output.txt"
            file = discord.File(path, filename="Output.txt")

            await ctx.send("Here's your HTML file:", file=file)
            os.remove("Output.txt")

        except Exception as e:
            print("Error fetching URL:", e)
            await ctx.send("Error fetching URL:", e)
            
    @bot.command()
    async def scatter(ctx):
        print("Scatter called")
        try:
            x, y, graphName, xAxis, yAxis = graphHelper(ctx)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x, y=y, name = "Graph", mode="markers"))


            fig.update_layout(
                font=dict(
                    family="LEMON MILK",
                    size=18,
                    color="Black"
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                template='plotly_white', 
                title=graphName, 
                xaxis_title=xAxis, 
                yaxis_title=yAxis
            )
            fig.update_yaxes(showgrid=True,
                            gridcolor="lightgrey",
                            linecolor="black",
                            tickcolor="black",
                            tickfont=dict(color="black", size=10),
                            title_font = {"size": 22, "color": "black"},
                            title_standoff = 15,
            )
            fig.update_xaxes(linecolor="black",
                            tickfont=dict(color="black", size=10),
                            title_font = {"size": 22, "color": "black"},
                            title_standoff = 15
            )

            fig.write_image("graph.png")
            

            path = "graph.png"
            file = discord.File(path, filename="graph.png")

            await ctx.send("Here's your graph:", file=file)
            os.remove(path)
        except:
            print("ERROR")
            await ctx.send("Data is not in correct format")

    @bot.command()
    async def pie(ctx):
        try:
            print("Pie called")
            x, y, graphName, xAxis, yAxis = graphHelper(ctx)

            x = []

            message = ctx.message.content
            xIndex1 = message.find('[') + 1
            xIndex2 = message.find(']')

            i = xIndex1

            while i < xIndex2:
                a = message[i]
                j = i

                while (message[j+1] != "," and j + 1 < xIndex2):
                    a = a + message[j+1]
                    j = j + 1

                x.append(a)
                i = j + 3



            fig = go.Figure(data=go.Pie(labels=x, values=y, name = "Graph"))


            fig.update_layout(
                font=dict(
                    family="LEMON MILK",
                    size=18,
                    color="Black"
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                template='plotly_white', 
                title=graphName, 
            )

            fig.write_image("graph.png")
            

            path = "graph.png"
            file = discord.File(path, filename="graph.png")

            await ctx.send("Here's your graph:", file=file)
            os.remove(path)
        except:
            print("ERROR")
            await ctx.send("Data is not in correct format")

    @bot.command()
    async def stats(ctx):
        x, y, graphName, xAxis, yAxis = graphHelper(ctx)

        finalMessage = ""
        describe = str(sci.describe(x))
        describe = describe[20:len(describe)-1]
        describe = "length=" + describe[0:len(describe)]
        describe = describe.replace(", ", "\n")
        finalMessage += describe
        finalMessage += "\nInter-quartile Range: " + str(sci.iqr(x))
        finalMessage += "\nBayesian confidence intervals for the mean, var, and std: " + str(sci.bayes_mvs(x))
        finalMessage += "\nTrimmed mean (10%): " + str(sci.trim_mean(x, .1))
        finalMessage += "\nEnthropy: " + str(sci.entropy(x))

        print(finalMessage)
        await ctx.send(finalMessage)

    @bot.command()
    async def textbook(ctx):
        print("textbook called")
        from pypdf import PdfReader

        try:
            message = ctx.message.content
            message = int(message[10: len(message)])
            reader = PdfReader("math.pdf") #the openstax calculus textbook, of many potential open-sourc etextbooks that could be added for use by this bot
            page = reader.pages[message + 7]
            with open("Output.txt", "w") as text_file:
                    text_file.write(page.extract_text())
            
            path = "Output.txt"
            file = discord.File(path, filename="Output.txt")

            await ctx.send("Textbook page:", file=file)
            os.remove("Output.txt")
        except:
            print("ERROR")
            await ctx.send("ERROR in page number")

bot.run(TOKEN)
