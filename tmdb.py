#!/usr/bin/env python3
import discord
from discord import Embed, Colour
import discord.ext.commands as commands
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(".env")
TOKEN = os.getenv('DISCORD_TOKEN')
API_KEY = os.getenv('TMDB_API_KEY')

# necessary permission for the bot to be able to read and send messages
intents = discord.Intents.all()
description = "A bot to get the title, the id, the main cast and the youtube trailer link of a movie or a tvshow."
client = commands.Bot(command_prefix='!', description=description, help_command=None, intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

# function to display the help message
@client.command(name="help", help="Display the help message.")
async def help(ctx):
    embed = discord.Embed(title="List of commands", color=Colour.random())
    embed.add_field(name="!tmdb movie <movie name>", value="Get the title, the id, the main cast and the trailer youtube link.", inline=False)
    embed.add_field(name="!tmdb tv <tvshow name>", value="Get the title, the id, the main cast and the trailer youtube link.", inline=False)
    await ctx.send(embed=embed)

# function to get the title, the id of a movie or a tvshow, the trailer youtube link and the main cast
@client.command(name="tmdb", help="Get the title, the id of a movie or a tvshow, the trailer youtube link and the main cast.")
async def get_infos(ctx, *args):
    if len(args) > 1:
        # get a random color for the embed message
        color = discord.Colour.random()
        if args[0] == 'movie':
            # get movie title, id and link
            movie = ' '.join(args[1:])
            r = requests.get('https://api.themoviedb.org/3/search/movie?api_key=' + API_KEY + '&language=fr&query=' + movie + '&page=1&include_adult=false')
            data = json.loads(r.text)
            movie_name = data['results'][0]['title']
            movie_id = data['results'][0]['id']
            embed = discord.Embed(title=movie_name + ' - ' + str(movie_id), url="https://www.themoviedb.org/movie/" + str(movie_id), color=color)

            # thumbnail of the movie
            # change set_thumbnail by set_image to have the image as an attachment
            movie_thumbnail = 'https://image.tmdb.org/t/p/w500' + data['results'][0]['poster_path']
            embed.set_thumbnail(url=movie_thumbnail)
            
            # get movie overview
            movie_overview = data['results'][0]['overview']
            embed.add_field(name="Synopsis", value=movie_overview, inline=False)
            
            # get the main cast
            r = requests.get('https://api.themoviedb.org/3/movie/' + str(movie_id) + '/credits?api_key=' + API_KEY + '&language=fr')
            data = json.loads(r.text)
            cast = data['cast']
            cast_name = ''
            for i in range(5):
                cast_name += cast[i]['name'] + " - " + 'https://www.themoviedb.org/person/' + str(cast[i]['id']) + '\n'
            embed.add_field(name="Acteurs principaux", value=cast_name, inline=False)
            
            # get movie trailer youtube link
            r = requests.get('https://api.themoviedb.org/3/movie/' + str(movie_id) + '/videos?api_key=' + API_KEY + '&language=fr')
            data = json.loads(r.text)
            movie_trailer = data['results'][0]['key']
            embed.add_field(name="Bande annonce", value='https://www.youtube.com/watch?v=' + movie_trailer, inline=False)
            
            # send the embed message
            await ctx.send(embed=embed)

        elif args[0] == 'tv':
            # get tv title, id and link
            tv = ' '.join(args[1:])
            r = requests.get('https://api.themoviedb.org/3/search/tv?api_key=' + API_KEY + '&language=fr&query=' + tv + '&page=1&include_adult=false')
            data = json.loads(r.text)
            tv_id = data['results'][0]['id']
            tv_name = data['results'][0]['name']
            embed = discord.Embed(title=tv_name + ' - ' + str(tv_id), url="https://www.themoviedb.org/tv/" + str(tv_id), color=color)

            # thumbnail of the tv
            # change set_thumbnail by set_image to have the image as an attachment
            tv_thumbnail = 'https://image.tmdb.org/t/p/w500' + data['results'][0]['poster_path']
            embed.set_thumbnail(url=tv_thumbnail)
  
            # get the number of seasons and episodes
            r2 = requests.get('https://api.themoviedb.org/3/tv/' + str(tv_id) + '?api_key=' + API_KEY + '&language=fr')
            data2 = json.loads(r2.text)
            tv_seasons = data2['number_of_seasons']
            tv_episodes = data2['number_of_episodes']
            embed.add_field(name="Saisons", value=tv_seasons, inline=True)
            embed.add_field(name="Episodes", value=tv_episodes, inline=True)

            # get tv overview
            tv_overview = data['results'][0]['overview']
            embed.add_field(name="Synopsis", value=tv_overview, inline=False)

            # get the main cast and url of the actors tmdb page
            r = requests.get('https://api.themoviedb.org/3/tv/' + str(tv_id) + '/credits?api_key=' + API_KEY + '&language=fr')
            data = json.loads(r.text)
            cast = data['cast']
            cast_name = ''
            for i in range(5):
                cast_name += cast[i]['name'] + " - " + 'https://www.themoviedb.org/person/' + str(cast[i]['id']) + '\n'
            embed.add_field(name="Acteurs principaux", value=cast_name, inline=False)

            # get tv trailer youtube link
            r = requests.get('https://api.themoviedb.org/3/tv/' + str(tv_id) + '/videos?api_key=' + API_KEY + '&language=fr')
            data = json.loads(r.text)
            tv_trailer = data['results'][0]['key']
            embed.add_field(name="Bande annonce", value='https://www.youtube.com/watch?v=' + tv_trailer, inline=False)

            # send the embed message
            await ctx.send(embed=embed)
    else:
        await ctx.send('You must specify a movie or a tvshow.')

client.run(TOKEN)

