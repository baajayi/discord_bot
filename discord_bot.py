import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHATBOT_API_URL = os.getenv('CHATBOT_API_URL')
CHATBOT_API_KEY = os.getenv('CHATBOT_API_KEY')

# Set up bot with command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

@bot.command(name='ask')
async def ask_chatbot(ctx, *, question: str):
    """
    Command: !ask <your question>
    Sends the question to your chatbot API and returns the response
    """
    # Show typing indicator while processing
    async with ctx.typing():
        try:
            # Prepare the API request
            headers = {
                'Content-Type': 'application/json',
            }
            
            # Add API key if you have one
            if CHATBOT_API_KEY:
                headers['Authorization'] = f'Bearer {CHATBOT_API_KEY}'
            
            # Prepare payload (adjust based on your API structure)
            payload = {
                'query': question,
                'user_id': str(ctx.author.id),  # Optional: track user
                'channel_id': str(ctx.channel.id)  # Optional: track channel
            }
            
            # Send request to your chatbot API
            response = requests.post(
                CHATBOT_API_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            # Check if request was successful
            if response.status_code == 200:
                data = response.json()
                # Adjust based on your API response structure
                answer = data.get('response') or data.get('answer') or data.get('message')
                
                # Discord has a 2000 character limit per message
                if len(answer) > 2000:
                    # Split long responses
                    chunks = [answer[i:i+2000] for i in range(0, len(answer), 2000)]
                    for chunk in chunks:
                        await ctx.send(chunk)
                else:
                    await ctx.send(answer)
            else:
                await ctx.send(f"❌ Error: API returned status code {response.status_code}")
                
        except requests.exceptions.Timeout:
            await ctx.send("⏱️ Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            await ctx.send(f"❌ Error connecting to chatbot: {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)

# Run the bot
if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)