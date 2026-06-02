import discord
from discord import app_commands
import time
import json
import os

# ========================= CONFIG =========================
TOKEN = "TOKEN"
GUILD_ID = 1509047831946727536

# === TEAM ROLES ===
TEAM_ROLES = {
    "Montreal Angels": 1509047832101916735,
    "Baltimore Bats": 1509047832101916734,
    "Santa Barbara Tigers": 1509047832101916733,
    "Winchester Widows": 1509047832093655080,
    "Bristol City Thunder": 1509047832093655079,
    "Buffalo Horsemen": 1509047832093655078,
    "Rushmore Rhinos": 1509047832101916737,
    "Springfield Wasps": 1509047832101916736,
    "Mobile Flock": 1509047832093655077,
    "St. Paul Pups": 1509047832093655076,
    "Memphis Kings": 1509047832093655075,
    "Nebraska Commanders": 1509047832093655074,
    "Alabama State Bruins": 1509683143479656529,
    "Jacksonville Bolts": 1509683149570048060,
    "Fargo Blizzards": 1509683153114239188,
    "Glendale Ghosts": 1509683155765035068,
}

# === TEAM LOGOS ===
TEAM_LOGOS = {
    "Montreal Angels": "https://cdn.discordapp.com/emojis/1490806529996099604.png",
    "Baltimore Bats": "https://cdn.discordapp.com/emojis/1510012607661084792.png",
    "Santa Barbara Tigers": "https://cdn.discordapp.com/emojis/1510012672630984937.png",
    "Winchester Widows": "https://cdn.discordapp.com/emojis/1510012798241869834.png",
    "Bristol City Thunder": "https://cdn.discordapp.com/emojis/1510012881100603563.png",
    "Buffalo Horsemen": "https://cdn.discordapp.com/emojis/1510013013783220508.png",
    "Rushmore Rhinos": "https://cdn.discordapp.com/emojis/1510012226159775935.png",
    "Springfield Wasps": "https://cdn.discordapp.com/emojis/1510012389980897481.png",
    "Mobile Flock": "https://cdn.discordapp.com/emojis/1510013069001228328.png",
    "St. Paul Pups": "https://cdn.discordapp.com/emojis/1510013140794867712.png",
    "Memphis Kings": "https://cdn.discordapp.com/emojis/1408581167481094216.png",
    "Nebraska Commanders": "https://cdn.discordapp.com/emojis/1481077625610043463.png",
    "Alabama State Bruins": "https://cdn.discordapp.com/emojis/1510013468122681424.png",
    "Jacksonville Bolts": "https://cdn.discordapp.com/emojis/1510013430499643493.png",
    "Fargo Blizzards": "https://cdn.discordapp.com/emojis/1510013369690755202.png",
    "Glendale Ghosts": "https://cdn.discordapp.com/emojis/1485852578523910325.png",
}

# Special Roles
NO_TRANSFERS_ROLE_ID = 1509047831946727540
EXTRA_TRANSFER_1_ROLE_ID = 1509756656689483906
EXTRA_TRANSFER_2_ROLE_ID = 1510163844943712286
EXTRA_TRANSFER_3_ROLE_ID = 1510163936115425420
HEAD_COACH_ROLE_ID = 1509047832101916740
ASSISTANT_COACH_ROLE_ID = 1509047832101916739
CAPTAIN_ROLE_ID = 1509754503191335152
BOOSTER_ROLE_ID = 1509674877068771502
VERIFIED_ROLE_ID = 1510710691735273613   # ← Put your Verified role ID here

# Analytics & Admin
ANALYTICS_ROLE_ID = 1509334552366153890          # ← Analytics role ID (only they can use /analytics)
ADMIN_ROLE_1_ID = 1509047832135602209
ADMIN_ROLE_2_ID = 1509047832135602210
ADMIN_ROLE_3_ID = 1509049501426520284

# Channels
TRANSACTIONS_CHANNEL_ID = 1509065936471330856
COMPETITION_CHANNEL_ID = 1509067684472553585
ACCOUNT_SWITCH_CHANNEL_ID = 1510192088279417002
SCOUT_CHANNEL_ID = 1509067258461425814
HC_APPLY_CHANNEL_ID = 1510416102151421982       # ← Channel where /hcapply submissions are sent

# Affiliated Servers
AFFILIATED_SERVERS = [
    "https://discord.gg/QdFn6fWKKP",
    "https://discord.gg/FnSZksyE7B",
    "https://discord.gg/TNbNn2ERg6",
    "https://discord.gg/B4Jy93BSgB",
    "https://discord.gg/YanukYHxDR",
]

# QBB Cooldown
QBB_COOLDOWN = 1 * 6
last_qbb_time = 0

# Color Roles
COLOR_ROLES = {
    "Blueberry": 1510135497182150846,
    "Woody": 1510148561873010824,
    "Charcoal": 1510148698225508492,
    "Tortilla": 1510150641983557752,
    "Banana": 1510151428671406220,
    "Cherry": 1510156856490725556,
    "Bubblegum": 1510134224416669898,
    "Strawberry": 1510155331081343196,
    "Crystal": 1510148677837258863,
}

# Stats storage
STATS_FILE = "user_stats.json"
user_stats = {}

def load_stats():
    global user_stats
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                user_stats = json.load(f)
        except:
            user_stats = {}

def save_stats():
    with open(STATS_FILE, "w") as f:
        json.dump(user_stats, f, indent=2)

load_stats()

# =========================================================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def get_user_team(member: discord.Member):
    for team_name, role_id in TEAM_ROLES.items():
        if role_id != 0 and member.get_role(role_id):
            return team_name, role_id
    return None, None

def is_admin(member: discord.Member):
    return any(member.get_role(rid) for rid in [ADMIN_ROLE_1_ID, ADMIN_ROLE_2_ID, ADMIN_ROLE_3_ID] if rid != 0)

async def log_transaction(interaction, title: str, description: str, color: int, team_name: str = None):
    if TRANSACTIONS_CHANNEL_ID == 0:
        return
    channel = interaction.guild.get_channel(TRANSACTIONS_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title=title, description=description, color=color)
        if team_name and team_name in TEAM_LOGOS and TEAM_LOGOS[team_name]:
            embed.set_thumbnail(url=TEAM_LOGOS[team_name])
        await channel.send(embed=embed)

@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await tree.sync(guild=guild)
        print(f"✅ Successfully synced {len(synced)} commands to your server!")
        await tree.sync()
        print("✅ Global sync attempted")
    except Exception as e:
        print(f"❌ Sync error: {e}")

# ====================== QBB ELO SYSTEM ======================
QBB_ELO_FILE = "qbb_elo.json"
QBB_ELO_LEADERBOARD_CHANNEL_ID = 1509067729448079461   # ← CHANGE THIS TO YOUR LEADERBOARD CHANNEL ID

qbb_data = {
    "players": {},
    "matches": [],
    "next_match_id": 1
}

def load_qbb_data():
    global qbb_data
    if os.path.exists(QBB_ELO_FILE):
        try:
            with open(QBB_ELO_FILE, "r") as f:
                qbb_data = json.load(f)
        except:
            pass

def save_qbb_data():
    with open(QBB_ELO_FILE, "w") as f:
        json.dump(qbb_data, f, indent=2)

load_qbb_data()

# ====================== HC APPLY ======================
class HCApplyModal(discord.ui.Modal, title="Head Coach Application"):
    why = discord.ui.TextInput(label="Why do you want to become Head Coach?", style=discord.TextStyle.paragraph, required=True)
    offer = discord.ui.TextInput(label="What do you offer over other candidates?", style=discord.TextStyle.paragraph, required=True)
    lineup = discord.ui.TextInput(label="Projected lineup if you were Head Coach?", style=discord.TextStyle.paragraph, required=True)  # ← Shortened
    experience = discord.ui.TextInput(label="Do you have any experience as a head coach?", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🧠 New Head Coach Application", color=0xFF69B4)
        embed.add_field(name="Applicant", value=interaction.user.mention, inline=False)
        embed.add_field(name="Why do you want to become Head Coach?", value=self.why.value, inline=False)
        embed.add_field(name="What do you offer over other candidates?", value=self.offer.value, inline=False)
        embed.add_field(name="Projected Lineup", value=self.lineup.value, inline=False)
        embed.add_field(name="Experience as Head Coach?", value=self.experience.value, inline=False)

        channel = interaction.guild.get_channel(HC_APPLY_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("✅ Your Head Coach application has been submitted!", ephemeral=True)

@tree.command(name="hcapply", description="Apply for Head Coach position")
async def hcapply(interaction: discord.Interaction):
    await interaction.response.send_modal(HCApplyModal())

# ====================== CLEAR STATS ======================
@tree.command(name="clearstats", description="Clear stats for a user (Analytics role only)")
@app_commands.describe(username="Username", position="Position")
@app_commands.choices(position=[
    app_commands.Choice(name="Quarterback (QB)", value="Quarterback (QB)"),
    app_commands.Choice(name="Runningback (RB)", value="Runningback (RB)"),
    app_commands.Choice(name="Wide Receiver (WR)", value="Wide Receiver (WR)"),
    app_commands.Choice(name="Tight End (TE)", value="Tight End (TE)"),
    app_commands.Choice(name="Center (C)", value="Center (C)"),
    app_commands.Choice(name="Defensive End (DE)", value="Defensive End (DE)"),
    app_commands.Choice(name="Linebacker (LB)", value="Linebacker (LB)"),
    app_commands.Choice(name="Defensive Back (DB)", value="Defensive Back (DB)"),
    app_commands.Choice(name="Kicker (K)", value="Kicker (K)"),
])
async def clearstats(interaction: discord.Interaction, username: str, position: str):
    if ANALYTICS_ROLE_ID != 0 and not interaction.user.get_role(ANALYTICS_ROLE_ID):
        await interaction.response.send_message("❌ You need the Analytics role to use this command.", ephemeral=True)
        return

    username = username.strip()

    if username in user_stats and position in user_stats[username]:
        del user_stats[username][position]
        save_stats()
        await interaction.response.send_message(f"✅ Cleared **{position}** stats for **{username}**.", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ No stats found for **{username}** in **{position}**.", ephemeral=True)

def get_rank(elo: int) -> str:
    if elo < 1000: return "Bronze"
    elif elo < 1500: return "Silver"
    elif elo < 2000: return "Gold"
    elif elo < 2500: return "Crowns"
    elif elo < 3500: return "Titles"
    else: return "Elite"

def calculate_elo_change(winner_elo: int, loser_elo: int):
    if winner_elo == loser_elo:
        return 50, -50
    diff = abs(winner_elo - loser_elo)
    if winner_elo > loser_elo:
        loss = max(30, 50 - (diff // 20))
        return 30, -loss
    else:
        gain = min(70, 50 + (diff // 15))
        return gain, -30

last_leaderboard_msg_id = None

async def update_qbb_leaderboard():
    global last_leaderboard_msg_id

    if QBB_ELO_LEADERBOARD_CHANNEL_ID == 0:
        return

    channel = client.get_channel(QBB_ELO_LEADERBOARD_CHANNEL_ID)
    if not channel:
        return

    players = qbb_data.get("players", {})
    if not players:
        return

    # Sort by ELO
    sorted_players = sorted(players.items(), key=lambda x: x[1].get("elo", 1000), reverse=True)

    embed = discord.Embed(title="🏆 QBB ELO LEADERBOARD", color=0xFFFFFF)  # White color
    text = ""

    for i, (username, data) in enumerate(sorted_players[:15], 1):
        elo = data.get("elo", 1000)
        rank = get_rank(elo)
        text += f"**#{i}** {username} **{rank}** {elo} ELO\n"

    embed.description = text

    # Edit previous message if it exists
    if last_leaderboard_msg_id:
        try:
            msg = await channel.fetch_message(last_leaderboard_msg_id)
            await msg.edit(embed=embed)
            return
        except:
            pass  # Message was deleted, send new one

    # Send new message and save ID
    new_msg = await channel.send(embed=embed)
    last_leaderboard_msg_id = new_msg.id

# ====================== STATS ======================
@tree.command(name="stats", description="View stats for a user")
@app_commands.describe(position="Select position", username="Username")
@app_commands.choices(position=[
    app_commands.Choice(name="Quarterback (QB)", value="Quarterback (QB)"),
    app_commands.Choice(name="Runningback (RB)", value="Runningback (RB)"),
    app_commands.Choice(name="Wide Receiver (WR)", value="Wide Receiver (WR)"),
    app_commands.Choice(name="Tight End (TE)", value="Tight End (TE)"),
    app_commands.Choice(name="Center (C)", value="Center (C)"),
    app_commands.Choice(name="Defensive End (DE)", value="Defensive End (DE)"),
    app_commands.Choice(name="Linebacker (LB)", value="Linebacker (LB)"),
    app_commands.Choice(name="Defensive Back (DB)", value="Defensive Back (DB)"),
    app_commands.Choice(name="Kicker (K)", value="Kicker (K)"),
])
async def stats(interaction: discord.Interaction, position: str, username: str):
    username = username.strip()
    pos_stats = user_stats.get(username, {}).get(position, {})

    if not pos_stats:
        await interaction.response.send_message(
            f"❌ No stats found at **{position}** for **{username}**.",
            ephemeral=True
        )
        return

    embed = discord.Embed(color=0xFFFFFF)
    embed.description = f"**{username}**\n\nPosition: **{position}**\n"

    if position == "Quarterback (QB)":
        comp_rate = pos_stats.get('comp_rate', 'N/A')
        embed.description += f"\n**Comp. Rate**\n{comp_rate}"

        # Auto calculate percentage
        if comp_rate and "/" in comp_rate:
            try:
                comp, att = map(int, comp_rate.split("/"))
                if att > 0:
                    pct = round((comp / att) * 100)
                    embed.description += f"  **{pct}%**"
            except:
                pass

        embed.description += f"\n\n**Yards**\n{pos_stats.get('yards', 'N/A')}"
        embed.description += f"\n\n**Touchdowns**\n{pos_stats.get('touchdowns', 'N/A')}"

        # Interceptions / Fumbles
        int_fumbles = pos_stats.get('interceptions_fumbles', '0 / 0')
        try:
            parts = int_fumbles.replace(" ", "").split("/")
            ints = parts[0] if len(parts) > 0 else "0"
            fumbles = parts[1] if len(parts) > 1 else "0"
            embed.description += f"\n\n**Interceptions**\n{ints}"
            embed.description += f"\n\n**Fumbles**\n{fumbles}"
        except:
            embed.description += f"\n\n**Interceptions**\n0"
            embed.description += f"\n\n**Fumbles**\n0"

    elif position == "Runningback (RB)":
        embed.description += f"\n**Rush Attempts**\n{pos_stats.get('rush_attempts', 'N/A')}"
        embed.description += f"\n\n**Yards**\n{pos_stats.get('yards', 'N/A')}"
        embed.description += f"\n\n**Touchdowns**\n{pos_stats.get('touchdowns', 'N/A')}"
        embed.description += f"\n\n**Fumbles**\n{pos_stats.get('fumbles', 'N/A')}"

    elif position in ["Wide Receiver (WR)", "Tight End (TE)"]:
        embed.description += f"\n**Yards**\n{pos_stats.get('yards', 'N/A')}"
        embed.description += f"\n\n**Touchdowns**\n{pos_stats.get('touchdowns', 'N/A')}"
        embed.description += f"\n\n**Receptions**\n{pos_stats.get('receptions', 'N/A')}"
        embed.description += f"\n\n**Targets**\n{pos_stats.get('targets', 'N/A')}"

    elif position == "Center (C)":
        embed.description += f"\n**Sacks Allowed**\n{pos_stats.get('sacks_allowed', 'N/A')}"
        embed.description += f"\n\n**Snaps**\n{pos_stats.get('snaps', 'N/A')}"
        embed.description += f"\n\n**Pressures**\n{pos_stats.get('pressures', 'N/A')}"

    elif position == "Defensive End (DE)":
        embed.description += f"\n**Sacks**\n{pos_stats.get('sacks', 'N/A')}"
        embed.description += f"\n\n**Tackles**\n{pos_stats.get('tackles', 'N/A')}"
        embed.description += f"\n\n**Tackles For Loss**\n{pos_stats.get('tackles_for_loss', 'N/A')}"
        embed.description += f"\n\n**Pressures**\n{pos_stats.get('pressures', 'N/A')}"

    elif position == "Linebacker (LB)":
        embed.description += f"\n**Interceptions**\n{pos_stats.get('interceptions', 'N/A')}"
        embed.description += f"\n\n**Tackles**\n{pos_stats.get('tackles', 'N/A')}"
        embed.description += f"\n\n**Catches Allowed**\n{pos_stats.get('catches_allowed', 'N/A')}"
        embed.description += f"\n\n**Targets**\n{pos_stats.get('targets', 'N/A')}"

    elif position == "Defensive Back (DB)":
        embed.description += f"\n**Interceptions**\n{pos_stats.get('interceptions', 'N/A')}"
        embed.description += f"\n\n**Tackles**\n{pos_stats.get('tackles', 'N/A')}"
        embed.description += f"\n\n**Targets**\n{pos_stats.get('targets', 'N/A')}"
        embed.description += f"\n\n**Catches Allowed**\n{pos_stats.get('catches_allowed', 'N/A')}"

    elif position == "Kicker (K)":
        embed.description += f"\n**Kick Percentage**\n{pos_stats.get('kick_percentage', 'N/A')}"
        embed.description += f"\n\n**Good Kicks**\n{pos_stats.get('good_kicks', 'N/A')}"
        embed.description += f"\n\n**Attempts**\n{pos_stats.get('attempts', 'N/A')}"
        embed.description += f"\n\n**Long**\n{pos_stats.get('long', 'N/A')}"

    await interaction.response.send_message(embed=embed)

# ====================== ANALYTICS ======================
class StatsInputModal(discord.ui.Modal, title="Enter / Update Stats"):
    def __init__(self, position: str):
        super().__init__(title=f"Stats - {position}")
        self.position = position

        self.add_item(discord.ui.TextInput(label="Username", placeholder="AzoWasTaken", required=True))

        if position == "Quarterback (QB)":
            self.add_item(discord.ui.TextInput(label="Comp. Rate", placeholder="22/31", required=False))
            self.add_item(discord.ui.TextInput(label="Yards", placeholder="309", required=False))
            self.add_item(discord.ui.TextInput(label="Touchdowns", placeholder="5", required=False))
            self.add_item(discord.ui.TextInput(label="Interceptions / Fumbles", placeholder="2 / 3", required=False))

        elif position == "Runningback (RB)":
            self.add_item(discord.ui.TextInput(label="Rush Attempts", placeholder="12", required=False))
            self.add_item(discord.ui.TextInput(label="Yards", placeholder="91", required=False))
            self.add_item(discord.ui.TextInput(label="Touchdowns", placeholder="1", required=False))
            self.add_item(discord.ui.TextInput(label="Fumbles", placeholder="2", required=False))

        elif position == "Wide Receiver (WR)":
            self.add_item(discord.ui.TextInput(label="Yards", placeholder="91", required=False))
            self.add_item(discord.ui.TextInput(label="Touchdowns", placeholder="1", required=False))
            self.add_item(discord.ui.TextInput(label="Receptions", placeholder="4", required=False))
            self.add_item(discord.ui.TextInput(label="Targets", placeholder="7", required=False))

        elif position == "Tight End (TE)":
            self.add_item(discord.ui.TextInput(label="Yards", placeholder="42", required=False))
            self.add_item(discord.ui.TextInput(label="Touchdowns", placeholder="1", required=False))
            self.add_item(discord.ui.TextInput(label="Receptions", placeholder="4", required=False))
            self.add_item(discord.ui.TextInput(label="Targets", placeholder="7", required=False))

        elif position == "Center (C)":
            self.add_item(discord.ui.TextInput(label="Sacks Allowed", placeholder="1", required=False))
            self.add_item(discord.ui.TextInput(label="Snaps", placeholder="45", required=False))
            self.add_item(discord.ui.TextInput(label="Pressures", placeholder="32", required=False))

        elif position == "Defensive End (DE)":
            self.add_item(discord.ui.TextInput(label="Sacks", placeholder="2", required=False))
            self.add_item(discord.ui.TextInput(label="Tackles", placeholder="9", required=False))
            self.add_item(discord.ui.TextInput(label="Tackles For Loss", placeholder="2", required=False))
            self.add_item(discord.ui.TextInput(label="Pressures", placeholder="11", required=False))

        elif position == "Linebacker (LB)":
            self.add_item(discord.ui.TextInput(label="Interceptions", placeholder="4", required=False))
            self.add_item(discord.ui.TextInput(label="Tackles", placeholder="19", required=False))
            self.add_item(discord.ui.TextInput(label="Catches Allowed", placeholder="2", required=False))
            self.add_item(discord.ui.TextInput(label="Targets", placeholder="10", required=False))

        elif position == "Defensive Back (DB)":
            self.add_item(discord.ui.TextInput(label="Interceptions", placeholder="7", required=False))
            self.add_item(discord.ui.TextInput(label="Tackles", placeholder="10", required=False))
            self.add_item(discord.ui.TextInput(label="Targets", placeholder="32", required=False))
            self.add_item(discord.ui.TextInput(label="Catches Allowed", placeholder="9", required=False))

        elif position == "Kicker (K)":
            self.add_item(discord.ui.TextInput(label="Kick Percentage", placeholder="98.2%", required=False))
            self.add_item(discord.ui.TextInput(label="Good Kicks", placeholder="26", required=False))
            self.add_item(discord.ui.TextInput(label="Attempts", placeholder="27", required=False))
            self.add_item(discord.ui.TextInput(label="Long", placeholder="42", required=False))

    async def on_submit(self, interaction: discord.Interaction):
        username = self.children[0].value.strip()
        values = {}

        for child in self.children[1:]:
            if child.value:
                label = child.label.lower()

                # Clean key names properly
                if "comp" in label:
                    key = "comp_rate"
                elif "interceptions" in label and "fumbles" in label:
                    key = "interceptions_fumbles"
                else:
                    key = label.replace(" ", "_").replace("/", "_")

                values[key] = child.value.strip()

        if username not in user_stats:
            user_stats[username] = {}
        user_stats[username][self.position] = values
        save_stats()

        await interaction.response.send_message(f"✅ Stats saved for **{username}** as **{self.position}**!", ephemeral=True)


@tree.command(name="analytics", description="Enter or update stats (Analytics role only)")
@app_commands.describe(position="Select position")
@app_commands.choices(position=[
    app_commands.Choice(name="Quarterback (QB)", value="Quarterback (QB)"),
    app_commands.Choice(name="Runningback (RB)", value="Runningback (RB)"),
    app_commands.Choice(name="Wide Receiver (WR)", value="Wide Receiver (WR)"),
    app_commands.Choice(name="Tight End (TE)", value="Tight End (TE)"),
    app_commands.Choice(name="Center (C)", value="Center (C)"),
    app_commands.Choice(name="Defensive End (DE)", value="Defensive End (DE)"),
    app_commands.Choice(name="Linebacker (LB)", value="Linebacker (LB)"),
    app_commands.Choice(name="Defensive Back (DB)", value="Defensive Back (DB)"),
    app_commands.Choice(name="Kicker (K)", value="Kicker (K)"),
])
async def analytics(interaction: discord.Interaction, position: str):
    if ANALYTICS_ROLE_ID != 0 and not interaction.user.get_role(ANALYTICS_ROLE_ID):
        await interaction.response.send_message("❌ You need the Analytics role to use this command.", ephemeral=True)
        return

    await interaction.response.send_modal(StatsInputModal(position=position))

# ====================== ROSTER ======================
@tree.command(name="roster", description="Show team roster publicly")
@app_commands.describe(team="Select team")
@app_commands.choices(team=[app_commands.Choice(name=name, value=name) for name in TEAM_ROLES.keys()])
async def roster(interaction: discord.Interaction, team: str):
    if team not in TEAM_ROLES:
        await interaction.response.send_message("❌ Invalid team.", ephemeral=True)
        return

    team_role = interaction.guild.get_role(TEAM_ROLES[team])
    if not team_role:
        await interaction.response.send_message("❌ Team role not found.", ephemeral=True)
        return

    head_coaches = [m.mention for m in interaction.guild.members if m.get_role(HEAD_COACH_ROLE_ID) and m.get_role(TEAM_ROLES[team])]
    ast_coaches = [m.mention for m in interaction.guild.members if m.get_role(ASSISTANT_COACH_ROLE_ID) and m.get_role(TEAM_ROLES[team])]
    players = [m.mention for m in interaction.guild.members if m.get_role(TEAM_ROLES[team]) and not m.get_role(HEAD_COACH_ROLE_ID) and not m.get_role(ASSISTANT_COACH_ROLE_ID)]

    embed = discord.Embed(title=f"{team} Roster", color=0x00FFFF)
    embed.add_field(name="Head Coach", value=head_coaches[0] if head_coaches else "None", inline=False)
    embed.add_field(name="Assistant Coaches", value="\n".join(ast_coaches) if ast_coaches else "None", inline=False)
    embed.add_field(name="Players", value="\n".join(players) if players else "None", inline=False)

    await interaction.response.send_message(embed=embed)  # Public


# ====================== TEAM SWAP ======================
class TeamSwapView(discord.ui.View):
    def __init__(self, team_a, team_b):
        super().__init__(timeout=60)
        self.team_a = team_a
        self.team_b = team_b

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Swap logic
        role_a = interaction.guild.get_role(TEAM_ROLES[self.team_a])
        role_b = interaction.guild.get_role(TEAM_ROLES[self.team_b])

        for member in interaction.guild.members:
            if member.get_role(TEAM_ROLES[self.team_a]):
                await member.remove_roles(role_a)
                await member.add_roles(role_b)
            elif member.get_role(TEAM_ROLES[self.team_b]):
                await member.remove_roles(role_b)
                await member.add_roles(role_a)

        await interaction.response.edit_message(content=f"✅ Successfully swapped **{self.team_a}** with **{self.team_b}**!", view=None)

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Team swap cancelled.", view=None)


@tree.command(name="teamswap", description="Swap two teams (Admin only)")
@app_commands.describe(team_a="Team A", team_b="Team B")
@app_commands.choices(team_a=[app_commands.Choice(name=name, value=name) for name in TEAM_ROLES.keys()],
                      team_b=[app_commands.Choice(name=name, value=name) for name in TEAM_ROLES.keys()])
async def teamswap(interaction: discord.Interaction, team_a: str, team_b: str):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only Admins can use this command.", ephemeral=True)
        return
    if team_a == team_b:
        await interaction.response.send_message("❌ You cannot swap a team with itself.", ephemeral=True)
        return

    await interaction.response.send_message(
        f"Are you sure you want to swap **{team_a}** with **{team_b}**?",
        view=TeamSwapView(team_a, team_b),
        ephemeral=True
    )


# ====================== COMMIT ======================
@tree.command(name="commit", description="Commit to a team")
@app_commands.describe(team="Select your team")
@app_commands.choices(team=[app_commands.Choice(name=name, value=name) for name in TEAM_ROLES.keys()])
async def commit(interaction: discord.Interaction, team: str):
    if team not in TEAM_ROLES or TEAM_ROLES[team] == 0:
        await interaction.response.send_message("❌ Team not set up yet.", ephemeral=True)
        return

    member = interaction.user
    current_team, current_role_id = get_user_team(member)

    # Remove from old team if already on one
    if current_role_id:
        old_role = interaction.guild.get_role(current_role_id)
        if old_role:
            await member.remove_roles(old_role)

    role = interaction.guild.get_role(TEAM_ROLES[team])
    if role:
        await member.add_roles(role)
        await interaction.response.send_message(f"✅ You committed to **{team}**!", ephemeral=True)
        role_mention = f"<@&{TEAM_ROLES[team]}>"
        desc = f"**{interaction.user.mention}** has committed to {role_mention}"
        await log_transaction(interaction, "Commitment", desc, 0xFFC1E3, team)

# ====================== TRANSFER ======================
@tree.command(name="transfer", description="Transfer to a different team")
@app_commands.describe(team="Select new team")
@app_commands.choices(team=[app_commands.Choice(name=name, value=name) for name in TEAM_ROLES.keys()])
async def transfer(interaction: discord.Interaction, team: str):
    if team not in TEAM_ROLES or TEAM_ROLES[team] == 0:
        await interaction.response.send_message("❌ Invalid team.", ephemeral=True)
        return
    member = interaction.user
    current_team, current_role_id = get_user_team(member)
    if not current_team:
        await interaction.response.send_message("❌ You are not on any team!", ephemeral=True)
        return
    if current_team == team:
        await interaction.response.send_message("❌ You are already on that team!", ephemeral=True)
        return
    has_no_transfers = member.get_role(NO_TRANSFERS_ROLE_ID)
    has_extra = any(member.get_role(rid) for rid in [EXTRA_TRANSFER_1_ROLE_ID, EXTRA_TRANSFER_2_ROLE_ID, EXTRA_TRANSFER_3_ROLE_ID])
    if has_no_transfers and not has_extra:
        await interaction.response.send_message("❌ You have no transfers left.", ephemeral=True)
        return
    new_role = interaction.guild.get_role(TEAM_ROLES[team])
    old_role = interaction.guild.get_role(current_role_id)
    if old_role: await member.remove_roles(old_role)
    if new_role: await member.add_roles(new_role)
    for rid in [EXTRA_TRANSFER_1_ROLE_ID, EXTRA_TRANSFER_2_ROLE_ID, EXTRA_TRANSFER_3_ROLE_ID]:
        role = interaction.guild.get_role(rid)
        if role and member.get_role(rid):
            await member.remove_roles(role)
    no_transfer_role = interaction.guild.get_role(NO_TRANSFERS_ROLE_ID)
    if no_transfer_role: await member.add_roles(no_transfer_role)
    await interaction.response.send_message(f"✅ Transferred from **{current_team}** to **{team}**!", ephemeral=True)
    old_mention = f"<@&{current_role_id}>"
    new_mention = f"<@&{TEAM_ROLES[team]}>"
    desc = f"**{interaction.user.mention}** has transferred from {old_mention} to {new_mention}"
    await log_transaction(interaction, "Transfer", desc, 0xA8E6A1, team)


# ====================== PROMOTE ======================
@tree.command(name="promote", description="Promote a player (Head Coach only)")
@app_commands.describe(member="Player to promote")
async def promote(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.get_role(HEAD_COACH_ROLE_ID):
        await interaction.response.send_message("❌ Only Head Coaches can promote.", ephemeral=True)
        return
    coach_team, _ = get_user_team(interaction.user)
    player_team, _ = get_user_team(member)
    if not coach_team or coach_team != player_team:
        await interaction.response.send_message("❌ You can only promote players on your own team.", ephemeral=True)
        return
    ast_role = interaction.guild.get_role(ASSISTANT_COACH_ROLE_ID)
    if ast_role:
        await member.add_roles(ast_role)
    await interaction.response.send_message(f"✅ You promoted **{member}** to Assistant Coach!", ephemeral=True)
    ast_mention = f"<@&{ASSISTANT_COACH_ROLE_ID}>"
    team_mention = f"<@&{TEAM_ROLES[coach_team]}>"
    desc = f"**{interaction.user.mention}** has promoted **{member.mention}** to {ast_mention} on {team_mention}"
    await log_transaction(interaction, "Promotion", desc, 0xFFF7A3, coach_team)


# ====================== ACCOUNT SWITCH ======================
@tree.command(name="accountswitch", description="Request an account switch")
@app_commands.describe(username="New Username", reason="Reason for switching")
async def accountswitch(interaction: discord.Interaction, username: str, reason: str):
    embed = discord.Embed(title="🔄 Account Switch Request", color=0xFFD700)
    embed.add_field(name="User", value=interaction.user.mention, inline=False)
    embed.add_field(name="New Username", value=username, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)

    channel = interaction.guild.get_channel(ACCOUNT_SWITCH_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)

    await interaction.response.send_message("✅ Account switch request submitted!", ephemeral=True)


# ====================== SCOUT ======================
@tree.command(name="scout", description="Submit a scout report")
@app_commands.describe(
    roblox_username="Roblox Username",
    off_primary="Offensive Primary Position",
    def_primary="Defensive Primary Position",
    off_secondary="Offensive Secondary Position",
    def_secondary="Defensive Secondary Position",
    notes="Additional Notes",
    film_link="Film / Highlight Link"
)
async def scout(interaction: discord.Interaction, roblox_username: str, off_primary: str, def_primary: str,
                off_secondary: str, def_secondary: str, notes: str, film_link: str):
    
    # Roblox avatar (simple method)
    avatar_url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds=1&size=420x420&format=Png&isCircular=false"

    embed = discord.Embed(title="🔍 Scout Report", color=0xFF0000)  # Red left line
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="Roblox Username", value=roblox_username, inline=False)
    embed.add_field(name="Offensive Primary", value=off_primary, inline=True)
    embed.add_field(name="Defensive Primary", value=def_primary, inline=True)
    embed.add_field(name="Offensive Secondary", value=off_secondary, inline=True)
    embed.add_field(name="Defensive Secondary", value=def_secondary, inline=True)
    embed.add_field(name="Notes", value=notes, inline=False)
    embed.add_field(name="Film / Link", value=film_link, inline=False)
    embed.set_footer(text=f"Scouted by {interaction.user}")

    channel = interaction.guild.get_channel(SCOUT_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)

    await interaction.response.send_message("✅ Scout report submitted!", ephemeral=True)


# ====================== COLOR ======================
@tree.command(name="color", description="Choose a color role (Boosters only)")
@app_commands.describe(color="Select color")
@app_commands.choices(color=[app_commands.Choice(name=name, value=name) for name in COLOR_ROLES.keys()])
async def color(interaction: discord.Interaction, color: str):
    if not interaction.user.get_role(BOOSTER_ROLE_ID):
        await interaction.response.send_message("❌ Only Server Boosters can use this command.", ephemeral=True)
        return
    if color not in COLOR_ROLES:
        await interaction.response.send_message("❌ Invalid color.", ephemeral=True)
        return
    for role_id in COLOR_ROLES.values():
        role = interaction.guild.get_role(role_id)
        if role and interaction.user.get_role(role_id):
            await interaction.user.remove_roles(role)
    new_role = interaction.guild.get_role(COLOR_ROLES[color])
    if new_role:
        await interaction.user.add_roles(new_role)
        await interaction.response.send_message(f"✅ You now have the **{color}** color!", ephemeral=True)


# ====================== SERVERS ======================
@tree.command(name="servers", description="Get affiliated server links")
async def servers(interaction: discord.Interaction):
    await interaction.response.send_message("✅ I've sent you the ACFU affiliated servers in DM!", ephemeral=True)
    message = "**ACFU Affiliated Servers:**\n\n" + "\n".join(AFFILIATED_SERVERS)
    try:
        await interaction.user.send(message)
    except:
        await interaction.followup.send("❌ Could not DM you. Please enable DMs from server members.", ephemeral=True)

# ====================== QBB ======================
async def get_roblox_username(member: discord.Member) -> str:
    discord_id = member.id
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
            async with session.get(f"https://api.blox.link/v4/public/discord/{discord_id}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success") and data.get("user"):
                        roblox_name = data["user"].get("robloxUsername")
                        if roblox_name:
                            return roblox_name
    except:
        pass
    return member.display_name or member.name


@tree.command(name="qbb", description="Queue for QBB Matchmaking (Captains only)")
@app_commands.describe(opponent="Opponent Captain", code="6-character code")
async def qbb(interaction: discord.Interaction, opponent: discord.Member, code: str):
    global last_qbb_time

    await interaction.response.defer(ephemeral=True)

    if not interaction.user.get_role(CAPTAIN_ROLE_ID):
        await interaction.followup.send("❌ Only Captains can use this command.", ephemeral=True)
        return
    if not opponent.get_role(CAPTAIN_ROLE_ID):
        await interaction.followup.send("❌ Opponent must have Captain role.", ephemeral=True)
        return
    if len(code) != 6:
        await interaction.followup.send("❌ Code must be exactly 6 characters.", ephemeral=True)
        return

    current_time = time.time()
    time_left = last_qbb_time + QBB_COOLDOWN - current_time
    if time_left > 0:
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        await interaction.followup.send(f"⏳ **{minutes}m {seconds}s** left until QBB opens.", ephemeral=True)
        return

    p1_roblox = await get_roblox_username(interaction.user)
    p2_roblox = await get_roblox_username(opponent)

    p1_elo = qbb_data["players"].get(p1_roblox, {}).get("elo", 1000)
    p2_elo = qbb_data["players"].get(p2_roblox, {}).get("elo", 1000)

    p1_rank = get_rank(p1_elo)
    p2_rank = get_rank(p2_elo)

    p1_emoji = QBB_RANK_EMOJIS.get(p1_rank, "")
    p2_emoji = QBB_RANK_EMOJIS.get(p2_rank, "")

    comp_channel = interaction.guild.get_channel(COMPETITION_CHANNEL_ID)
    if comp_channel:
        msg = (
            f"{p1_emoji} {p1_elo} {interaction.user.mention} (@{p1_roblox}) vs "
            f"{p2_emoji} {p2_elo} {opponent.mention} (@{p2_roblox}) – {code.upper()} @here"
        )
        await comp_channel.send(msg)

    await interaction.followup.send("✅ QBB match posted!", ephemeral=True)
    last_qbb_time = current_time

# ====================== QBB RANK EMOJIS ======================
# Put your custom emoji IDs here. Leave blank ("") if you don't want an emoji for that rank.
QBB_RANK_EMOJIS = {
    "Bronze": "<:StaffOTY:1510741535707369644>",      # Replace with your emoji ID
    "Silver": "<:PositionOTY:1510744095063015556>",
    "Gold": "<:MVP:1510744025840222361>",
    "Crowns": "<:y_crowns:1510743986086871303>",
    "Titles": "<:Title:1510743951257370696>",
}

# ====================== QBB ELO COMMANDS ======================

@tree.command(name="claim", description="Claim your QBB win (You are the winner)")
@app_commands.describe(opponent="The player you beat", match_code="The 6-character code from the match")
async def claim(interaction: discord.Interaction, opponent: discord.Member, match_code: str):
    if not interaction.user.get_role(CAPTAIN_ROLE_ID):
        await interaction.response.send_message("❌ Only Captains can claim matches.", ephemeral=True)
        return

    winner_name = interaction.user.display_name
    loser_name = opponent.display_name

    # Initialize players if they don't exist
    if winner_name not in qbb_data["players"]:
        qbb_data["players"][winner_name] = {"elo": 1000}
    if loser_name not in qbb_data["players"]:
        qbb_data["players"][loser_name] = {"elo": 1000}

    winner_elo = qbb_data["players"][winner_name]["elo"]
    loser_elo = qbb_data["players"][loser_name]["elo"]

    if winner_name == loser_name:
        await interaction.response.send_message("❌ You can't claim against yourself.", ephemeral=True)
        return

    # Calculate ELO change
    gain, loss = calculate_elo_change(winner_elo, loser_elo)

    # Apply ELO changes
    qbb_data["players"][winner_name]["elo"] += gain
    qbb_data["players"][loser_name]["elo"] += loss

    # Record the match
    match_entry = {
        "match_id": qbb_data["next_match_id"],
        "player1": winner_name,
        "player2": loser_name,
        "code": match_code.upper(),
        "winner": winner_name,
        "elo_change": {winner_name: gain, loser_name: loss}
    }
    qbb_data["matches"].append(match_entry)
    qbb_data["next_match_id"] += 1

    save_qbb_data()

    # Refresh leaderboard
    await update_qbb_leaderboard()

    await interaction.response.send_message(
        f"✅ **{winner_name}** wins!\n"
        f"**{winner_name}** gained **+{gain}** ELO\n"
        f"**{loser_name}** lost **{abs(loss)}** ELO",
        ephemeral=True
    )


@tree.command(name="setelo", description="Set a user's ELO (Admin only)")
@app_commands.describe(user="User to modify", elo="New ELO value")
async def setelo(interaction: discord.Interaction, user: discord.Member, elo: int):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return

    name = user.display_name
    if name not in qbb_data["players"]:
        qbb_data["players"][name] = {"elo": 1000}

    qbb_data["players"][name]["elo"] = elo
    save_qbb_data()
    await update_qbb_leaderboard()

    await interaction.response.send_message(f"✅ Set **{name}** ELO to **{elo}**.", ephemeral=True)


@tree.command(name="resetqbb", description="Reset or manage QBB matches (Admin only)")
@app_commands.describe(action="What do you want to do?")
@app_commands.choices(action=[
    app_commands.Choice(name="Void Last Match", value="void_last"),
    app_commands.Choice(name="Show History", value="history"),
])
async def resetqbb(interaction: discord.Interaction, action: str):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return

    if action == "void_last":
        if not qbb_data["matches"]:
            await interaction.response.send_message("No matches to void.", ephemeral=True)
            return
        last = qbb_data["matches"].pop()
        save_qbb_data()
        await interaction.response.send_message(f"✅ Voided match #{last['match_id']}.", ephemeral=True)

    elif action == "history":
        if not qbb_data["matches"]:
            await interaction.response.send_message("No QBB history yet.", ephemeral=True)
            return
        text = "**QBB Match History:**\n"
        for m in qbb_data["matches"][-10:]:
            text += f"#{m['match_id']} {m['player1']} vs {m['player2']} - {m['code']} (Winner: {m.get('winner', 'N/A')})\n"
        await interaction.response.send_message(text, ephemeral=True)

# ====================== INTERN / VERIFIED ROLE ======================
@tree.command(name="intern", description="Give a player the Verified role (Head Coach only)")
@app_commands.describe(player="Player to give Verified role")
async def intern(interaction: discord.Interaction, player: discord.Member):
    if not interaction.user.get_role(HEAD_COACH_ROLE_ID):
        await interaction.response.send_message("❌ Only Head Coaches can use this command.", ephemeral=True)
        return

    if VERIFIED_ROLE_ID == 0:
        await interaction.response.send_message("❌ Verified role is not set up.", ephemeral=True)
        return

    coach_team, _ = get_user_team(interaction.user)
    player_team, _ = get_user_team(player)

    if not coach_team or coach_team != player_team:
        await interaction.response.send_message("❌ You can only verify players on your own team.", ephemeral=True)
        return

    verified_role = interaction.guild.get_role(VERIFIED_ROLE_ID)
    if not verified_role:
        await interaction.response.send_message("❌ Verified role not found.", ephemeral=True)
        return

    # Count current verified players on team
    verified_count = 0
    verified_members = []
    for member in interaction.guild.members:
        if member.get_role(TEAM_ROLES[coach_team]) and member.get_role(VERIFIED_ROLE_ID):
            verified_count += 1
            verified_members.append(member)

    if player.get_role(VERIFIED_ROLE_ID):
        await interaction.response.send_message("❌ This player already has the Verified role.", ephemeral=True)
        return

    if verified_count >= 3:
        class RemoveView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)

            @discord.ui.button(label="Yes, remove one", style=discord.ButtonStyle.green)
            async def yes(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                if button_interaction.user.id != interaction.user.id:
                    await button_interaction.response.send_message("❌ Only the Head Coach can do this.", ephemeral=True)
                    return

                options = []
                for i, m in enumerate(verified_members):
                    options.append(discord.SelectOption(label=m.display_name, value=str(m.id)))

                class RemoveSelect(discord.ui.Select):
                    def __init__(self):
                        super().__init__(placeholder="Select a player to remove Verified from", options=options)

                    async def callback(self, select_interaction: discord.Interaction):
                        selected_id = int(self.values[0])
                        selected_member = interaction.guild.get_member(selected_id)
                        if selected_member and selected_member.get_role(VERIFIED_ROLE_ID):
                            await selected_member.remove_roles(verified_role)
                            await select_interaction.response.send_message(
                                f"✅ Removed Verified from **{selected_member.display_name}**.", ephemeral=True
                            )
                            self.view.stop()

                select_view = discord.ui.View()
                select_view.add_item(RemoveSelect())
                await button_interaction.response.send_message("Select who to remove:", view=select_view, ephemeral=True)

            @discord.ui.button(label="No", style=discord.ButtonStyle.red)
            async def no(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                await button_interaction.response.send_message("Cancelled.", ephemeral=True)
                self.stop()

        await interaction.response.send_message(
            "❌ You have already reached the limit of **3/3** verified players on your team.\n"
            "Would you like to remove one?",
            view=RemoveView(),
            ephemeral=True
        )
        return

    # Give role
    await player.add_roles(verified_role)
    await interaction.response.send_message(
        f"✅ Gave **{player.display_name}** the Verified role.\n"
        f"**{verified_count + 1}/3** verified players on **{coach_team}**.",
        ephemeral=True
    )


# Run the bot
client.run("TOKEN")