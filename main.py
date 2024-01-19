import os
import discord
from discord import app_commands 
from discord import Interaction
import paramiko
import gspread
from google.oauth2.service_account import Credentials
import config
import Statistics

# 必要なIntentsを有効化します
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

# clientを初期化します
Dsclient = discord.Client(intents=intents)
tree = app_commands.CommandTree(Dsclient)
Sshclient = paramiko.SSHClient()
Sshclient.set_missing_host_key_policy(paramiko.WarningPolicy())

# Discord Botの準備ができたら実行する処理を追加します
@Dsclient.event
async def on_ready():
  print(f'Logged in as {Dsclient.user}')
  await tree.sync()

async def is_admin(interaction: Interaction):
    return interaction.user.guild_permissions.administrator

# メンバー参加イベントを処理します
@Dsclient.event
async def on_member_join(member):
  joined_time = member.joined_at.strftime('%Y-%m-%d %H:%M:%S')
  await update_google_spreadsheet(member.name, joined_time)
  print('Spreadsheet updated successfully.')


# Googleスプレッドシートに書き込むための関数
async def update_google_spreadsheet(member_name, joined_time):
  scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
  ]
  credentials = Credentials.from_service_account_file(config.CREDENTIALS_JSON,
                                                      scopes=scope)
  gc = gspread.authorize(credentials)
  doc = gc.open_by_key(config.SPREADSHEET_KEY)
  sheet = doc.get_worksheet(0)  # デフォルトのシートを使用します（最初のシートを使用します）
  sheet.append_row([member_name, joined_time])

# コマンドを実装します
@tree.command(name='start',description='サーバーを起動します')
async def start(interaction: Interaction,text:str):
    server_commands = {
        'main': config.START_MAIN,
        'sigen': config.START_SIGEN,
        'azkaban': config.START_AZKABAN,
        'rsfab': config.START_RSFAB,
        'lobby': config.START_LOBBY,
        'event1':config.START_EVENT1,
        'event2':config.START_EVENT2,
        'exp':config.START_EXP
    }
    if await is_admin(interaction):
        if text in server_commands:
            start_command = server_commands[text]
            ConnectSSH()
            # SSHクライアントを使用してコマンドを実行する
            stdin, stdout, stderr = Sshclient.exec_command(start_command)
            await interaction.response.send_message('サーバー起動リクエストが送信されました\nしばらくしても起動しない場合は運営に報告してください')
        else:
            await interaction.response.send_message('無効なサーバー名です')
    else:
        await interaction.response.send_message('このコマンドは管理者のみが使用できます')

@tree.command(name='restart',description='サーバーを再起動します')
async def restart(interaction: Interaction,text:str):
    restart_commands = {
        'exp': config.RESTART_EXP,
        'main':config.RESTART_MAIN
    }
    if await is_admin(interaction):
        if text in restart_commands:
            start_command = restart_commands[text]
            ConnectSSH()
            # SSHクライアントを使用してコマンドを実行する
            stdin, stdout, stderr = Sshclient.exec_command(start_command)
            await interaction.response.send_message('サーバー再起動リクエストが送信されました\nしばらくしても起動しない場合は運営に報告してください')
        else:
            await interaction.response.send_message('無効なサーバー名です')
    else:
        await interaction.response.send_message('このコマンドは管理者のみが使用できます')

def ConnectSSH():
  Sshclient.connect(hostname=config.HOSTNAME, 
  port=22, 
  username=config.USERNAME,
  password=config.PASSWORD,
  key_filename=config.KEY_FILENAME)

@Dsclient.event
async def on_message(message):
    # メッセージがボット自身のものであれば無視
    if message.author == Dsclient.user:
        return
    # 特定のチャンネルID
    target_channel_id = config.ANNOUNCE

    # 投稿されたメッセージが特定のチャンネルからのものかチェック
    if message.channel.id == target_channel_id:
        await message.publish() 

@tree.command(name='statistics',description='統計を表示します')
async def restart(interaction: Interaction):
    await interaction.response.defer()
    ConnectSSH()
    sftp_connecution = Sshclient.open_sftp()
    path = "/root/Main/stats/"+interaction.user.display_name+".txt"

    with sftp_connecution.open(path) as fl:
        for line in fl:
            f=sftp_connecution.open("/root/Main/world/stats/"+line+".json")
            Statistics.convertjson(line+".json",f)
    await interaction.followup.send(file=discord.File(line+ ".json"))


# Discord Botを起動します
Dsclient.run(config.TOKEN)

#変更日 24/1/19