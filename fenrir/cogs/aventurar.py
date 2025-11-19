import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import random
import asyncio
from datetime import datetime, timedelta

class AventuraCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ARQUIVO_AVENTURAS = "aventuras_data.json"
        
        self.COOLDOWN_HORAS = 4
        
        self.CHANCE_VITORIA_COMBATE = (30, 50)
        self.CHANCE_MACHUCADO_VITORIA = (40, 60)
        self.CHANCE_FURTIVIDADE = 50 
        
        self.PENALIDADE_FURTIVIDADE_FALHA = (750, 1500) 
        self.RECOMPENSA_FURTIVIDADE = (1000, 2000)   
        
        self.RECOMPENSA_TESOURO = (1000, 3000)     
        self.RECOMPENSA_VITORIA_ILESO = (800, 1500) 
        self.RECOMPENSA_VITORIA_MACHUCADO = (400, 750) 
        
        self.XP_VITORIA_ILESO = 3000  
        self.XP_VITORIA_MACHUCADO = 1500
        self.XP_TESOURO = 4000  
        self.XP_FURTIVIDADE = 2000       
        
        self.situacoes = [
            {
                "nome": "Esqueletos na Masmorra",
                "descricao": "🌌 Enquanto explora uma masmorra antiga, você é cercado por três esqueletos armados!",
                "imagem": "https://cdn.discordapp.com/attachments/1288876556898275328/1428865372076904560/ChatGPT_Image_17_10_2025_18_28_20.png?ex=68f40e13&is=68f2bc93&hm=9bd4a3e97f2e7ba0afb97bd89bc900be7e03cd538bf245142bfe8145842b1b49&",
                "tipo": "combate",
            },
            {
                "nome": "Piratas no Porto", 
                "descricao": "⚓ Ao chegar no porto, um grupo de piratas famintos te cerca exigindo seu tesouro!",
                "imagem": "https://cdn.discordapp.com/attachments/1288876556898275328/1428865474091028511/Piratas_e_o_Lobo_Fantasma.png?ex=68f40e2c&is=68f2bcac&hm=f92f414c791383bdec7c754f7e39d8124b594d8034b1e96ca3917d598a56fa39&",
                "tipo": "combate",
            },
            {
                "nome": "Tesouro Perdido",
                "descricao": "💰 Você encontra um baú antigo escondido! Parece que a sorte está ao seu lado hoje!",
                "imagem": "https://cdn.discordapp.com/attachments/1288876556898275328/1428869687512662077/Image_fx_4.jpg?ex=68f41218&is=68f2c098&hm=9d82119e389a40de720a1d1603b8913c2349a5d7284f424f66efe0dc8ba358d1&",
                "tipo": "tesouro",
            }
        ]

        self.verificar_aventuras_expiradas.start()
        self.verificar_aventuras_prontas.start()

    def carregar_dados(self):
        try:
            if os.path.exists(self.ARQUIVO_AVENTURAS):
                with open(self.ARQUIVO_AVENTURAS, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for user_id, aventura_data in data.items():
                        if "inicio" in aventura_data:
                            data[user_id]["inicio"] = datetime.fromisoformat(aventura_data["inicio"])
                    return data
            return {}
        except Exception as e:
            print(f"❌ Erro ao carregar dados das aventuras: {e}")
            return {}

    def salvar_dados(self, dados):
        try:
            data_para_salvar = {}
            for user_id, aventura_data in dados.items():
                data_para_salvar[user_id] = aventura_data.copy()
                if "inicio" in data_para_salvar[user_id]:
                    data_para_salvar[user_id]["inicio"] = data_para_salvar[user_id]["inicio"].isoformat()
            
            with open(self.ARQUIVO_AVENTURAS, "w", encoding="utf-8") as f:
                json.dump(data_para_salvar, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar dados das aventuras: {e}")

    def obter_aventura_usuario(self, usuario_id):
        dados = self.carregar_dados()
        return dados.get(str(usuario_id))

    def remover_aventura_usuario(self, usuario_id):
        dados = self.carregar_dados()
        usuario_id_str = str(usuario_id)
        if usuario_id_str in dados:
            del dados[usuario_id_str]
            self.salvar_dados(dados)
            return True
        return False

    def adicionar_aventura_usuario(self, usuario_id, aventura_data):
        dados = self.carregar_dados()
        dados[str(usuario_id)] = aventura_data
        self.salvar_dados(dados)

    def obter_tempo_restante(self, inicio_aventura):
        fim_aventura = inicio_aventura + timedelta(hours=self.COOLDOWN_HORAS)
        tempo_restante = (fim_aventura - datetime.utcnow()).total_seconds()
        return max(0, tempo_restante)

    def obter_tempo_decorrido(self, inicio_aventura):
        tempo_decorrido = (datetime.utcnow() - inicio_aventura).total_seconds()
        return tempo_decorrido

    def aventura_expirada(self, inicio_aventura):
        tempo_restante = self.obter_tempo_restante(inicio_aventura)
        return tempo_restante <= 0

    def aventura_pronta(self, inicio_aventura):
        tempo_restante = self.obter_tempo_restante(inicio_aventura)
        return tempo_restante <= 0

    async def adicionar_xp(self, user_id: int, xp: int, motivo: str):
        try:
            level_cog = self.bot.get_cog("XPCog")
            if level_cog:
                sucesso = await level_cog.adicionar_xp(user_id, xp, motivo)
                
                if sucesso and xp > 0:
                    canal_log = self.bot.get_channel(1427479688544129064)
                    if canal_log:
                        user = self.bot.get_user(user_id)
                        if isinstance(user, discord.User):
                            for guild in self.bot.guilds:
                                member = guild.get_member(user.id)
                                if member:
                                    user = member
                                    break
                        if user:
                            embed_log = discord.Embed(
                                title="⭐ XP Ganho na Aventura",
                                description=f"**{user.mention}** ganhou **{xp} XP**!\n**Motivo:** {motivo}",
                                color=discord.Color.gold(),
                                timestamp=discord.utils.utcnow()
                            )
                            await canal_log.send(embed=embed_log)
                
                return sucesso
            else:
                print(f"❌ Sistema de level não encontrado para adicionar XP")
                return False
        except Exception as e:
            print(f"❌ Erro ao adicionar XP: {e}")
            return False

    def calcular_chance_vitoria(self, situacao):
        chance_min, chance_max = self.CHANCE_VITORIA_COMBATE
        
        if situacao.get("dificuldade") == "alta":
            chance_min = max(20, chance_min - 10)
            chance_max = max(40, chance_max - 10)
        
        return random.randint(chance_min, chance_max)

    def calcular_chance_machucado(self, situacao):
        """Calcula a chance de se machucar baseada na dificuldade"""
        chance_min, chance_max = self.CHANCE_MACHUCADO_VITORIA
        
        if situacao.get("dificuldade") == "alta":
            chance_min = min(90, chance_min + 20)
            chance_max = min(90, chance_max + 20)
        
        return random.randint(chance_min, chance_max)

    def formatar_tempo(self, segundos):
        """Formata segundos em horas, minutos e segundos de forma legível"""
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segundos_rest = int(segundos % 60)
        
        if horas > 0:
            if minutos == 0 and segundos_rest == 0:
                return f"{horas}h"
            elif segundos_rest == 0:
                return f"{horas}h {minutos}m"
            else:
                return f"{horas}h {minutos}m {segundos_rest}s"
        elif minutos > 0:
            if segundos_rest == 0:
                return f"{minutos}m"
            else:
                return f"{minutos}m {segundos_rest}s"
        else:
            return f"{segundos_rest}s"

    def formatar_data_local(self, data_utc):
        """Formata data UTC para o fuso horário local do Brasil"""
        try:
            fuso_brasil = timedelta(hours=-3)
            data_local = data_utc + fuso_brasil
            
            dias_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
            meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
            
            dia_semana = dias_semana[data_local.weekday()]
            dia = data_local.day
            mes = meses[data_local.month - 1]
            ano = data_local.year
            hora = data_local.hour
            minuto = data_local.minute
            
            return f"{dia_semana}, {dia} de {mes} de {ano} às {hora:02d}:{minuto:02d}"
        
        except Exception as e:
            print(f"❌ Erro ao formatar data: {e}")
            return data_utc.strftime("%d/%m/%Y às %H:%M")

    class AventuraView(discord.ui.View):
        def __init__(self, aventura_cog, usuario_id, interaction_original, situacao):
            super().__init__(timeout=None) 
            self.aventura_cog = aventura_cog
            self.usuario_id = usuario_id
            self.interaction_original = interaction_original
            self.situacao = situacao

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            """Verifica se a interação ainda é válida"""
            if interaction.user.id != self.usuario_id:
                await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
                return False
            
            # Verificar se a aventura ainda existe e está pronta
            aventura_data = self.aventura_cog.obter_aventura_usuario(self.usuario_id)
            if not aventura_data:
                await interaction.response.send_message("❌ Esta aventura já foi concluída ou expirou!", ephemeral=True)
                return False
                
            inicio_aventura = aventura_data["inicio"]
            if not self.aventura_cog.aventura_pronta(inicio_aventura):
                await interaction.response.send_message("❌ Esta aventura ainda não está pronta!", ephemeral=True)
                return False
                
            return True

        @discord.ui.button(label="⚔️ Enfrentá-los", style=discord.ButtonStyle.green, emoji="⚔️", custom_id="aventura_enfrentar")
        async def enfrentar(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.aventura_cog.remover_aventura_usuario(self.usuario_id)

            coins_cog = self.aventura_cog.bot.get_cog("FenrirCoins")
            
            chance_vitoria = self.aventura_cog.calcular_chance_vitoria(self.situacao)
            vitoria = random.randint(1, 100) <= chance_vitoria
            
            xp_ganho = 0
            ganho = 0
            machucado = False

            if vitoria:
                chance_machucado = self.aventura_cog.calcular_chance_machucado(self.situacao)
                machucado = random.randint(1, 100) <= chance_machucado
                
                if machucado:
                    ganho = random.randint(*self.aventura_cog.RECOMPENSA_VITORIA_MACHUCADO)
                    xp_ganho = self.aventura_cog.XP_VITORIA_MACHUCADO
                    if coins_cog:
                        await coins_cog.adicionar_coins(self.usuario_id, ganho, "Vitória machucado na aventura")
                    
                    embed = discord.Embed(
                        title="⚔️ Vitória com Ferimentos!",
                        description=(
                            f"**Você venceu o combate, mas saiu machucado!**\n\n"
                            f"🏥 **Estado:** Ferido (-50% recompensa)\n"
                            f"💰 **Recompensa:** {ganho} coins\n"
                            f"⭐ **XP Ganho:** +{xp_ganho} XP\n\n"
                            f"*Esta foi uma batalha difícil!*"
                        ),
                        color=discord.Color.orange()
                    )
                else:
                    ganho = random.randint(*self.aventura_cog.RECOMPENSA_VITORIA_ILESO)
                    xp_ganho = self.aventura_cog.XP_VITORIA_ILESO
                    if coins_cog:
                        await coins_cog.adicionar_coins(self.usuario_id, ganho, "Vitória ileso na aventura")
                    
                    embed = discord.Embed(
                        title="🎉 Vitória Completa!",
                        description=(
                            f"**Você venceu o combate sem um arranhão!**\n\n"
                            f"💪 **Estado:** Ileso\n"
                            f"💰 **Recompensa:** {ganho} coins\n"
                            f"⭐ **XP Ganho:** +{xp_ganho} XP\n\n"
                            f"*Uma vitória impressionante!*"
                        ),
                        color=discord.Color.green()
                    )
                
                await self.aventura_cog.adicionar_xp(self.usuario_id, xp_ganho, f"Vitória em {self.situacao['nome']}")
                
            else:
                embed = discord.Embed(
                    title="💀 Derrota no Combate",
                    description=(
                        f"**Você foi derrotado na batalha!**\n\n"
                        f"😔 **Estado:** Derrotado\n"
                        f"💸 **Recompensa:** 0 coins\n"
                        f"⭐ **XP Ganho:** 0 XP\n\n"
                        f"*Mais sorte na próxima aventura!*"
                    ),
                    color=discord.Color.red()
                )
                ganho = 0

            await interaction.response.send_message(embed=embed)

            canal_log = self.aventura_cog.bot.get_channel(1428872885216481432)
            if canal_log:
                if vitoria:
                    resultado = "Vitória Ileso" if not machucado else "Vitória com Ferimentos"
                else:
                    resultado = "Derrota"
                    
                embed_log = discord.Embed(
                    title=f"🌌 Aventura - {self.situacao['nome']}",
                    description=(
                        f"**Usuário:** {interaction.user.mention} (`{self.usuario_id}`)\n"
                        f"**Ação:** Enfrentar\n"
                        f"**Resultado:** {resultado}\n"
                        f"**Dificuldade:** {self.situacao.get('dificuldade', 'média').title()}\n"
                        f"**Coins:** +{ganho}\n"
                        f"**XP:** +{xp_ganho}"
                    ),
                    color=discord.Color.green() if vitoria and not machucado else discord.Color.orange() if vitoria else discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                await canal_log.send(embed=embed_log)

            self.stop()

        @discord.ui.button(label="👣 Avançar Furtivamente", style=discord.ButtonStyle.blurple, emoji="👣", custom_id="aventura_furtividade")
        async def furtividade(self, interaction: discord.Interaction, button: discord.ui.Button):

            self.aventura_cog.remover_aventura_usuario(self.usuario_id)

            coins_cog = self.aventura_cog.bot.get_cog("FenrirCoins")

            sucesso = random.randint(1, 100) <= self.aventura_cog.CHANCE_FURTIVIDADE
            
            xp_ganho = 0
            ganho = 0
            
            if sucesso:
                ganho = random.randint(*self.aventura_cog.RECOMPENSA_FURTIVIDADE)
                xp_ganho = self.aventura_cog.XP_FURTIVIDADE
                if coins_cog:
                    await coins_cog.adicionar_coins(self.usuario_id, ganho, "Furtividade bem sucedida na aventura")
                
                embed = discord.Embed(
                    title="👣 Furtividade Bem Sucedida!",
                    description=(
                        f"**Você passou despercebido pelos perigos!**\n\n"
                        f"🎭 **Estratégia:** Furtividade\n"
                        f"💰 **Recompensa:** {ganho} coins\n"
                        f"⭐ **XP Ganho:** +{xp_ganho} XP\n\n"
                        f"*Às vezes, a sabedoria está em evitar o conflito...*"
                    ),
                    color=discord.Color.blue()
                )
                
                await self.aventura_cog.adicionar_xp(self.usuario_id, xp_ganho, f"Furtividade em {self.situacao['nome']}")
                
            else:
                embed = discord.Embed(
                    title="🚨 Furtividade Fracassada",
                    description=(
                        f"**Você foi descoberto e teve que fugir!**\n\n"
                        f"🏃 **Situação:** Fuga\n"
                        f"💸 **Ganho:** 0 coins\n"
                        f"⭐ **XP Ganho:** 0 XP\n\n"
                        f"*A sorte não estava do seu lado desta vez...*"
                    ),
                    color=discord.Color.orange()
                )

            await interaction.response.send_message(embed=embed)

            canal_log = self.aventura_cog.bot.get_channel(1428872885216481432)
            if canal_log:
                embed_log = discord.Embed(
                    title=f"🌌 Aventura - {self.situacao['nome']}",
                    description=(
                        f"**Usuário:** {interaction.user.mention} (`{self.usuario_id}`)\n"
                        f"**Ação:** Furtividade\n"
                        f"**Resultado:** {'Sucesso' if sucesso else 'Fracasso'}\n"
                        f"**Dificuldade:** {self.situacao.get('dificuldade', 'média').title()}\n"
                        f"**Coins:** {'+' if sucesso else ''}{ganho}\n"
                        f"**XP:** +{xp_ganho if sucesso else 0}"
                    ),
                    color=discord.Color.blue() if sucesso else discord.Color.orange(),
                    timestamp=discord.utils.utcnow()
                )
                await canal_log.send(embed=embed_log)

            self.stop()

    class TesouroView(discord.ui.View):
        def __init__(self, aventura_cog, usuario_id, interaction_original, situacao):
            super().__init__(timeout=None) 
            self.aventura_cog = aventura_cog
            self.usuario_id = usuario_id
            self.interaction_original = interaction_original
            self.situacao = situacao

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            """Verifica se a interação ainda é válida"""
            if interaction.user.id != self.usuario_id:
                await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
                return False
            
            aventura_data = self.aventura_cog.obter_aventura_usuario(self.usuario_id)
            if not aventura_data:
                await interaction.response.send_message("❌ Esta aventura já foi concluída ou expirou!", ephemeral=True)
                return False
                
            inicio_aventura = aventura_data["inicio"]
            if not self.aventura_cog.aventura_pronta(inicio_aventura):
                await interaction.response.send_message("❌ Esta aventura ainda não está pronta!", ephemeral=True)
                return False
                
            return True

        @discord.ui.button(label="💰 Coletar Tesouro", style=discord.ButtonStyle.green, emoji="💰", custom_id="tesouro_coletar")
        async def coletar_tesouro(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.aventura_cog.remover_aventura_usuario(self.usuario_id)

            coins_cog = self.aventura_cog.bot.get_cog("FenrirCoins")
            ganho = random.randint(*self.aventura_cog.RECOMPENSA_TESOURO)
            xp_ganho = self.aventura_cog.XP_TESOURO
            
            if coins_cog:
                await coins_cog.adicionar_coins(self.usuario_id, ganho, "Tesouro encontrado na aventura")

            await self.aventura_cog.adicionar_xp(self.usuario_id, xp_ganho, f"Tesouro em {self.situacao['nome']}")

            embed = discord.Embed(
                title="💰 Tesouro Encontrado!",
                description=(
                    f"**Você encontrou um tesouro magnífico!**\n\n"
                    f"💎 **Fortuna:** {ganho} coins\n"
                    f"⭐ **XP Ganho:** +{xp_ganho} XP\n"
                    f"🎉 **Situação:** Sorte pura!\n\n"
                    f"*Às vezes a sorte sorri para os aventureiros...*"
                ),
                color=discord.Color.gold()
            )

            await interaction.response.send_message(embed=embed)

            canal_log = self.aventura_cog.bot.get_channel(1428872885216481432)
            if canal_log:
                embed_log = discord.Embed(
                    title=f"🌌 Aventura - {self.situacao['nome']}",
                    description=(
                        f"**Usuário:** {interaction.user.mention} (`{self.usuario_id}`)\n"
                        f"**Tipo:** Tesouro\n"
                        f"**Resultado:** Sucesso\n"
                        f"**Coins:** +{ganho}\n"
                        f"**XP:** +{xp_ganho}"
                    ),
                    color=discord.Color.gold(),
                    timestamp=discord.utils.utcnow()
                )
                await canal_log.send(embed=embed_log)

            self.stop()

    @tasks.loop(minutes=1)
    async def verificar_aventuras_prontas(self):
        try:
            dados = self.carregar_dados()
            aventuras_notificadas = []
            
            for user_id_str, aventura_data in dados.items():
                if "inicio" in aventura_data and "notificado" not in aventura_data:
                    inicio_aventura = aventura_data["inicio"]
                    
                    if self.aventura_pronta(inicio_aventura):
                        user_id = int(user_id_str)
                        user = self.bot.get_user(user_id)
                        
                        if user:
                            situacao = aventura_data["situacao"]
                            canal_id = aventura_data.get("canal_id")
                            canal_original = self.bot.get_channel(canal_id) if canal_id else None
                            
                            try:
                                embed_dm = discord.Embed(
                                    title="🎯 Sua Aventura Está Pronta!",
                                    description=(
                                        f"**Sua aventura '{situacao['nome']}' está concluída!**\n\n"
                                        f"⏰ **Status:** Pronta para resgate\n"
                                        f"💎 **Recompensa:** Aguardando sua escolha\n\n"
                                        f"**Use o comando `/aventura` para ver suas opções e resgatar sua recompensa!**"
                                    ),
                                    color=discord.Color.gold()
                                )
                                
                                if situacao.get("imagem"):
                                    embed_dm.set_image(url=situacao["imagem"])
                                
                                await user.send(embed=embed_dm)
                                print(f"✅ Notificação DM enviada para {user.display_name}")
                                
                            except discord.Forbidden:
                                if canal_original:
                                    try:
                                        embed_canal = discord.Embed(
                                            title="🎯 Sua Aventura Está Pronta!",
                                            description=(
                                                f"**{user.mention}, sua aventura '{situacao['nome']}' está concluída!**\n\n"
                                                f"⏰ **Status:** Pronta para resgate\n"
                                                f"💎 **Recompensa:** Aguardando sua escolha\n\n"
                                                f"**Use o comando `/aventura` para ver suas opções e resgatar sua recompensa!**"
                                            ),
                                            color=discord.Color.gold()
                                        )
                                        
                                        if situacao.get("imagem"):
                                            embed_canal.set_image(url=situacao["imagem"])
                                        
                                        await canal_original.send(embed=embed_canal)
                                        print(f"✅ Notificação no canal enviada para {user.display_name}")
                                        
                                    except Exception as e:
                                        print(f"❌ Erro ao enviar notificação no canal para {user_id}: {e}")
                                else:
                                    print(f"❌ Não foi possível notificar {user.display_name} (sem DM e sem canal)")
                            
                            aventura_data["notificado"] = True
                            aventuras_notificadas.append(user_id_str)
            
            if aventuras_notificadas:
                self.salvar_dados(dados)
                print(f"🔔 Notificadas {len(aventuras_notificadas)} aventuras prontas")
                
        except Exception as e:
            print(f"❌ Erro na verificação de aventuras prontas: {e}")

    @tasks.loop(minutes=30)
    async def verificar_aventuras_expiradas(self):
        try:
            dados = self.carregar_dados()
            aventuras_remover = []
            agora = datetime.utcnow()
            
            for user_id, aventura_data in dados.items():
                if "inicio" in aventura_data:
                    inicio_aventura = aventura_data["inicio"]
                    tempo_decorrido = agora - inicio_aventura
                    
                    if (self.aventura_pronta(inicio_aventura) and 
                        tempo_decorrido.total_seconds() > 24 * 3600):
                        aventuras_remover.append(user_id)
            
            for user_id in aventuras_remover:
                del dados[user_id]
                print(f"🗑️ Removida aventura expirada do usuário {user_id}")
            
            if aventuras_remover:
                self.salvar_dados(dados)
                print(f"🔄 Removidas {len(aventuras_remover)} aventuras expiradas")
                
        except Exception as e:
            print(f"❌ Erro na verificação de aventuras expiradas: {e}")

    @verificar_aventuras_prontas.before_loop
    async def antes_de_verificar_prontas(self):
        await self.bot.wait_until_ready()

    @verificar_aventuras_expiradas.before_loop
    async def antes_de_verificar_expiradas(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.AventuraView(self, 0, None, self.situacoes[0]))
        self.bot.add_view(self.TesouroView(self, 0, None, self.situacoes[0]))

    @app_commands.command(name="aventura", description="🌌 Inicie uma aventura ou resgate uma pendente")
    async def aventura(self, interaction: discord.Interaction):
        
        if interaction.channel.id != 1426205118293868748:
            await interaction.response.send_message(f"❌ Ei, {interaction.user.mention}, use esse **comando** apenas em {self.bot.get_channel(1426205118293868748).mention} !", ephemeral=True)
            return
        
        try:
            usuario_id = str(interaction.user.id)
            
            aventura_existente = self.obter_aventura_usuario(interaction.user.id)
            
            if aventura_existente:
                inicio_aventura = aventura_existente["inicio"]
                situacao = aventura_existente["situacao"]
                
                if self.aventura_pronta(inicio_aventura):
                    if situacao["tipo"] == "tesouro":
                        view = self.TesouroView(self, interaction.user.id, interaction, situacao)
                        descricao = "**Um tesouro brilhante aguarda por você!**"
                    else:
                        view = self.AventuraView(self, interaction.user.id, interaction, situacao)
                        descricao = "**O momento da decisão chegou! Escolha sua estratégia:**"

                    embed = discord.Embed(
                        title=f"🎯 {situacao['nome']} - AVENTURA PRONTA!",
                        description=descricao,
                        color=discord.Color.gold()
                    )
                    
                    if situacao.get("imagem"):
                        embed.set_image(url=situacao["imagem"])
                    
                    embed.add_field(
                        name="⏰ Status",
                        value="**Sua aventura está pronta para ser concluída!**",
                        inline=False
                    )
                    
                    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                    return
                
                else:
                    tempo_decorrido = self.obter_tempo_decorrido(inicio_aventura)
                    tempo_restante = self.obter_tempo_restante(inicio_aventura)
                    tempo_decorrido_str = self.formatar_tempo(tempo_decorrido)
                    tempo_restante_str = self.formatar_tempo(tempo_restante)
                    
                    embed = discord.Embed(
                        title="🌌 Aventura em Andamento",
                        description=(
                            f"**Você já está em uma aventura!**\n\n"
                            f"⏰ **Tempo decorrido:** {tempo_decorrido_str}\n"
                            f"⏳ **Termina em:** {tempo_restante_str}\n\n"
                            f"💡 **Você receberá uma notificação quando estiver pronta!**"
                        ),
                        color=discord.Color.blue()
                    )
                    embed.set_image(url="https://cdn.discordapp.com/attachments/1288876556898275328/1429521906637340772/Gemini_Generated_Image_bkc70fbkc70fbkc7.png?ex=68f67185&is=68f52005&hm=8cb588ac19ddc26190dfb6820f5232810950f99105a5eaa8658f6548cecafe8a&")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

            situacao = random.choice(self.situacoes)
            inicio = datetime.utcnow()

            nova_aventura = {
                "inicio": inicio,
                "canal_id": interaction.channel.id,
                "situacao": situacao
            }
            
            self.adicionar_aventura_usuario(interaction.user.id, nova_aventura)

            duracao_total_segundos = self.COOLDOWN_HORAS * 3600
            duracao_str = self.formatar_tempo(duracao_total_segundos)
            data_inicio_formatada = self.formatar_data_local(inicio)

            embed = discord.Embed(
                title="🌌 Aventura Iniciada!",
                description=(
                    f"**{interaction.user.mention} partiu em uma grande aventura!**\n\n"
                    f"⏰ **Duração:** {duracao_str}\n"
                    f"🕐 **Iniciada:** {data_inicio_formatada}\n\n"
                    f"💡 **Você receberá uma notificação quando estiver pronta!**\n"
                    f"📱 **Use `/aventura` para resgatar sua recompensa após esse tempo.**"
                ),
                color=discord.Color.purple()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1288876556898275328/1428881856102924332/Voce_esta_navegando.png?ex=68f617ad&is=68f4c62d&hm=471e8152f8ba4fe678eedf38521c97f7ece756105e5990e8679645c1a2911f74&")
            
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"❌ Erro no comando aventura: {e}")
            await interaction.response.send_message(
                "❌ **Erro ao processar aventura. Tente novamente.**",
                ephemeral=True
            )

    @app_commands.command(name="aventura_status", description="🌌 Verifique o status da sua aventura atual")
    async def aventura_status(self, interaction: discord.Interaction):
        
        if interaction.channel.id != 1426205118293868748:
            await interaction.response.send_message(f"❌ Ei, {interaction.user.mention}, use esse **comando** apenas em {self.bot.get_channel(1426205118293868748).mention} !", ephemeral=True)
            return
        
        try:
            aventura_data = self.obter_aventura_usuario(interaction.user.id)
            
            if not aventura_data:
                embed = discord.Embed(
                    title="🌌 Sem Aventuras",
                    description="**Você não tem nenhuma aventura em andamento.**\nUse `/aventura` para iniciar uma!",
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            inicio_aventura = aventura_data["inicio"]
            situacao = aventura_data.get("situacao", self.situacoes[0])
            
            if self.aventura_pronta(inicio_aventura):
                embed = discord.Embed(
                    title="🎯 Aventura Pronta!",
                    description=(
                        f"**Sua aventura está concluída!**\n\n"
                        f"🎭 **Situação:** {situacao['nome']}\n"
                        f"✅ **Status:** Pronta para escolha de ação\n"
                        f"🕐 **Iniciada:** {self.formatar_data_local(inicio_aventura)}\n\n"
                        f"**Use `/aventura` para resgatar sua recompensa!**"
                    ),
                    color=discord.Color.gold()
                )
            else:
                tempo_decorrido = self.obter_tempo_decorrido(inicio_aventura)
                tempo_restante = self.obter_tempo_restante(inicio_aventura)
                tempo_decorrido_str = self.formatar_tempo(tempo_decorrido)
                tempo_restante_str = self.formatar_tempo(tempo_restante)
                
                embed = discord.Embed(
                    title="🌌 Aventura em Andamento",
                    description=(
                        f"**Sua aventura está em progresso!**\n\n"
                        f"⏰ **Tempo decorrido:** {tempo_decorrido_str}\n"
                        f"⏳ **Termina em:** {tempo_restante_str}\n"
                        f"🕐 **Iniciada:** {self.formatar_data_local(inicio_aventura)}\n\n"
                        f"💡 **Você receberá uma notificação quando estiver pronta!**"
                    ),
                    color=discord.Color.green()
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"❌ Erro no comando aventura_status: {e}")
            await interaction.response.send_message(
                "❌ **Erro ao verificar status da aventura.**",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(AventuraCog(bot))