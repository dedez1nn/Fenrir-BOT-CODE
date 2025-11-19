from discord.ext import tasks
import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import time

class PremiumCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ARQUIVO_DADOS = "user_data.json"
        
        self.planos_info = {
            "aventureiro": {
                "nome": "Aventureiro",
                "preco": 5000,
                "cor": 0x00ff00,
                "emoji": "🟢",
                "beneficios": [
                    "**2x XP** em todas as atividades",
                    "**2x Coins** em mensagens, voz e vitórias",
                    "Limite de **10 membros** na guild",
                    "Multiplicador de guild: **1.5x** (5 membros) / **2.0x** (10 membros)",
                    "**2 administradores** na guild"
                ]
            },
            "lendario": {
                "nome": "Lendário", 
                "preco": 15000,
                "cor": 0xff9900,
                "emoji": "🟠",
                "beneficios": [
                    "**4x XP** em todas as atividades",
                    "**4x Coins** em mensagens, voz e vitórias", 
                    "Limite de **20 membros** na guild",
                    "Multiplicador de guild: **1.5x** (5) / **2.0x** (10) / **3.0x** (20)",
                    "**3 administradores** na guild",
                    "**+20% XP** para toda a guild"
                ]
            },
            "mitico": {
                "nome": "Mítico",
                "preco": 30000, 
                "cor": 0xff00ff,
                "emoji": "🟣",
                "beneficios": [
                    "**6x XP** em todas as atividades",
                    "**6x Coins** em mensagens, voz e vitórias",
                    "Limite de **50 membros** na guild",
                    "Multiplicador de guild: **1.5x** (5) / **2.0x** (10) / **3.0x** (20) / **5.0x** (50)",
                    "**5 administradores** na guild", 
                    "**+50% XP** para toda a guild",
                    "**Farm AFK** ativado",
                    "Acesso a recursos exclusivos"
                ]
            }
        }
        
        self.premium_expiration_loop.start()

    @tasks.loop(hours=24)
    async def premium_expiration_loop(self):
        try:
            dados = self.carregar_dados()
            agora = time.time()
            planos_expirados = []
            
            for user_id, user_data in dados.items():
                if "premium_expiracao" in user_data and user_data["premium_expiracao"] <= agora:
                    plano_expirado = user_data.get("premium")
                    planos_expirados.append((user_id, plano_expirado))
                    
                    user_data["premium"] = None
                    del user_data["premium_expiracao"]
                    
                    print(f"⏰ Plano {plano_expirado} expirado para usuário {user_id}")
            
            if planos_expirados:
                self.salvar_dados(dados)
                
                await self.processar_planos_expirados(planos_expirados)
                
                print(f"🔄 {len(planos_expirados)} planos premium expirados foram removidos")
                
        except Exception as e:
            print(f"❌ Erro no premium_expiration_loop: {e}")

    @premium_expiration_loop.before_loop
    async def before_premium_expiration_loop(self):
        await self.bot.wait_until_ready()

    async def processar_planos_expirados(self, planos_expirados):
        for user_id, plano_expirado in planos_expirados:
            try:
                user = self.bot.get_user(int(user_id))
                if user:
                    await self.enviar_notificacao_expiracao(user, plano_expirado)
                    
                    await self.enviar_log_expiracao(user, plano_expirado)
                    
            except Exception as e:
                print(f"❌ Erro ao processar expiração para {user_id}: {e}")

    async def enviar_notificacao_expiracao(self, user: discord.User, plano_expirado: str):
        try:
            plano_info = self.planos_info.get(plano_expirado, {})
            nome_plano = plano_info.get('nome', plano_expirado.title())
            
            embed = discord.Embed(
                title="⏰ Plano Premium Expirado",
                description=f"Seu plano **{nome_plano}** expirou!",
                color=0xff6b6b,
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(
                name="📊 Status Atual",
                value="Você voltou para o plano **Gratuito**",
                inline=False
            )
            
            embed.add_field(
                name="🔄 Como Renovar",
                value="Abra um `ticket` para adquirir um novo plano",
                inline=False
            )
            
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text="Obrigado por ter usado nosso plano premium!")
            
            await user.send(embed=embed)
            print(f"📧 Notificação de expiração enviada para {user.name}")
            
        except discord.Forbidden:
            print(f"❌ Não foi possível enviar DM de expiração para {user.name}")
        except Exception as e:
            print(f"❌ Erro ao enviar notificação de expiração: {e}")

    async def enviar_log_expiracao(self, user: discord.User, plano_expirado: str):
        try:
            canal_log = self.bot.get_channel(1429919086934097950)
            if canal_log:
                plano_info = self.planos_info.get(plano_expirado, {})
                nome_plano = plano_info.get('nome', plano_expirado.title())
                
                embed = discord.Embed(
                    title="⏰ Plano Premium Expirado",
                    description=f"**{user.mention}** teve o plano **{nome_plano}** expirado",
                    color=0xff6b6b,
                    timestamp=discord.utils.utcnow()
                )
                
                embed.add_field(name="👤 Usuário", value=f"{user.name} ({user.id})", inline=True)
                embed.add_field(name="💎 Plano", value=nome_plano, inline=True)
                embed.add_field(name="📊 Status", value="Removido automaticamente", inline=True)
                
                embed.set_thumbnail(url=user.display_avatar.url)
                
                await canal_log.send(embed=embed)
                
        except Exception as e:
            print(f"❌ Erro ao enviar log de expiração: {e}")

    def carregar_dados(self):
        if os.path.exists(self.ARQUIVO_DADOS):
            with open(self.ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def salvar_dados(self, dados):
        with open(self.ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4)

    def obter_dados_usuario(self, user_id):
        dados = self.carregar_dados()
        user_id_str = str(user_id)
        if user_id_str not in dados:
            dados[user_id_str] = {
                "xp": 0, "nivel": 1, "titulo": "Aprendiz", 
                "dobro": False, "premium": None, "coins": 0,
                "daily_streak": 0, "last_daily": None, "total_ganho": 0
            }
        return dados[user_id_str]

    async def enviar_embed_premium(self, user: discord.User, plano: str, acao: str):
        plano_info = self.planos_info.get(plano)
        if not plano_info:
            return False

        try:
            if acao == "ativado":
                embed = discord.Embed(
                    title=f"🎉 {plano_info['emoji']} PLANO {plano_info['nome'].upper()} ATIVADO!",
                    description=f"Parabéns {user.mention}! Seu plano **{plano_info['nome']}** foi ativado com sucesso!",
                    color=plano_info['cor'],
                    timestamp=discord.utils.utcnow()
                )
                
                embed.add_field(
                    name="🚀 **BENEFÍCIOS ATIVADOS:**",
                    value="\n".join([f"✅ {beneficio}" for beneficio in plano_info['beneficios']]),
                    inline=False
                )
                
                embed.add_field(
                    name="💎 **MULTIPLICADORES:**",
                    value=f"**XP:** {self.obter_multiplicador_xp(plano)}x\n**Coins:** {self.obter_multiplicador_coins(plano)}x",
                    inline=True
                )
                
                embed.add_field(
                    name="🏰 **BENEFÍCIOS DA GUILD:**",
                    value=f"**Membros máx.:** {self.obter_limite_membros(plano)}\n**Admins:** {self.obter_limite_admins(plano)}",
                    inline=True
                )
                
            elif acao == "atualizado":
                embed = discord.Embed(
                    title=f"🔄 {plano_info['emoji']} PLANO ATUALIZADO!",
                    description=f"Seu plano foi atualizado para **{plano_info['nome']}**!",
                    color=plano_info['cor'],
                    timestamp=discord.utils.utcnow()
                )
                
                embed.add_field(
                    name="🎁 **NOVOS BENEFÍCIOS:**",
                    value="\n".join([f"⭐ {beneficio}" for beneficio in plano_info['beneficios']]),
                    inline=False
                )
                
            elif acao == "removido":
                embed = discord.Embed(
                    title="😔 PLANO PREMIUM REMOVIDO",
                    description="Seu plano premium foi removido.",
                    color=0xff0000,
                    timestamp=discord.utils.utcnow()
                )
                
                embed.add_field(
                    name="ℹ️ **INFORMAÇÃO:**",
                    value="Você voltou para o plano gratuito. Para renovar seu plano, use `/premium_comprar`",
                    inline=False
                )

            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text="💖 Obrigado por apoiar nosso servidor!")
            
            await user.send(embed=embed)
            return True
            
        except discord.Forbidden:
            print(f"❌ Não foi possível enviar DM para {user.name}")
            return False
        except Exception as e:
            print(f"❌ Erro ao enviar embed premium: {e}")
            return False

    def obter_multiplicador_xp(self, plano: str) -> int:
        multiplicadores = {
            "aventureiro": 2,
            "lendario": 4, 
            "mitico": 6
        }
        return multiplicadores.get(plano, 1)

    def obter_multiplicador_coins(self, plano: str) -> int:
        multiplicadores = {
            "aventureiro": 2,
            "lendario": 4,
            "mitico": 6
        }
        return multiplicadores.get(plano, 1)

    def obter_limite_membros(self, plano: str) -> int:
        limites = {
            "gratuito": 5,
            "aventureiro": 10,
            "lendario": 20,
            "mitico": 50
        }
        return limites.get(plano, 5)

    def obter_limite_admins(self, plano: str) -> int:
        limites = {
            "gratuito": 1,
            "aventureiro": 2, 
            "lendario": 3,
            "mitico": 5
        }
        return limites.get(plano, 1)

    @app_commands.command(name="premium", description="Mostra informações sobre os planos premium")
    async def premium_info(self, interaction: discord.Interaction):
        
        if interaction.channel.id != 1426205118293868748:
            ephemero = True
        else:
            ephemero = False
                
        emoji_presente = discord.utils.get(interaction.guild.emojis, name="presente_fenrir")
        emoji_coins = discord.utils.get(interaction.guild.emojis, name="fenrir_coins")        
        
        try:
            await interaction.response.defer(ephemeral=ephemero)
            
            embed = discord.Embed(
                title=f"{emoji_presente} PLANOS PREMIUM",
                description="Aprimore sua experiência no servidor com nossos planos exclusivos!",
                color=0x9b59b6,
                timestamp=discord.utils.utcnow()
            )
            
            canal_premium = self.bot.get_channel(1429555260917284947)
            
            if canal_premium:
                embed.add_field(
                    name=f"{emoji_coins} **Como Comprar:**",
                    value=f"Vá para {canal_premium.mention} para ver as `informações`\n dos nossos planos"
                    ,
                    inline=False
                )
            
            embed.set_image(url="https://cdn.discordapp.com/attachments/1288876556898275328/1431255183521873956/Lobo_Estiloso_com_Presente_Brilhante.png?ex=68fcbfc3&is=68fb6e43&hm=d5c6ccf72ff39d063c0508688174ac2db56f187f462bf9708637318392e2f286&")
            embed.set_footer(text="💖 Apoie nosso servidor!")
            
            await interaction.followup.send(embed=embed, ephemeral=ephemero)
            
        except Exception as e:
            print(f"❌ Erro em premium_info: {e}")
            await interaction.followup.send("❌ Erro ao carregar informações!", ephemeral=True)

    @app_commands.command(name="premium_remover", description="Remove plano premium de um usuário (ADM)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(usuario="Usuário que terá o plano removido")
    async def premium_remover(self, interaction: discord.Interaction, usuario: discord.Member):
        try:
            await interaction.response.defer(ephemeral=True)
            
            user_id = str(usuario.id)
            dados_usuarios = self.carregar_dados()
            
            if user_id not in dados_usuarios:
                await interaction.followup.send("❌ Usuário não encontrado no sistema!", ephemeral=True)
                return
            
            plano_anterior = dados_usuarios[user_id].get("premium")
            if not plano_anterior:
                await interaction.followup.send("❌ Este usuário não possui plano premium!", ephemeral=True)
                return
            
            dados_usuarios[user_id]["premium"] = None
            self.salvar_dados(dados_usuarios)
            
            await self.enviar_embed_premium(usuario, plano_anterior, "removido")
            canal_log = self.bot.get_channel(1427479688544129064)
            if canal_log:
                embed_log = discord.Embed(
                    title="🔧 Plano Premium Removido",
                    description=f"**{usuario.mention}** teve o plano **{plano_anterior}** removido",
                    color=0xff0000,
                    timestamp=discord.utils.utcnow()
                )
                embed_log.add_field(name="👤 Removido por", value=interaction.user.mention, inline=True)
                embed_log.set_thumbnail(url=usuario.display_avatar.url)
                embed_log.set_footer(text=f"ID: {usuario.id}")
                await canal_log.send(embed=embed_log)
            
            await interaction.followup.send(
                f"✅ Plano **{plano_anterior}** removido de {usuario.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            print(f"❌ Erro em premium_remover: {e}")
            await interaction.followup.send("❌ Erro ao remover plano!", ephemeral=True)
            
    @app_commands.command(name="premium_adicionar", description="Adiciona plano premium a um usuário (ADM)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        usuario="Usuário que receberá o plano",
        plano="Plano premium a ser adicionado",
        duracao_dias="Duração em dias (0 = permanente)"
    )
    @app_commands.choices(plano=[
        app_commands.Choice(name="🟢 Aventureiro", value="aventureiro"),
        app_commands.Choice(name="🟠 Lendário", value="lendario"), 
        app_commands.Choice(name="🟣 Mítico", value="mitico"),
        app_commands.Choice(name="❌ Remover Premium", value="none")
    ])
    async def premium_adicionar(self, interaction: discord.Interaction, usuario: discord.Member, plano: str, duracao_dias: int = 0):
        try:
            await interaction.response.defer(ephemeral=True)
            
            user_id = str(usuario.id)
            dados_usuarios = self.carregar_dados()
            
            if user_id not in dados_usuarios:
                await interaction.followup.send("❌ Usuário não encontrado no sistema!", ephemeral=True)
                return
            
            plano_anterior = dados_usuarios[user_id].get("premium")
            
            if plano == "none":
                if not plano_anterior:
                    await interaction.followup.send("❌ Este usuário não possui plano premium!", ephemeral=True)
                    return
                
                dados_usuarios[user_id]["premium"] = None
                if "premium_expiracao" in dados_usuarios[user_id]:
                    del dados_usuarios[user_id]["premium_expiracao"]
                
                self.salvar_dados(dados_usuarios)
                
                await self.enviar_embed_premium(usuario, plano_anterior, "removido")
                
                await interaction.followup.send(
                    f"✅ Plano **{plano_anterior}** removido de {usuario.mention}",
                    ephemeral=True
                )
                
            else:
                plano_info = self.planos_info.get(plano)
                if not plano_info:
                    await interaction.followup.send("❌ Plano inválido!", ephemeral=True)
                    return
                
                if duracao_dias > 0:
                    expiracao = time.time() + (duracao_dias * 86400)
                    dados_usuarios[user_id]["premium_expiracao"] = expiracao
                elif "premium_expiracao" in dados_usuarios[user_id]:
                    del dados_usuarios[user_id]["premium_expiracao"]
                
                dados_usuarios[user_id]["premium"] = plano
                self.salvar_dados(dados_usuarios)
                
                acao = "ativado" if not plano_anterior else "atualizado"
                embed_enviado = await self.enviar_embed_premium(usuario, plano, acao)
                
                mensagem = f"✅ Plano **{plano_info['nome']}** {acao} para {usuario.mention}"
                if duracao_dias > 0:
                    mensagem += f"\n⏰ **Duração:** {duracao_dias} dias"
                else:
                    mensagem += "\n⏰ **Duração:** Permanente"
                
                if plano_anterior:
                    mensagem += f"\n📊 **Plano anterior:** {plano_anterior}"
                
                await interaction.followup.send(mensagem, ephemeral=True)
            
            canal_log = self.bot.get_channel(1429919086934097950)
            if canal_log:
                embed_log = discord.Embed(
                    title="🔧 Plano Premium Modificado (ADM)",
                    color=0x3498db,
                    timestamp=discord.utils.utcnow()
                )
                
                if plano == "none":
                    embed_log.description = f"**{usuario.mention}** teve o plano **{plano_anterior}** removido"
                    embed_log.add_field(name="🗑️ Ação", value="Remoção", inline=True)
                else:
                    embed_log.description = f"**{usuario.mention}** recebeu o plano **{plano}**"
                    embed_log.add_field(name="🔄 Ação", value=acao.title(), inline=True)
                    if duracao_dias > 0:
                        embed_log.add_field(name="⏰ Duração", value=f"{duracao_dias} dias", inline=True)
                    else:
                        embed_log.add_field(name="⏰ Duração", value="Permanente", inline=True)
                
                embed_log.add_field(name="👤 Executado por", value=interaction.user.mention, inline=True)
                if plano_anterior and plano != "none":
                    embed_log.add_field(name="📊 Plano Anterior", value=plano_anterior, inline=True)
                
                embed_log.set_thumbnail(url=usuario.display_avatar.url)
                embed_log.set_footer(text=f"ID: {usuario.id}")
                await canal_log.send(embed=embed_log)
                
        except Exception as e:
            print(f"❌ Erro em premium_adicionar: {e}")
            await interaction.followup.send("❌ Erro ao modificar plano!", ephemeral=True)
            

async def setup(bot: commands.Bot):
    await bot.add_cog(PremiumCog(bot))