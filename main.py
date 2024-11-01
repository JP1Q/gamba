import discord
from discord.ext import commands
import random
import pickle
import os
import asyncio

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="kkt ", intents=intents)


# Player class
class Player:
    def __init__(self, nick, balance=10):
        self.nick = nick
        self.balance = balance

# Load player data
players = {}
if os.path.exists("players.pkl"):
    with open("players.pkl", "rb") as file:
        players = pickle.load(file)
    print("Loaded saved players.")
else:
    print("No saved players found. Starting fresh.")

# Save players to file
def save_players():
    with open("players.pkl", "wb") as file:
        pickle.dump(players, file)

# Retrieve or create a player by Discord ID
def get_player(user_id, nickname):
    if user_id not in players:
        print(f"New user {nickname} {user_id} has joined!")
        players[user_id] = Player(nickname, balance=1000)
    return players[user_id]

import asyncio

async def bet(ctx, player):
    embed = discord.Embed(
        title="Enter Your Bet",
        description="Please enter your bet amount as a whole number. Make sure it's within your balance.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

    try:
        # Wait for user input with error handling
        msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
        wager = int(msg.content)

        if wager <= 0:
            await ctx.send(embed=discord.Embed(title="Invalid Input", description="Bet amount must be a positive number. Please try again.", color=discord.Color.red()))
            return None

        if wager > player.balance:
            await ctx.send(embed=discord.Embed(title="Error", description="You don't have that much money.", color=discord.Color.red()))
            return None

        return wager

    except ValueError:
        await ctx.send(embed=discord.Embed(title="Invalid Input", description="Please enter a valid number. (You need to run the command again)", color=discord.Color.red()))
        return None
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(title="Timeout", description="Betting timed out. Please try again.", color=discord.Color.red()))
        return None

# Help Command
@bot.command()
async def commands(ctx):
    embed = discord.Embed(
        title="Help Menu",
        description="List of available commands:",
        color=discord.Color.green()
    )

    embed.add_field(name="kkt coinflip", value="Play a coin flip game. Bet an amount, guess Heads or Tails, and see if you win!", inline=False)
    embed.add_field(name="kkt diceroll", value="Play a dice roll game. Bet an amount and guess the dice roll outcome (1-6).", inline=False)
    embed.add_field(name="kkt slotmachine", value="Play the slot machine! Bet an amount and spin for a chance to win.", inline=False)
    embed.add_field(name="kkt crash", value="Play the crash game. Watch the multiplier increase and choose to cash out or risk losing it all!", inline=False)
    embed.add_field(name="kkt balance", value="Check your current balance.", inline=False)
    embed.add_field(name="kkt leaderboard", value="View the top players by balance.", inline=False)
    embed.add_field(name="kkt reset_balance @user", value="(Creator only) Reset the balance of a specified user to 10.", inline=False)

    await ctx.send(embed=embed)


# Coin Flip Game with user guidance
@bot.command()
async def coinflip(ctx):
    player = get_player(ctx.author.id, ctx.author.display_name)
    bet_amount = await bet(ctx, player)
    if bet_amount is None:
        return

    embed = discord.Embed(
        title="Coin Flip",
        description=f"{player.nick}, type 'h' for Heads or 't' for Tails to make your guess.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

    ht = (await bot.wait_for('message', timeout=30)).content.lower()
    if random.choice(["h", "t"]) == ht:
        player.balance += bet_amount
        result = f"{player.nick}, you won!"
    else:
        player.balance -= bet_amount
        result = f"{player.nick}, better luck next time!"

    await ctx.send(embed=discord.Embed(title="Coin Flip Result", description=result, color=discord.Color.green() if "won" in result else discord.Color.red()))
    save_players()

# Dice Roll Game with user guidance
@bot.command()
async def diceroll(ctx):
    player = get_player(ctx.author.id, ctx.author.display_name)
    bet_amount = await bet(ctx, player)
    if bet_amount is None:
        return

    embed = discord.Embed(
        title="Dice Roll",
        description=f"{player.nick}, guess the dice roll result by entering a number between 1 and 6.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

    guess = int((await bot.wait_for('message', timeout=30)).content)
    actual_roll = random.randint(1, 6)
    if actual_roll == guess:
        player.balance += bet_amount
        result = f"{player.nick}, you guessed it right! You won!"
    else:
        player.balance -= bet_amount
        result = f"{player.nick}, oops, the roll was {actual_roll}. Better luck next time!"

    await ctx.send(embed=discord.Embed(title="Dice Roll Result", description=result, color=discord.Color.green() if "won" in result else discord.Color.red()))
    save_players()

@bot.command()
async def slotmachine(ctx):
    player = get_player(ctx.author.id, ctx.author.display_name)
    bet_amount = await bet(ctx, player)
    if bet_amount is None:
        return

    # Slot symbols and winnings
    symbols = ["🍒", "🍋", "🔔", "💎", "🍀", "🍉", "⭐", "🍒", "🍀", "🍒", "🍀"]  # Duplicated winning symbols for higher chances
    winnings = {
        "🍒": 2,  # Reduced multiplier for more frequent wins
        "🍋": 4,
        "🔔": 5,
        "💎": 10,
        "🍀": 8,
        "🍉": 6,
        "⭐": 20
    }
    ultra_small_symbols = ["🍒", "🍀", "🍉"]  # More symbols that give ultra-small wins if they appear anywhere

    # Deduct the bet amount upfront
    player.balance -= bet_amount

    # Simulate slot machine rolling with more rows and enhanced animation
    rows, columns = 3, 3  # 3x3 grid
    rolls = []

    # Send the initial message for the slot machine
    initial_display = f"{player.nick}, spinning...\n"
    initial_embed = discord.Embed(
        title="Slot Machine 🎰",
        description=initial_display,
        color=discord.Color.blue()
    )
    message = await ctx.send(embed=initial_embed)

    for _ in range(5):  # Increased number of animations
        roll = [[random.choice(symbols) for _ in range(columns)] for _ in range(rows)]
        rolls.append(roll)

        # Format the roll into a visual 3x3 grid
        display = "\n".join([" | ".join(row) for row in roll])
        embed = discord.Embed(
            title="Slot Machine 🎰",
            description=display,
            color=discord.Color.blue()
        )

        # Edit the existing message with the new display
        await message.edit(embed=embed)
        await asyncio.sleep(0.7)  # Slight delay for animation effect

    # Final roll result
    final_roll = rolls[-1]
    display_result = "\n".join([" | ".join(row) for row in final_roll])
    result_embed = discord.Embed(
        title="Slot Machine Result 🎰",
        description=display_result,
        color=discord.Color.green()
    )

    # Check for full match, partial match, ultra-small win, or no win
    all_symbols = [symbol for row in final_roll for symbol in row]

    # Check for full row matches
    for row in final_roll:
        if row[0] == row[1] == row[2]:  # Full row match
            winnings_amount = int(bet_amount * winnings[row[0]])  # Convert to int for better balance updates
            player.balance += winnings_amount
            result_embed.add_field(name="Jackpot!", value=f"{player.nick}, you won {winnings_amount}!", inline=False)

    # Check for partial matches (two matching symbols in any row)
    partial_win = False
    for row in final_roll:
        if row[0] == row[1] or row[1] == row[2] or row[0] == row[2]:
            small_win_amount = int(bet_amount * 0.8)  # Increased small win amount
            player.balance += small_win_amount
            partial_win = True

    if partial_win:
        result_embed.add_field(name="Small Win!", value=f"{player.nick}, two symbols matched in a row! You won {small_win_amount}.", inline=False)

    # Ultra-small win for specific symbols appearing anywhere
    ultra_small_win = any(symbol in ultra_small_symbols for symbol in all_symbols)
    if ultra_small_win:
        ultra_small_amount = bet_amount // 3  # Increased ultra-small win amount
        player.balance += ultra_small_amount
        result_embed.add_field(name="Ultra-Small Win!", value=f"{player.nick}, special symbols appeared! You won {ultra_small_amount}.", inline=False)

    # No win case
    if not any(field.name in ["Jackpot!", "Small Win!", "Ultra-Small Win!"] for field in result_embed.fields):
        result_embed.add_field(name="Better Luck Next Time!", value=f"{player.nick}, no win this time.", inline=False)

    await ctx.send(embed=result_embed)
    save_players()

@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    player = get_player(ctx.author.id, ctx.author.display_name)
    recipient = get_player(member.id, member.display_name)

    if amount <= 0:
        await ctx.send(embed=discord.Embed(title="Invalid Amount", description="You must specify an amount greater than 0.", color=discord.Color.red()))
        return

    if player.balance < amount:
        await ctx.send(embed=discord.Embed(title="Insufficient Balance", description="You do not have enough balance to make this payment.", color=discord.Color.red()))
        return

    # Process the payment
    player.balance -= amount
    recipient.balance += amount

    await ctx.send(embed=discord.Embed(title="Payment Successful", description=f"{player.nick} paid {member.display_name} {amount}.", color=discord.Color.green()))
    save_players()

@bot.command()
async def crash(ctx):
    player = get_player(ctx.author.id, ctx.author.display_name)
    bet_amount = await bet(ctx, player)
    if bet_amount is None:
        return

    multiplier = 1.0
    player.balance -= bet_amount

    # Send initial message for the game
    embed = discord.Embed(
        title="Crash Game",
        description=f"{player.nick}, Current Multiplier: {multiplier}x\nType 'cash' to cash out now or 'continue' to keep playing.",
        color=discord.Color.orange()
    )
    message = await ctx.send(embed=embed)

    while True:
        # Update the multiplier
        multiplier = round(multiplier * 1.2, 2)
        
        # Edit the existing message with the updated multiplier
        embed.description = f"{player.nick}, Current Multiplier: {multiplier}x\nType 'cash' to cash out now or 'continue' to keep playing."
        await message.edit(embed=embed)

        # Random chance for the crash
        if random.randint(1, 10) == 1:
            await ctx.send(embed=discord.Embed(title="Crash!", description=f"{player.nick}, the game crashed! You lost your wager.", color=discord.Color.red()))
            break
        
        # Wait for user action
        try:
            action_msg = await bot.wait_for('message', timeout=30, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            action = action_msg.content.lower()
            await action_msg.delete()  # Delete the user's message after reading it
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(title="Timeout!", description=f"{player.nick}, you took too long to respond. The game has ended.", color=discord.Color.red()))
            break

        if action == 'cash':
            winnings = int(bet_amount * multiplier)
            player.balance += winnings
            await ctx.send(embed=discord.Embed(title="Cashed Out", description=f"{player.nick}, you cashed out! You won {winnings}.", color=discord.Color.green()))
            break
        elif action != 'continue':
            await ctx.send(embed=discord.Embed(title="Invalid Choice", description=f"{player.nick}, type 'cash' or 'continue'.", color=discord.Color.red()))
            break

    save_players()

# Show Balance
@bot.command()
async def balance(ctx):
    player = get_player(ctx.author.id, ctx.author.display_name)
    embed = discord.Embed(title="Balance", description=f"{player.nick}'s balance: {player.balance}", color=discord.Color.blue())
    await ctx.send(embed=embed)

# Leaderboard
@bot.command()
async def leaderboard(ctx):
    sorted_players = sorted(players.values(), key=lambda p: p.balance, reverse=True)
    leaderboard_text = "\n".join([f"{p.nick}: {p.balance}" for p in sorted_players[:10]])
    embed = discord.Embed(title="Leaderboard", description=leaderboard_text, color=discord.Color.gold())
    await ctx.send(embed=embed)



# Reset Balance
@bot.command()
async def reset_balance(ctx, user: discord.User):
    """
    Resets a user's balance to 10. Only the bot creator can use this command.

    Args:
        user (discord.User): The user whose balance should be reset.
    """

    if ctx.author.id != 709444526657503306:
        await ctx.send(embed=discord.Embed(title="Unauthorized", description="Only the bot creator can reset balances.", color=discord.Color.red()))
        return

    player = get_player(user.id, user.display_name)
    player.balance = 10
    save_players()
    await ctx.send(embed=discord.Embed(title="Balance Reset", description=f"{user.display_name}'s balance has been reset to 10.", color=discord.Color.green()))
