import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import os
import time
import asyncio
import random
from typing import Optional

def carregar_user_data():
    try:
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar user_data: {e}")
    return {}

def salvar_user_data(dados):
    """Salva os dados no user_data.json"""
    try:
        with open("user_data.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar user_data: {e}")
        return False

def obter_xp_usuario(user_id: int) -> int:
    dados = carregar_user_data()
    user_id_str = str(user_id)
    
    if user_id_str in dados:
        return dados[user_id_str].get("xp", 0)
    return 0

def remover_xp_usuario(user_id: int, quantidade: int, motivo: str = "") -> bool:
    try:
        dados = carregar_user_data()
        user_id_str = str(user_id)
        
        if user_id_str not in dados:
            print(f"❌ Usuário {user_id} não encontrado no user_data.json")
            return False
        
        xp_atual = dados[user_id_str].get("xp", 0)
        if xp_atual < quantidade:
            print(f"❌ Usuário {user_id} não tem XP suficiente. Tem: {xp_atual}, Precisa: {quantidade}")
            return False
        
        dados[user_id_str]["xp"] = xp_atual - quantidade
        
        if "total_ganho" in dados[user_id_str]:
            dados[user_id_str]["total_ganho"] = max(0, dados[user_id_str]["total_ganho"] - quantidade)
        
        print(f"✅ XP removido: {user_id} perdeu {quantidade} XP. Motivo: {motivo}")
        return salvar_user_data(dados)
        
    except Exception as e:
        print(f"❌ Erro ao remover XP: {e}")
        return False

def obter_coins_usuario(user_id: int) -> int:
    dados = carregar_user_data()
    user_id_str = str(user_id)
    
    if user_id_str in dados:
        return dados[user_id_str].get("coins", 0)
    return 0

def remover_coins_usuario(user_id: int, quantidade: int, motivo: str = "") -> bool:
    try:
        dados = carregar_user_data()
        user_id_str = str(user_id)
        
        if user_id_str not in dados:
            print(f"❌ Usuário {user_id} não encontrado no user_data.json")
            return False
        
        coins_atual = dados[user_id_str].get("coins", 0)
        if coins_atual < quantidade:
            print(f"❌ Usuário {user_id} não tem coins suficiente. Tem: {coins_atual}, Precisa: {quantidade}")
            return False
        
        dados[user_id_str]["coins"] = coins_atual - quantidade
        
        if "total_ganho" in dados[user_id_str]:
            dados[user_id_str]["total_ganho"] = max(0, dados[user_id_str]["total_ganho"] - quantidade)
        
        return salvar_user_data(dados)
        
    except Exception as e:
        print(f"❌ Erro ao remover coins: {e}")
        return False

def adicionar_xp_usuario(user_id: int, quantidade: int, motivo: str = "") -> bool:
    try:
        dados = carregar_user_data()
        user_id_str = str(user_id)
        
        if user_id_str not in dados:
            print(f"❌ Usuário {user_id} não encontrado no user_data.json")
            return False
        
        xp_atual = dados[user_id_str].get("xp", 0)
        dados[user_id_str]["xp"] = xp_atual + quantidade
        
        if "total_ganho" in dados[user_id_str]:
            dados[user_id_str]["total_ganho"] = dados[user_id_str]["total_ganho"] + quantidade
        
        print(f"✅ XP adicionado: {user_id} ganhou {quantidade} XP. Motivo: {motivo}")
        return salvar_user_data(dados)
        
    except Exception as e:
        print(f"❌ Erro ao adicionar XP: {e}")
        return False

def adicionar_coins_usuario(user_id: int, quantidade: int, motivo: str = "") -> bool:
    try:
        dados = carregar_user_data()
        user_id_str = str(user_id)
        
        if user_id_str not in dados:
            print(f"❌ Usuário {user_id} não encontrado no user_data.json")
            return False
        
        coins_atual = dados[user_id_str].get("coins", 0)
        dados[user_id_str]["coins"] = coins_atual + quantidade
        
        if "total_ganho" in dados[user_id_str]:
            dados[user_id_str]["total_ganho"] = dados[user_id_str]["total_ganho"] + quantidade
        
        print(f"✅ Coins adicionadas: {user_id} ganhou {quantidade} coins. Motivo: {motivo}")
        return salvar_user_data(dados)
        
    except Exception as e:
        print(f"❌ Erro ao adicionar coins: {e}")
        return False


class DoacaoXPModal(discord.ui.Modal, title='Doar XP para a Raid'):
    def __init__(self, guild_system, raid_id, guild_tipo):
        super().__init__()
        self.guild_system = guild_system
        self.raid_id = raid_id
        self.guild_tipo = guild_tipo

    valor_xp = discord.ui.TextInput(
        label='Quantidade de XP para doar',
        placeholder='Digite um valor entre 1 e 100',
        min_length=1,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            valor = int(self.valor_xp.value)
            if valor < 1 or valor > 100:
                await interaction.response.send_message('❌ O valor de XP deve estar entre 1 e 100!', ephemeral=True)
                return

            sucesso = await self.guild_system.registrar_doacao(interaction, self.raid_id, self.guild_tipo, 'xp', valor)
            if sucesso:
                await interaction.response.send_message(f'✅ Você doou {valor} XP para a raid!', ephemeral=True)
            else:
                await interaction.response.send_message('❌ Erro ao processar doação de XP!', ephemeral=True)

        except ValueError:
            await interaction.response.send_message('❌ Por favor, digite um número válido!', ephemeral=True)

class DoacaoCoinsModal(discord.ui.Modal, title='Doar Coins para a Raid'):
    def __init__(self, guild_system, raid_id, guild_tipo):
        super().__init__()
        self.guild_system = guild_system
        self.raid_id = raid_id
        self.guild_tipo = guild_tipo

    valor_coins = discord.ui.TextInput(
        label='Quantidade de Coins para doar',
        placeholder='Digite um valor entre 1 e 1000',
        min_length=1,
        max_length=4
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            valor = int(self.valor_coins.value)
            if valor < 1 or valor > 1000:
                await interaction.response.send_message('❌ O valor de Coins deve estar entre 1 e 1000!', ephemeral=True)
                return

            sucesso = await self.guild_system.registrar_doacao(interaction, self.raid_id, self.guild_tipo, 'coins', valor)
            if sucesso:
                await interaction.response.send_message(f'✅ Você doou {valor} Coins para a raid!', ephemeral=True)
            else:
                await interaction.response.send_message('❌ Erro ao processar doação de Coins!', ephemeral=True)

        except ValueError:
            await interaction.response.send_message('❌ Por favor, digite um número válido!', ephemeral=True)

class DoacaoRaidView(discord.ui.View):
    def __init__(self, guild_system, raid_id, guild_tipo):
        super().__init__(timeout=18000) 
        self.guild_system = guild_system
        self.raid_id = raid_id
        self.guild_tipo = guild_tipo  # 'atacante' ou 'defensor'

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label='Doar Experiência', style=discord.ButtonStyle.primary, emoji='🌟')
    async def doar_xp(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DoacaoXPModal(self.guild_system, self.raid_id, self.guild_tipo))

    @discord.ui.button(label='Doar Coins', style=discord.ButtonStyle.success, emoji='🪙')
    async def doar_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DoacaoCoinsModal(self.guild_system, self.raid_id, self.guild_tipo))

class ConfirmacaoAliancaPropostaView(discord.ui.View):
    def __init__(self, guild_system, guild_id, guild_alvo_id):
        super().__init__(timeout=86400)
        self.guild_system = guild_system
        self.guild_id = guild_id
        self.guild_alvo_id = guild_alvo_id

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label='Aceitar Aliança', style=discord.ButtonStyle.success, emoji='✅')
    async def aceitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            await self.processar_resposta(interaction, True)
        except Exception as e:
            print(f"❌ Erro em aceitar aliança: {e}")

    @discord.ui.button(label='Recusar Aliança', style=discord.ButtonStyle.danger, emoji='❌')
    async def recusar(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            await self.processar_resposta(interaction, False)
        except Exception as e:
            print(f"❌ Erro em recusar aliança: {e}")

    async def processar_resposta(self, interaction: discord.Interaction, aceitar: bool):
        try:
            dados = self.guild_system.carregar_dados()
            guild_data = dados.get(self.guild_alvo_id)
            guild_proponente_data = dados.get(self.guild_id)
            
            if not guild_data or not guild_proponente_data:
                await interaction.followup.send("❌ Guild não encontrada!", ephemeral=True)
                return

            if guild_data["lider"] != str(interaction.user.id):
                await interaction.followup.send("❌ Apenas o líder da guild pode aceitar alianças!", ephemeral=True)
                return

            if aceitar:
                if "aliancas" not in guild_data:
                    guild_data["aliancas"] = []
                if "aliancas" not in guild_proponente_data:
                    guild_proponente_data["aliancas"] = []

                guild_data["aliancas"].append(self.guild_id)
                guild_proponente_data["aliancas"].append(self.guild_alvo_id)
                
                guild_data["data_alianca"] = time.time()
                guild_proponente_data["data_alianca"] = time.time()

                dados[self.guild_alvo_id] = guild_data
                dados[self.guild_id] = guild_proponente_data
                self.guild_system.salvar_dados(dados)

                embed = discord.Embed(
                    title="🤝 Aliança Formada!",
                    description=f"**{guild_data['nome']}** e **{guild_proponente_data['nome']}** agora são aliadas!",
                    color=discord.Color.green()
                )
                embed.add_field(name="🏰 Guilds", value=f"{guild_data['nome']} 🤝 {guild_proponente_data['nome']}", inline=False)
                embed.add_field(name="📊 Benefícios", value="• Apoio em raids\n• Defesa conjunta\n• Bônus estratégicos", inline=False)
                
                await interaction.followup.send(embed=embed)
                
                try:
                    lider_proponente = await self.guild_system.bot.fetch_user(int(guild_proponente_data["lider"]))
                    await lider_proponente.send(embed=embed)
                except:
                    pass
                    
            else:
                embed = discord.Embed(
                    title="❌ Proposta Recusada",
                    description=f"Você recusou a aliança com **{guild_proponente_data['nome']}**",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                
                try:
                    lider_proponente = await self.guild_system.bot.fetch_user(int(guild_proponente_data["lider"]))
                    embed_recusa = discord.Embed(
                        title="❌ Proposta Recusada",
                        description=f"**{guild_data['nome']}** recusou sua proposta de aliança.",
                        color=discord.Color.red()
                    )
                    await lider_proponente.send(embed=embed_recusa)
                except:
                    pass

        except Exception as e:
            print(f"❌ Erro ao processar resposta de aliança: {e}")
            await interaction.followup.send("❌ Erro ao processar resposta!", ephemeral=True)

class AliancaView(discord.ui.View):
    def __init__(self, guild_system, raid_id, tipo):
        super().__init__(timeout=43200)
        self.guild_system = guild_system
        self.raid_id = raid_id
        self.tipo = tipo

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label='Atacar pela Frente', style=discord.ButtonStyle.primary, emoji='⚔️')
    async def atacar_frente(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_estrategia_aliado(interaction, "frente")

    @discord.ui.button(label='Atacar pelos Flancos', style=discord.ButtonStyle.danger, emoji='🎯')
    async def atacar_flancos(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_estrategia_aliado(interaction, "flancos")

    async def processar_estrategia_aliado(self, interaction: discord.Interaction, estrategia: str):
        try:
            await interaction.response.defer(ephemeral=True)
            dados = self.guild_system.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            
            if self.raid_id not in raids_ativas:
                await interaction.followup.send("❌ Esta raid não existe mais!", ephemeral=True)
                return

            raid_data = raids_ativas[self.raid_id]
            guild_id_aliado = self.guild_system.obter_guild_por_membro(interaction.user.id)
            
            if not guild_id_aliado:
                await interaction.followup.send("❌ Você precisa estar em uma guild para apoiar!", ephemeral=True)
                return

            guild_principal_id = raid_data[self.tipo]["guild_id"]
            guild_principal = dados[guild_principal_id]
            
            if guild_id_aliado not in guild_principal.get("aliancas", []):
                await interaction.followup.send("❌ Sua guild não é aliada da guild principal!", ephemeral=True)
                return

            aliados = raid_data[self.tipo].get("aliados", {})
            if guild_id_aliado in aliados:
                await interaction.followup.send("❌ Sua guild já escolheu uma estratégia!", ephemeral=True)
                return

            if len(aliados) >= 2:
                await interaction.followup.send("❌ Limite de 2 aliados já atingido!", ephemeral=True)
                return

            aliados[guild_id_aliado] = {
                "estrategia": estrategia,
                "timestamp": time.time(),
                "guild_nome": dados[guild_id_aliado]["nome"]
            }

            raid_data[self.tipo]["aliados"] = aliados
            raids_ativas[self.raid_id] = raid_data
            dados["raids_ativas"] = raids_ativas
            self.guild_system.salvar_dados(dados)

            embed = discord.Embed(
                title="✅ Apoio Confirmado!",
                description=f"**{dados[guild_id_aliado]['nome']}** vai apoiar com **{estrategia.replace('_', ' ').title()}**",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

            await self.verificar_confirmacoes_completas()

        except Exception as e:
            print(f"❌ Erro ao processar estratégia de aliado: {e}")
            await interaction.followup.send("❌ Erro ao processar estratégia!", ephemeral=True)

    async def verificar_confirmacoes_completas(self):
        try:
            dados = self.guild_system.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            raid_data = raids_ativas.get(self.raid_id)
            
            if not raid_data:
                return

            aliados_atacante = raid_data["atacante"].get("aliados", {})
            aliados_defensor = raid_data["defensor"].get("aliados", {})
            
            if (len(aliados_atacante) >= raid_data["atacante"].get("aliados_solicitados", 0) and
                len(aliados_defensor) >= raid_data["defensor"].get("aliados_solicitados", 0)):
                await self.guild_system.processar_raid_imediatamente(self.raid_id)

        except Exception as e:
            print(f"❌ Erro ao verificar confirmações: {e}")

class DefensorAliancaView(discord.ui.View):
    def __init__(self, guild_system, raid_id, tipo):
        super().__init__(timeout=43200)
        self.guild_system = guild_system
        self.raid_id = raid_id
        self.tipo = tipo

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label='Construir Muros', style=discord.ButtonStyle.primary, emoji='🏰')
    async def construir_muros(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_estrategia_aliado(interaction, "muros")

    @discord.ui.button(label='Bloquear Ataque de Flechas', style=discord.ButtonStyle.success, emoji='🛡️')
    async def bloquear_flechas(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_estrategia_aliado(interaction, "bloquear_flechas")

    async def processar_estrategia_aliado(self, interaction: discord.Interaction, estrategia: str):
        try:
            await interaction.response.defer(ephemeral=True)
            dados = self.guild_system.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            
            if self.raid_id not in raids_ativas:
                await interaction.followup.send("❌ Esta raid não existe mais!", ephemeral=True)
                return

            raid_data = raids_ativas[self.raid_id]
            guild_id_aliado = self.guild_system.obter_guild_por_membro(interaction.user.id)
            
            if not guild_id_aliado:
                await interaction.followup.send("❌ Você precisa estar em uma guild para apoiar!", ephemeral=True)
                return

            guild_principal_id = raid_data[self.tipo]["guild_id"]
            guild_principal = dados[guild_principal_id]
            
            if guild_id_aliado not in guild_principal.get("aliancas", []):
                await interaction.followup.send("❌ Sua guild não é aliada da guild principal!", ephemeral=True)
                return

            aliados = raid_data[self.tipo].get("aliados", {})
            if guild_id_aliado in aliados:
                await interaction.followup.send("❌ Sua guild já escolheu uma estratégia!", ephemeral=True)
                return

            if len(aliados) >= 2:
                await interaction.followup.send("❌ Limite de 2 aliados já atingido!", ephemeral=True)
                return

            aliados[guild_id_aliado] = {
                "estrategia": estrategia,
                "timestamp": time.time(),
                "guild_nome": dados[guild_id_aliado]["nome"]
            }

            raid_data[self.tipo]["aliados"] = aliados
            raids_ativas[self.raid_id] = raid_data
            dados["raids_ativas"] = raids_ativas
            self.guild_system.salvar_dados(dados)

            embed = discord.Embed(
                title="✅ Apoio Confirmado!",
                description=f"**{dados[guild_id_aliado]['nome']}** vai apoiar com **{estrategia.replace('_', ' ').title()}**",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

            await self.verificar_confirmacoes_completas()

        except Exception as e:
            print(f"❌ Erro ao processar estratégia de aliado: {e}")
            await interaction.followup.send("❌ Erro ao processar estratégia!", ephemeral=True)

    async def verificar_confirmacoes_completas(self):
        try:
            dados = self.guild_system.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            raid_data = raids_ativas.get(self.raid_id)
            
            if not raid_data:
                return

            aliados_atacante = raid_data["atacante"].get("aliados", {})
            aliados_defensor = raid_data["defensor"].get("aliados", {})
            
            if (len(aliados_atacante) >= raid_data["atacante"].get("aliados_solicitados", 0) and
                len(aliados_defensor) >= raid_data["defensor"].get("aliados_solicitados", 0)):
                await self.guild_system.processar_raid_imediatamente(self.raid_id)

        except Exception as e:
            print(f"❌ Erro ao verificar confirmações: {e}")

class RaidAtaqueView(discord.ui.View):
    def __init__(self, guild_system, raid_id):
        super().__init__(timeout=18000)  # 5 horas
        self.guild_system = guild_system
        self.raid_id = raid_id

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label='Atacar Furtivamente', style=discord.ButtonStyle.primary, emoji='🕵️')
    async def atacar_furtivo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_estrategia(interaction, "furtivo")

    @discord.ui.button(label='Atacar pela Frente', style=discord.ButtonStyle.danger, emoji='⚔️')
    async def atacar_frontal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_estrategia(interaction, "frontal")

    async def processar_estrategia(self, interaction: discord.Interaction, estrategia: str):
        try:
            await interaction.response.defer(ephemeral=True)
            dados = self.guild_system.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            
            if self.raid_id not in raids_ativas:
                await interaction.followup.send("❌ Esta raid não existe mais!", ephemeral=True)
                return

            raid_data = raids_ativas[self.raid_id]
            
            guild_atacante_id = self.guild_system.obter_guild_por_membro(interaction.user.id)
            if not guild_atacante_id or guild_atacante_id != raid_data["atacante"]["guild_id"]:
                await interaction.followup.send("❌ Apenas o líder da guild atacante pode escolher a estratégia!", ephemeral=True)
                return

            user_cargo = dados[guild_atacante_id]["membros"].get(str(interaction.user.id), {}).get("cargo")
            if user_cargo not in ["Líder", "Admin"]:
                await interaction.followup.send("❌ Apenas líderes e administradores podem escolher estratégias!", ephemeral=True)
                return

            if raid_data["atacante"]["estrategia"] is not None:
                await interaction.followup.send("❌ Estratégia de ataque já foi escolhida!", ephemeral=True)
                return

            raid_data["atacante"]["estrategia"] = estrategia
            raids_ativas[self.raid_id] = raid_data
            dados["raids_ativas"] = raids_ativas
            self.guild_system.salvar_dados(dados)

            await self.atualizar_embed_raid(interaction, raid_data)

            embed = discord.Embed(
                title="🎯 Estratégia de Ataque Definida!",
                description=f"**{estrategia.replace('_', ' ').title()}**",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

            if raid_data["defensor"]["estrategia"] is not None:
                await self.guild_system.processar_raid_imediatamente(self.raid_id)

        except Exception as e:
            print(f"❌ Erro ao processar estratégia de ataque: {e}")
            await interaction.followup.send("❌ Erro ao processar estratégia!", ephemeral=True)

    async def atualizar_embed_raid(self, interaction: discord.Interaction, raid_data: dict):
        try:
            thread = interaction.channel
            if not isinstance(thread, discord.Thread):
                return

            async for message in thread.history(limit=10, oldest_first=True):
                if message.author.id == self.guild_system.bot.user.id and message.embeds:
                    embed = message.embeds[0]

                    novos_campos = []
                    for field in embed.fields:
                        if field.name == "⚔️ Estratégia do Atacante":
                            novos_campos.append(("⚔️ Estratégia do Atacante", f"`{raid_data['atacante']['estrategia'].replace('_', ' ').title()}` ✅", True))
                        else:
                            novos_campos.append((field.name, field.value, field.inline))
     
                    novo_embed = discord.Embed(
                        title=embed.title,
                        description=embed.description,
                        color=embed.color,
                        timestamp=embed.timestamp
                    )
                    
                    for name, value, inline in novos_campos:
                        novo_embed.add_field(name=name, value=value, inline=inline)
                    
                    if embed.footer:
                        novo_embed.set_footer(text=embed.footer.text, icon_url=embed.footer.icon_url)
                    
                    await message.edit(embed=novo_embed)
                    break
                    
        except Exception as e:
            print(f"❌ Erro ao atualizar embed da raid: {e}")

class RaidDefesaView(discord.ui.View):
    def __init__(self, guild_system, raid_id):
        super().__init__(timeout=18000)  # 5 horas
        self.guild_system = guild_system
        self.raid_id = raid_id

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label='Contra-Atacar', style=discord.ButtonStyle.primary, emoji='🛡️')
    async def contra_atacar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_estrategia(interaction, "contra_ataque")

    @discord.ui.button(label='Defender', style=discord.ButtonStyle.success, emoji='🏰')
    async def defender(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_estrategia(interaction, "defesa")

    async def processar_estrategia(self, interaction: discord.Interaction, estrategia: str):
        try:
            await interaction.response.defer(ephemeral=True)
            dados = self.guild_system.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            
            if self.raid_id not in raids_ativas:
                await interaction.followup.send("❌ Esta raid não existe mais!", ephemeral=True)
                return

            raid_data = raids_ativas[self.raid_id]

            guild_defensora_id = self.guild_system.obter_guild_por_membro(interaction.user.id)
            if not guild_defensora_id or guild_defensora_id != raid_data["defensor"]["guild_id"]:
                await interaction.followup.send("❌ Apenas o líder da guild defensora pode escolher a estratégia!", ephemeral=True)
                return

            user_cargo = dados[guild_defensora_id]["membros"].get(str(interaction.user.id), {}).get("cargo")
            if user_cargo not in ["Líder", "Admin"]:
                await interaction.followup.send("❌ Apenas líderes e administradores podem escolher estratégias!", ephemeral=True)
                return

            if raid_data["defensor"]["estrategia"] is not None:
                await interaction.followup.send("❌ Estratégia de defesa já foi escolhida!", ephemeral=True)
                return

            raid_data["defensor"]["estrategia"] = estrategia
            raids_ativas[self.raid_id] = raid_data
            dados["raids_ativas"] = raids_ativas
            self.guild_system.salvar_dados(dados)

            await self.atualizar_embed_raid(interaction, raid_data)

            embed = discord.Embed(
                title="🎯 Estratégia de Defesa Definida!",
                description=f"**{estrategia.replace('_', ' ').title()}**",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

            if raid_data["atacante"]["estrategia"] is not None:
                await self.guild_system.processar_raid_imediatamente(self.raid_id)

        except Exception as e:
            print(f"❌ Erro ao processar estratégia de defesa: {e}")
            await interaction.followup.send("❌ Erro ao processar estratégia!", ephemeral=True)

    async def atualizar_embed_raid(self, interaction: discord.Interaction, raid_data: dict):
        try:
            thread = interaction.channel
            if not isinstance(thread, discord.Thread):
                return

            async for message in thread.history(limit=10, oldest_first=True):
                if message.author.id == self.guild_system.bot.user.id and message.embeds:
                    embed = message.embeds[0]

                    novos_campos = []
                    for field in embed.fields:
                        if field.name == "🛡️ Estratégia do Defensor":
                            novos_campos.append(("🛡️ Estratégia do Defensor", f"`{raid_data['defensor']['estrategia'].replace('_', ' ').title()}` ✅", True))
                        else:
                            novos_campos.append((field.name, field.value, field.inline))

                    novo_embed = discord.Embed(
                        title=embed.title,
                        description=embed.description,
                        color=embed.color,
                        timestamp=embed.timestamp
                    )
                    
                    for name, value, inline in novos_campos:
                        novo_embed.add_field(name=name, value=value, inline=inline)
                    
                    if embed.footer:
                        novo_embed.set_footer(text=embed.footer.text, icon_url=embed.footer.icon_url)
                    
                    await message.edit(embed=novo_embed)
                    break
                    
        except Exception as e:
            print(f"❌ Erro ao atualizar embed da raid: {e}")

class ConfirmacaoAliancaView(discord.ui.View):
    def __init__(self, guild_system, raid_id):
        super().__init__(timeout=300)
        self.guild_system = guild_system
        self.raid_id = raid_id

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label='Sim - Envolver Aliança', style=discord.ButtonStyle.success, emoji='🤝')
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_confirmacao(interaction, True)

    @discord.ui.button(label='Não - Raid Normal', style=discord.ButtonStyle.danger, emoji='⚔️')
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_confirmacao(interaction, False)

    async def processar_confirmacao(self, interaction: discord.Interaction, usar_alianca: bool):
        try:
            await interaction.response.defer(ephemeral=True)
            dados = self.guild_system.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            
            if self.raid_id not in raids_ativas:
                await interaction.followup.send("❌ Esta raid não existe mais!", ephemeral=True)
                return

            raid_data = raids_ativas[self.raid_id]
            raid_data["atacante"]["usar_alianca"] = usar_alianca
            raid_data["atacante"]["aliados_solicitados"] = 2 if usar_alianca else 0
            raid_data["atacante"]["aliados"] = {}

            raids_ativas[self.raid_id] = raid_data
            dados["raids_ativas"] = raids_ativas
            self.guild_system.salvar_dados(dados)

            if usar_alianca:
                await self.notificar_aliados_atacante(raid_data)
                embed = discord.Embed(
                    title="🤝 Aliança Convocada!",
                    description="Seus aliados foram notificados para apoiar na raid!",
                    color=discord.Color.blue()
                )
            else:
                embed = discord.Embed(
                    title="⚔️ Raid Normal",
                    description="Raid continuará sem apoio de aliados.",
                    color=discord.Color.orange()
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

            await self.guild_system.criar_topicos_raid(self.raid_id, raid_data)

        except Exception as e:
            print(f"❌ Erro ao processar confirmação de aliança: {e}")
            await interaction.followup.send("❌ Erro ao processar confirmação!", ephemeral=True)

    async def notificar_aliados_atacante(self, raid_data: dict):
        try:
            canal_aliancas_id = 1430607187193102456
            canal = self.guild_system.bot.get_channel(canal_aliancas_id)
            
            if not canal:
                print("❌ Canal de alianças não encontrado!")
                return

            dados = self.guild_system.carregar_dados()
            guild_atacante = dados[raid_data["atacante"]["guild_id"]]
            aliados = guild_atacante.get("aliancas", [])
            
            if not aliados:
                embed = discord.Embed(
                    title="🤝 Sem Aliados Disponíveis",
                    description=f"**{guild_atacante['nome']}** tentou convocar aliados, mas não tem alianças ativas!",
                    color=discord.Color.orange()
                )
                await canal.send(embed=embed)
                return

            embed = discord.Embed(
                title="🚨 CONVOCAÇÃO DE ALIANÇA - ATAQUE",
                description=f"**{guild_atacante['nome']}** está iniciando uma raid e precisa de seu apoio!",
                color=discord.Color.red()
            )
            embed.add_field(name="🎯 Alvo", value=raid_data["defensor"]["guild_nome"], inline=True)
            embed.add_field(name="⏰ Tempo para responder", value="12 horas", inline=True)
            embed.add_field(name="👥 Aliados necessários", value="2 guilds", inline=True)
            embed.add_field(
                name="⚔️ Estratégias disponíveis",
                value="**Atacar pela Frente**: +15% chance de vitória\n**Atacar pelos Flancos**: +10% chance de vitória",
                inline=False
            )
            embed.set_footer(text="Apenas guilds aliadas podem responder")

            view = AliancaView(self.guild_system, self.raid_id, "atacante")
            await canal.send(embed=embed, view=view)

        except Exception as e:
            print(f"❌ Erro ao notificar aliados atacante: {e}")

class ConfirmacaoDefensorAliancaView(discord.ui.View):
    def __init__(self, guild_system, raid_id):
        super().__init__(timeout=300)
        self.guild_system = guild_system
        self.raid_id = raid_id

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label='Sim - Pedir Apoio', style=discord.ButtonStyle.success, emoji='🛡️')
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_confirmacao(interaction, True)

    @discord.ui.button(label='Não - Defender Sozinho', style=discord.ButtonStyle.danger, emoji='⚔️')
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_confirmacao(interaction, False)

    async def processar_confirmacao(self, interaction: discord.Interaction, usar_alianca: bool):
        try:
            await interaction.response.defer(ephemeral=True)
            dados = self.guild_system.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            
            if self.raid_id not in raids_ativas:
                await interaction.followup.send("❌ Esta raid não existe mais!", ephemeral=True)
                return

            raid_data = raids_ativas[self.raid_id]
            raid_data["defensor"]["usar_alianca"] = usar_alianca
            raid_data["defensor"]["aliados_solicitados"] = 2 if usar_alianca else 0
            raid_data["defensor"]["aliados"] = {}

            raids_ativas[self.raid_id] = raid_data
            dados["raids_ativas"] = raids_ativas
            self.guild_system.salvar_dados(dados)

            if usar_alianca:
                await self.notificar_aliados_defensor(raid_data)
                embed = discord.Embed(
                    title="🛡️ Apoio Solicitado!",
                    description="Seus aliados foram notificados para ajudar na defesa!",
                    color=discord.Color.blue()
                )
            else:
                embed = discord.Embed(
                    title="⚔️ Defesa Solo",
                    description="Você defenderá sem apoio de aliados.",
                    color=discord.Color.orange()
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"❌ Erro ao processar confirmação de aliança defensor: {e}")
            await interaction.followup.send("❌ Erro ao processar confirmação!", ephemeral=True)

    async def notificar_aliados_defensor(self, raid_data: dict):
        try:
            canal_aliancas_id = 1430607187193102456
            canal = self.guild_system.bot.get_channel(canal_aliancas_id)
            
            if not canal:
                print("❌ Canal de alianças não encontrado!")
                return

            dados = self.guild_system.carregar_dados()
            guild_defensor = dados[raid_data["defensor"]["guild_id"]]
            aliados = guild_defensor.get("aliancas", [])
            
            if not aliados:
                embed = discord.Embed(
                    title="🛡️ Sem Aliados Disponíveis",
                    description=f"**{guild_defensor['nome']}** tentou convocar aliados, mas não tem alianças ativas!",
                    color=discord.Color.orange()
                )
                await canal.send(embed=embed)
                return

            embed = discord.Embed(
                title="🚨 CONVOCAÇÃO DE ALIANÇA - DEFESA",
                description=f"**{guild_defensor['nome']}** está sob ataque e precisa de sua ajuda!",
                color=discord.Color.red()
            )
            embed.add_field(name="⚔️ Atacante", value=raid_data["atacante"]["guild_nome"], inline=True)
            embed.add_field(name="⏰ Tempo para responder", value="12 horas", inline=True)
            embed.add_field(name="👥 Aliados necessários", value="2 guilds", inline=True)
            embed.add_field(
                name="🏰 Estratégias disponíveis",
                value="**Construir Muros**: +15% chance de defesa\n**Bloquear Flechas**: +10% chance de defesa",
                inline=False
            )
            embed.set_footer(text="Apenas guilds aliadas podem responder")

            view = DefensorAliancaView(self.guild_system, self.raid_id, "defensor")
            await canal.send(embed=embed, view=view)

        except Exception as e:
            print(f"❌ Erro ao notificar aliados defensor: {e}")

class GuildAllianceRaidSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ARQUIVO_GUILDS = "guilds_data.json"
        self.CANAL_RAIDS_ID = 1430607187193102456
        self.verificar_raids.start()

    def carregar_dados(self):
        try:
            if os.path.exists(self.ARQUIVO_GUILDS):
                with open(self.ARQUIVO_GUILDS, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
        return {"raids_ativas": {}}

    def salvar_dados(self, dados):
        try:
            with open(self.ARQUIVO_GUILDS, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4)
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")
            return False

    def obter_guild_por_membro(self, user_id: int) -> Optional[str]:
        dados = self.carregar_dados()
        user_id_str = str(user_id)
        
        for guild_id, guild_data in dados.items():
            if guild_id == "raids_ativas":
                continue
            if user_id_str in guild_data.get("membros", {}):
                return guild_id
        return None


    async def registrar_doacao(self, interaction: discord.Interaction, raid_id: str, guild_tipo: str, tipo_doacao: str, valor: int) -> bool:
        try:
            await interaction.response.defer(ephemeral=True)
            
            dados = self.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            
            if raid_id not in raids_ativas:
                await interaction.followup.send("❌ Esta raid não existe mais!", ephemeral=True)
                return False

            raid_data = raids_ativas[raid_id]
            guild_id = raid_data[guild_tipo]["guild_id"]
            
            user_guild_id = self.obter_guild_por_membro(interaction.user.id)
            if user_guild_id != guild_id:
                await interaction.followup.send("❌ Você não é membro da guild envolvida nesta raid!", ephemeral=True)
                return False

            if tipo_doacao == 'xp':
                xp_usuario = obter_xp_usuario(interaction.user.id)
                if xp_usuario < valor:
                    await interaction.followup.send("❌ Você não tem XP suficiente para doar!", ephemeral=True)
                    return False
                
                if not remover_xp_usuario(interaction.user.id, valor, f"Doação para raid {raid_id}"):
                    await interaction.followup.send("❌ Erro ao processar doação de XP!", ephemeral=True)
                    return False
                    
            else:
                coins_usuario = obter_coins_usuario(interaction.user.id)
                if coins_usuario < valor:
                    await interaction.followup.send("❌ Você não tem Coins suficiente para doar!", ephemeral=True)
                    return False
                
                if not remover_coins_usuario(interaction.user.id, valor, f"Doação para raid {raid_id}"):
                    await interaction.followup.send("❌ Erro ao processar doação de Coins!", ephemeral=True)
                    return False

            if "doacoes" not in raid_data[guild_tipo]:
                raid_data[guild_tipo]["doacoes"] = {}
            
            user_id_str = str(interaction.user.id)
            if user_id_str not in raid_data[guild_tipo]["doacoes"]:
                raid_data[guild_tipo]["doacoes"][user_id_str] = {"xp": 0, "coins": 0, "nome": interaction.user.display_name}
            
            raid_data[guild_tipo]["doacoes"][user_id_str][tipo_doacao] += valor

            if f"total_doacoes_{tipo_doacao}" not in raid_data[guild_tipo]:
                raid_data[guild_tipo][f"total_doacoes_{tipo_doacao}"] = 0
            raid_data[guild_tipo][f"total_doacoes_{tipo_doacao}"] += valor

            raids_ativas[raid_id] = raid_data
            dados["raids_ativas"] = raids_ativas
            self.salvar_dados(dados)

            try:
                await self.atualizar_embed_principal_raid(raid_id)
            except Exception as e:
                pass

            await interaction.followup.send(f'✅ Você doou {valor} {tipo_doacao.upper()} para a raid!', ephemeral=True)
            return True

        except Exception as e:
            print(f"❌ Erro ao registrar doação: {e}")
            try:
                await interaction.followup.send("❌ Erro ao processar doação!", ephemeral=True)
            except:
                pass
            return False


    @app_commands.command(name="guild_aliar-se", description="Faz uma proposta de aliança para outra guild")
    @app_commands.describe(guild_alvo="Nome da guild para proposta de aliança")
    async def guild_ally(self, interaction: discord.Interaction, guild_alvo: str):
        try:
            await interaction.response.defer(ephemeral=True)
            
            guild_id = self.obter_guild_por_membro(interaction.user.id)
            if not guild_id:
                await interaction.followup.send("❌ Você precisa estar em uma guild para fazer alianças!")
                return
            
            dados = self.carregar_dados()
            guild_data = dados.get(guild_id)
            
            if not guild_data:
                await interaction.followup.send("❌ Sua guild não foi encontrada!")
                return
            
            if guild_data["lider"] != str(interaction.user.id):
                await interaction.followup.send("❌ Apenas o líder da guild pode fazer alianças!")
                return
            
            guild_alvo_encontrada = None
            for gid, gdata in dados.items():
                if gid != "raids_ativas" and gdata.get("nome", "").lower() == guild_alvo.lower():
                    guild_alvo_encontrada = (gid, gdata)
                    break
            
            if not guild_alvo_encontrada:
                await interaction.followup.send("❌ Guild alvo não encontrada!")
                return
            
            guild_alvo_id, guild_alvo_data = guild_alvo_encontrada
            
            if guild_id == guild_alvo_id:
                await interaction.followup.send("❌ Você não pode fazer aliança com sua própria guild!")
                return
            
            if guild_alvo_id in guild_data.get("aliancas", []):
                await interaction.followup.send("❌ Suas guilds já são aliadas!")
                return
            
            if len(guild_data.get("aliancas", [])) >= 5:
                await interaction.followup.send("❌ Sua guild já atingiu o limite de 5 alianças!")
                return
            
            if len(guild_alvo_data.get("aliancas", [])) >= 5:
                await interaction.followup.send("❌ A guild alvo já atingiu o limite de alianças!")
                return
            
            try:
                lider_alvo = await self.bot.fetch_user(int(guild_alvo_data["lider"]))
                
                embed = discord.Embed(
                    title="🤝 Proposta de Aliança",
                    description=f"**{guild_data['nome']}** deseja formar uma aliança com sua guild!",
                    color=discord.Color.gold()
                )
                embed.add_field(name="🏰 Sua Guild", value=guild_alvo_data["nome"], inline=True)
                embed.add_field(name="🤝 Aliado", value=guild_data["nome"], inline=True)
                embed.add_field(name="📊 Benefícios", value="• Apoio em raids\n• Defesa conjunta\n• Bônus estratégicos", inline=False)
                embed.set_footer(text="A aliança permite apoio mútuo em batalhas")
                
                view = ConfirmacaoAliancaPropostaView(self, guild_id, guild_alvo_id)
                await lider_alvo.send(embed=embed, view=view)
                
                await interaction.followup.send(f"✅ Proposta de aliança enviada para **{guild_alvo_data['nome']}**!")
                
            except Exception as e:
                await interaction.followup.send("❌ Não foi possível enviar a proposta para o líder da guild alvo!")
            
        except Exception as e:
            print(f"❌ Erro em guild_ally: {e}")
            await interaction.followup.send("❌ Erro ao enviar proposta de aliança!")

    @app_commands.command(name="guild_aliancas", description="Mostra as alianças da sua guild")
    async def guild_allies(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            
            guild_id = self.obter_guild_por_membro(interaction.user.id)
            if not guild_id:
                await interaction.followup.send("❌ Você não está em uma guild!")
                return
            
            dados = self.carregar_dados()
            guild_data = dados.get(guild_id)
            
            if not guild_data:
                await interaction.followup.send("❌ Guild não encontrada!")
                return
            
            aliancas = guild_data.get("aliancas", [])
            
            embed = discord.Embed(
                title=f"🤝 Alianças de {guild_data['nome']}",
                color=discord.Color.blue()
            )
            
            if not aliancas:
                embed.description = "Sua guild não tem alianças ativas."
            else:
                for aliado_id in aliancas:
                    if aliado_id in dados:
                        aliado_data = dados[aliado_id]
                        dias_alianca = int((time.time() - aliado_data.get("data_alianca", time.time())) / 86400)
                        embed.add_field(
                            name=f"🏰 {aliado_data['nome']}",
                            value=f"Líder: <@{aliado_data['lider']}>\nMembros: {len(aliado_data['membros'])}\nAliança há: {dias_alianca} dias",
                            inline=True
                        )
            
            embed.set_footer(text=f"Total: {len(aliancas)}/5 alianças")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"❌ Erro em guild_allies: {e}")
            await interaction.followup.send("❌ Erro ao carregar alianças!")

    @app_commands.command(name="guild_remv_alianca", description="Rompe uma aliança")
    @app_commands.describe(guild_alvo="Nome da guild para romper aliança")
    async def guild_break_ally(self, interaction: discord.Interaction, guild_alvo: str):
        try:
            await interaction.response.defer(ephemeral=True)
            
            guild_id = self.obter_guild_por_membro(interaction.user.id)
            if not guild_id:
                await interaction.followup.send("❌ Você precisa estar em uma guild!")
                return
            
            dados = self.carregar_dados()
            guild_data = dados.get(guild_id)
            
            if not guild_data:
                await interaction.followup.send("❌ Sua guild não foi encontrada!")
                return
            
            if guild_data["lider"] != str(interaction.user.id):
                await interaction.followup.send("❌ Apenas o líder da guild pode romper alianças!")
                return
            
            guild_alvo_encontrada = None
            for gid, gdata in dados.items():
                if gid != "raids_ativas" and gdata.get("nome", "").lower() == guild_alvo.lower():
                    guild_alvo_encontrada = (gid, gdata)
                    break
            
            if not guild_alvo_encontrada:
                await interaction.followup.send("❌ Guild alvo não encontrada!")
                return
            
            guild_alvo_id, guild_alvo_data = guild_alvo_encontrada
            
            if guild_alvo_id not in guild_data.get("aliancas", []):
                await interaction.followup.send("❌ Suas guilds não são aliadas!")
                return
            
            guild_data["aliancas"].remove(guild_alvo_id)
            guild_alvo_data["aliancas"].remove(guild_id)
            
            dados[guild_id] = guild_data
            dados[guild_alvo_id] = guild_alvo_data
            
            if self.salvar_dados(dados):
                try:
                    lider_alvo = await self.bot.fetch_user(int(guild_alvo_data["lider"]))
                    embed = discord.Embed(
                        title="💔 Aliança Rompida",
                        description=f"**{guild_data['nome']}** rompeu a aliança com sua guild!",
                        color=discord.Color.red()
                    )
                    await lider_alvo.send(embed=embed)
                except:
                    pass
                
                await interaction.followup.send(f"✅ Aliança com **{guild_alvo_data['nome']}** rompida!")
            else:
                await interaction.followup.send("❌ Erro ao romper aliança!")
            
        except Exception as e:
            print(f"❌ Erro em guild_break_ally: {e}")
            await interaction.followup.send("❌ Erro ao romper aliança!")


    async def iniciar_raid(self, interaction: discord.Interaction, guild_alvo: str):
        try:
            await interaction.response.defer(ephemeral=True)
            
            guild_atacante_id = self.obter_guild_por_membro(interaction.user.id)
            if not guild_atacante_id:
                await interaction.followup.send("❌ Você precisa estar em uma guild para iniciar uma raid!")
                return
            
            dados = self.carregar_dados()
            guild_atacante = dados.get(guild_atacante_id)
            
            if not guild_atacante:
                await interaction.followup.send("❌ Sua guild não foi encontrada!")
                return
            
            cargo_usuario = guild_atacante["membros"].get(str(interaction.user.id), {}).get("cargo")
            if cargo_usuario not in ["Líder", "Admin"]:
                await interaction.followup.send("❌ Apenas líderes e administradores podem iniciar raids!")
                return
            
            guild_alvo_encontrada = None
            for guild_id, guild_data in dados.items():
                if guild_id != "raids_ativas" and guild_data.get("nome", "").lower() == guild_alvo.lower():
                    guild_alvo_encontrada = (guild_id, guild_data)
                    break
            
            if not guild_alvo_encontrada:
                await interaction.followup.send("❌ Guild alvo não encontrada!")
                return
            
            guild_alvo_id, guild_alvo_data = guild_alvo_encontrada
            
            if guild_atacante_id == guild_alvo_id:
                await interaction.followup.send("❌ Você não pode raidar sua própria guild!")
                return
            
            ultima_raid = guild_alvo_data.get("ultima_raid", 0)
            if time.time() - ultima_raid < 86400:
                tempo_restante = 86400 - (time.time() - ultima_raid)
                horas = int(tempo_restante // 3600)
                minutos = int((tempo_restante % 3600) // 60)
                await interaction.followup.send(f"❌ Esta guild foi raidada recentemente! Tente novamente em {horas}h {minutos}m", ephemeral=True)
                return
            
            if len(guild_atacante["membros"]) < 5:
                await interaction.followup.send("❌ Sua guild precisa ter pelo menos 5 membros para raidar!")
                return
            
            if guild_atacante["banco"] < 10000:
                await interaction.followup.send("❌ Seu banco da guild precisa ter pelo menos 10.000 coins para raidar!")
                return
            
            raid_id = f"raid_{int(time.time())}"
            raids_ativas = dados.get("raids_ativas", {})
            
            raids_ativas[raid_id] = {
                "atacante": {
                    "guild_id": guild_atacante_id,
                    "guild_nome": guild_atacante["nome"],
                    "lider_id": guild_atacante["lider"],
                    "estrategia": None,
                    "membros_count": len(guild_atacante["membros"]),
                    "usar_alianca": None,
                    "aliados_solicitados": 0,
                    "aliados": {},
                    "doacoes": {},
                    "total_doacoes_xp": 0,
                    "total_doacoes_coins": 0
                },
                "defensor": {
                    "guild_id": guild_alvo_id,
                    "guild_nome": guild_alvo_data["nome"],
                    "lider_id": guild_alvo_data["lider"],
                    "estrategia": None,
                    "usar_alianca": None,
                    "aliados_solicitados": 0,
                    "aliados": {},
                    "doacoes": {},
                    "total_doacoes_xp": 0,
                    "total_doacoes_coins": 0
                },
                "timestamp_criacao": time.time(),
                "timestamp_finalizacao": time.time() + 18000,
                "estado": "aguardando_confirmacao_alianca",
                "thread_id": None
            }
            
            dados["raids_ativas"] = raids_ativas
            
            if self.salvar_dados(dados):
                embed = discord.Embed(
                    title="🤝 Envolver Aliança na Raid?",
                    description=f"Deseja convocar seus aliados para a raid contra **{guild_alvo_data['nome']}**?",
                    color=discord.Color.gold()
                )
                embed.add_field(name="✅ Vantagens", value="• +10-30% chance de vitória\n• Estratégias adicionais\n• Suporte em batalha", inline=True)
                embed.add_field(name="❌ Desvantagens", value="• Recompensas divididas\n• Cooldown compartilhado", inline=True)
                embed.add_field(name="👥 Seus Aliados", value=f"{len(guild_atacante.get('aliancas', []))}/5 guilds disponíveis", inline=False)
                embed.set_footer(text="Você tem 5 minutos para decidir")
                
                view = ConfirmacaoAliancaView(self, raid_id)
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            else:
                await interaction.followup.send("❌ Erro ao iniciar raid!")
            
        except Exception as e:
            print(f"❌ Erro em iniciar_raid: {e}")
            await interaction.followup.send("❌ Erro ao iniciar raid!")

    async def criar_topicos_raid(self, raid_id: str, raid_data: dict):
        try:
            canal_raids = self.bot.get_channel(self.CANAL_RAIDS_ID)
            if not canal_raids:
                print("❌ Canal de raids não encontrado!")
                return

            embed_principal = discord.Embed(
                title="⚔️ RAID INICIADA",
                description=f"**{raid_data['atacante']['guild_nome']}** está atacando **{raid_data['defensor']['guild_nome']}**!",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            
            embed_principal.add_field(
                name="🏰 Atacante",
                value=f"**{raid_data['atacante']['guild_nome']}**\nLíder: <@{raid_data['atacante']['lider_id']}>",
                inline=True
            )
            
            embed_principal.add_field(
                name="🛡️ Defensor", 
                value=f"**{raid_data['defensor']['guild_nome']}**\nLíder: <@{raid_data['defensor']['lider_id']}>",
                inline=True
            )
            
            embed_principal.add_field(
                name="⚔️ Estratégia do Atacante",
                value="`Aguardando...` ⏳",
                inline=True
            )
            
            embed_principal.add_field(
                name="🛡️ Estratégia do Defensor",
                value="`Aguardando...` ⏳", 
                inline=True
            )
            
            embed_principal.add_field(
                name="⏰ Tempo Restante",
                value="5 horas",
                inline=True
            )
            
            embed_principal.add_field(
                name="🤝 Aliados",
                value=f"Atacante: {len(raid_data['atacante'].get('aliados', {}))}/2\nDefensor: {len(raid_data['defensor'].get('aliados', {}))}/2",
                inline=True
            )
            embed_principal.set_footer(text=f"ID: {raid_id}")
            embed_principal.set_image(url="https://cdn.discordapp.com/attachments/1288876556898275328/1430752851180916837/Gemini_Generated_Image_310q8h310q8h310q.png?ex=68faebed&is=68f99a6d&hm=3710266e358d305ccd0a285910cc276137c464b5484842c83e95a7285c8cc8f1&")

            mensagem_principal = await canal_raids.send(
                content=f"<@{raid_data['atacante']['lider_id']}> <@{raid_data['defensor']['lider_id']}>",
                embed=embed_principal
            )
            
            thread = await mensagem_principal.create_thread(
                name=f"⚔️ {raid_data['atacante']['guild_nome']} vs {raid_data['defensor']['guild_nome']}",
                auto_archive_duration=1440  
            )
            
            dados = self.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            if raid_id in raids_ativas:
                raids_ativas[raid_id]["thread_id"] = thread.id
                dados["raids_ativas"] = raids_ativas
                self.salvar_dados(dados)
            
            embed_ataque = discord.Embed(
                title="🎯 Escolha a Estratégia de ATAQUE",
                description=f"**Líder de {raid_data['atacante']['guild_nome']}**, escolha como sua guild vai atacar:",
                color=discord.Color.red()
            )
            embed_ataque.add_field(
                name="🕵️ Atacar Furtivamente", 
                value="• +25% chance contra Defesa\n• -15% chance contra Contra-Ataque\n• Surpresa tática",
                inline=False
            )
            embed_ataque.add_field(
                name="⚔️ Atacar pela Frente",
                value="• +15% chance contra Contra-Ataque\n• -25% chance contra Defesa\n• Ataque direto",
                inline=False
            )
            
            view_ataque = RaidAtaqueView(self, raid_id)
            await thread.send(embed=embed_ataque, view=view_ataque)

            embed_defesa = discord.Embed(
                title="🛡️ Escolha a Estratégia de DEFESA", 
                description=f"**Líder de {raid_data['defensor']['guild_nome']}**, escolha como sua guild vai defender:",
                color=discord.Color.blue()
            )
            embed_defesa.add_field(
                name="🛡️ Contra-Atacar",
                value="• +25% chance contra Ataque Frontal\n• -15% chance contra Ataque Furtivo\n• Emboscada ofensiva", 
                inline=False
            )
            embed_defesa.add_field(
                name="🏰 Defender",
                value="• +15% chance contra Ataque Furtivo\n• -25% chance contra Ataque Frontal\n• Defesa sólida",
                inline=False
            )
            
            view_defesa = RaidDefesaView(self, raid_id)
            await thread.send(embed=embed_defesa, view=view_defesa)

            embed_doacao_atacante = discord.Embed(
                title="💝 Doações para o Ataque",
                description=f"**Membros de {raid_data['atacante']['guild_nome']}**, ajudem sua guild doando recursos!",
                color=discord.Color.green()
            )
            embed_doacao_atacante.add_field(
                name="🌟 Doar Experiência",
                value="• Aumenta a força da guild\n• Máximo: 100 XP por usuário\n• Bônus na distribuição de recompensas",
                inline=False
            )
            embed_doacao_atacante.add_field(
                name="🪙 Doar Coins",
                value="• Aumenta a força da guild\n• Máximo: 1000 Coins por usuário\n• Bônus na distribuição de recompensas",
                inline=False
            )
            
            view_doacao_atacante = DoacaoRaidView(self, raid_id, "atacante")
            await thread.send(
                content=f"🎯 **Membros de {raid_data['atacante']['guild_nome']}** - Ajudem sua guild!",
                embed=embed_doacao_atacante,
                view=view_doacao_atacante
            )

            embed_doacao_defensor = discord.Embed(
                title="💝 Doações para a Defesa",
                description=f"**Membros de {raid_data['defensor']['guild_nome']}**, ajudem sua guild doando recursos!",
                color=discord.Color.blue()
            )
            embed_doacao_defensor.add_field(
                name="🌟 Doar Experiência",
                value="• Aumenta a força da guild\n• Máximo: 100 XP por usuário\n• Bônus na distribuição de recompensas",
                inline=False
            )
            embed_doacao_defensor.add_field(
                name="🪙 Doar Coins",
                value="• Aumenta a força da guild\n• Máximo: 1000 Coins por usuário\n• Bônus na distribuição de recompensas",
                inline=False
            )
            
            view_doacao_defensor = DoacaoRaidView(self, raid_id, "defensor")
            await thread.send(
                content=f"🛡️ **Membros de {raid_data['defensor']['guild_nome']}** - Ajudem sua guild!",
                embed=embed_doacao_defensor,
                view=view_doacao_defensor
            )

            await self.notificar_defensor_raid(raid_data, thread)

        except Exception as e:
            print(f"❌ Erro ao criar tópicos de raid: {e}")

    async def notificar_defensor_raid(self, raid_data: dict, thread: discord.Thread):
        try:
            lider_defensor = await self.bot.fetch_user(int(raid_data["defensor"]["lider_id"]))
            
            embed = discord.Embed(
                title="🚨 SUA GUILD ESTÁ SOB ATAQUE!",
                description=f"**{raid_data['defensor']['guild_nome']}** está sendo raidada por **{raid_data['atacante']['guild_nome']}**!",
                color=discord.Color.red()
            )
            embed.add_field(name="📋 O que fazer", value="Entre no tópico da raid e escolha sua estratégia de defesa!", inline=False)
            embed.add_field(name="🔗 Tópico", value=f"[Clique aqui para ir para o tópico]({thread.jump_url})", inline=False)
            embed.add_field(name="⏰ Tempo", value="Você tem 5 horas para responder", inline=False)
            embed.set_image(url="https://cdn.discordapp.com/attachments/1288876556898275328/1431260809174192168/a-dramatic-illustrated-medieval-battle-s_h8j3rOUIR8-yUGEzZ48dNw_Zgn-GNmORUqQeubpPuwakQ.jpeg?ex=68fcc500&is=68fb7380&hm=a52fa1e4ed6e7cfc0128933110d40fc9ee5312a4736b8982527b87933bb13154&")
            embed.set_footer(text="Não responder resultará em defesa automática")
            
            try:
                await lider_defensor.send(embed=embed)
            except:
                embed_publico = discord.Embed(
                    title="🔔 Notificação para Defensor",
                    description=f"<@{raid_data['defensor']['lider_id']}> sua guild está sob ataque!",
                    color=discord.Color.orange()
                )
                await thread.send(embed=embed_publico)
                
        except Exception as e:
            print(f"❌ Erro ao notificar defensor: {e}")

    async def atualizar_embed_principal_raid(self, raid_id: str):
        try:
            dados = self.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            raid_data = raids_ativas.get(raid_id)
            
            if not raid_data or not raid_data.get("thread_id"):
                return

            thread_id = raid_data["thread_id"]
            thread = self.bot.get_channel(thread_id)
            
            if not thread:
                print(f"❌ Thread {thread_id} não encontrado para a raid {raid_id}")
                return

            try:
                async for message in thread.history(limit=10, oldest_first=True):
                    if message.author.id == self.bot.user.id and message.embeds:
                        embed = message.embeds[0]
                        
                        tempo_restante = raid_data["timestamp_finalizacao"] - time.time()
                        if tempo_restante < 0:
                            tempo_restante = 0
                        horas = int(tempo_restante // 3600)
                        minutos = int((tempo_restante % 3600) // 60)
                        
                        novos_campos = []
                        for field in embed.fields:
                            if field.name == "⏰ Tempo Restante":
                                novos_campos.append(("⏰ Tempo Restante", f"{horas}h {minutos}m", True))
                            elif field.name == "⚔️ Estratégia do Atacante":
                                estrategia = raid_data["atacante"]["estrategia"]
                                status = "✅" if estrategia else "⏳"
                                valor = f"`{estrategia.replace('_', ' ').title()}` {status}" if estrategia else "`Aguardando...` ⏳"
                                novos_campos.append(("⚔️ Estratégia do Atacante", valor, True))
                            elif field.name == "🛡️ Estratégia do Defensor":
                                estrategia = raid_data["defensor"]["estrategia"]
                                status = "✅" if estrategia else "⏳"
                                valor = f"`{estrategia.replace('_', ' ').title()}` {status}" if estrategia else "`Aguardando...` ⏳"
                                novos_campos.append(("🛡️ Estratégia do Defensor", valor, True))
                            elif field.name == "🤝 Aliados":
                                aliados_atacante = len(raid_data["atacante"].get("aliados", {}))
                                aliados_defensor = len(raid_data["defensor"].get("aliados", {}))
                                novos_campos.append(("🤝 Aliados", f"Atacante: {aliados_atacante}/2\nDefensor: {aliados_defensor}/2", True))
                            else:
                                novos_campos.append((field.name, field.value, field.inline))

                        novo_embed = discord.Embed(
                            title=embed.title,
                            description=embed.description,
                            color=embed.color,
                            timestamp=embed.timestamp
                        )
                        
                        for name, value, inline in novos_campos:
                            novo_embed.add_field(name=name, value=value, inline=inline)
                        
                        if embed.footer:
                            novo_embed.set_footer(text=embed.footer.text, icon_url=embed.footer.icon_url)
                        
                        await message.edit(embed=novo_embed)
                        break
                        
            except discord.NotFound:
                print(f"❌ Thread da raid {raid_id} não encontrado (pode ter sido deletado)")
            except discord.Forbidden:
                print(f"❌ Sem permissão para acessar o thread da raid {raid_id}")
            except Exception as e:
                print(f"❌ Erro ao atualizar embed da raid {raid_id}: {e}")
                        
        except Exception as e:
            print(f"❌ Erro ao atualizar embed principal: {e}")

    async def atualizar_embed_final_raid(self, raid_id: str, raid_data: dict, vencedor: str):
        try:
            if not raid_data.get("thread_id"):
                return

            thread_id = raid_data["thread_id"]
            thread = self.bot.get_channel(thread_id)
            if not thread:
                return

            async for message in thread.history(limit=10, oldest_first=True):
                if message.author.id == self.bot.user.id and message.embeds:
                    embed = message.embeds[0]
                    
                    cor = discord.Color.green() if vencedor == "atacante" else discord.Color.blue()
                    
                    novo_embed = discord.Embed(
                        title="🏁 RAID FINALIZADA",
                        description=f"**{raid_data['atacante']['guild_nome']}** vs **{raid_data['defensor']['guild_nome']}**",
                        color=cor,
                        timestamp=discord.utils.utcnow()
                    )
                    
                    if vencedor == "atacante":
                        novo_embed.add_field(name="🎉 VENCEDOR", value=f"**{raid_data['atacante']['guild_nome']}** 🏆", inline=True)
                    else:
                        novo_embed.add_field(name="🎉 VENCEDOR", value=f"**{raid_data['defensor']['guild_nome']}** 🏆", inline=True)
                    
                    novo_embed.add_field(name="⚔️ Estratégia do Atacante", value=f"`{raid_data['atacante']['estrategia'].replace('_', ' ').title()}`", inline=True)
                    novo_embed.add_field(name="🛡️ Estratégia do Defensor", value=f"`{raid_data['defensor']['estrategia'].replace('_', ' ').title()}`", inline=True)

                    aliados_atacante = raid_data["atacante"].get("aliados", {})
                    aliados_defensor = raid_data["defensor"].get("aliados", {})
                    
                    if aliados_atacante:
                        aliados_str = ", ".join([aliado["guild_nome"] for aliado in aliados_atacante.values()])
                        novo_embed.add_field(name="🤝 Aliados do Atacante", value=aliados_str, inline=False)
                    
                    if aliados_defensor:
                        aliados_str = ", ".join([aliado["guild_nome"] for aliado in aliados_defensor.values()])
                        novo_embed.add_field(name="🤝 Aliados do Defensor", value=aliados_str, inline=False)
                    
                    novo_embed.set_footer(text="Tópico será arquivado em 1 hora")
                    
                    await message.edit(embed=novo_embed)
                    
                    embed_resultado = discord.Embed(
                        title="📊 RESULTADO DETALHADO",
                        description="As recompensas foram distribuídas entre os membros das guilds!",
                        color=cor
                    )
                    
                    total_xp_atacante = raid_data['atacante'].get('total_doacoes_xp', 0)
                    total_coins_atacante = raid_data['atacante'].get('total_doacoes_coins', 0)
                    total_xp_defensor = raid_data['defensor'].get('total_doacoes_xp', 0)
                    total_coins_defensor = raid_data['defensor'].get('total_doacoes_coins', 0)
                    
                    doadores_atacante = len(raid_data['atacante'].get('doacoes', {}))
                    doadores_defensor = len(raid_data['defensor'].get('doacoes', {}))
                    
                    embed_resultado.add_field(
                        name="💝 Doações Finais",
                        value=f"**Atacante:** {total_xp_atacante} XP, {total_coins_atacante} Coins ({doadores_atacante} doadores)\n**Defensor:** {total_xp_defensor} XP, {total_coins_defensor} Coins ({doadores_defensor} doadores)",
                        inline=False
                    )
                    
                    if vencedor == "atacante":
                        embed_resultado.add_field(
                            name="💰 Recompensas",
                            value=f"• {raid_data['atacante']['guild_nome']} roubou XP e coins\n• Doadores receberam bônus extras\n• Todos os membros receberam bônus",
                            inline=False
                        )
                    else:
                        embed_resultado.add_field(
                            name="💰 Recompensas", 
                            value=f"• {raid_data['defensor']['guild_nome']} recebeu compensação\n• Doadores receberam bônus extras\n• Todos os membros receberam bônus",
                            inline=False
                        )
                    
                    await thread.send(embed=embed_resultado)
                    break
                        
        except Exception as e:
            print(f"❌ Erro ao atualizar embed final: {e}")

    async def finalizar_raid(self, raid_id: str):
        try:
            dados = self.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            
            if raid_id not in raids_ativas:
                return
                
            raid_data = raids_ativas[raid_id]
            
            if raid_data["atacante"]["estrategia"] is None:
                raid_data["atacante"]["estrategia"] = "frontal"
            if raid_data["defensor"]["estrategia"] is None:
                raid_data["defensor"]["estrategia"] = "defesa"
            
            vencedor = await self.calcular_resultado_raid(raid_data)
            
            await self.distribuir_recompensas_raid(raid_data, vencedor)
            
            await self.notificar_resultado_raid(raid_data, vencedor)
            
            await self.atualizar_embed_final_raid(raid_id, raid_data, vencedor)
            
            if raid_data.get("thread_id"):
                try:
                    thread = self.bot.get_channel(raid_data["thread_id"])
                    if thread:
                        await asyncio.sleep(3600) 
                        await thread.edit(archived=True)
                except:
                    pass
            
            guild_defensora_id = raid_data["defensor"]["guild_id"]
            if guild_defensora_id in dados:
                dados[guild_defensora_id]["ultima_raid"] = time.time()
                self.salvar_dados(dados)
            
        except Exception as e:
            print(f"❌ Erro ao finalizar raid: {e}")

    async def atualizar_embed_final_raid(self, raid_data: dict, vencedor: str):
        try:
            if not raid_data.get("thread_id"):
                return

            thread_id = raid_data["thread_id"]
            thread = self.bot.get_channel(thread_id)
            if not thread:
                return

            async for message in thread.history(limit=10, oldest_first=True):
                if message.author.id == self.bot.user.id and message.embeds:
                    embed = message.embeds[0]
                    
                    cor = discord.Color.green() if vencedor == "atacante" else discord.Color.blue()
                    
                    novo_embed = discord.Embed(
                        title="🏁 RAID FINALIZADA",
                        description=f"**{raid_data['atacante']['guild_nome']}** vs **{raid_data['defensor']['guild_nome']}**",
                        color=cor,
                        timestamp=discord.utils.utcnow()
                    )
                    
                    if vencedor == "atacante":
                        novo_embed.add_field(name="🎉 VENCEDOR", value=f"**{raid_data['atacante']['guild_nome']}** 🏆", inline=True)
                    else:
                        novo_embed.add_field(name="🎉 VENCEDOR", value=f"**{raid_data['defensor']['guild_nome']}** 🏆", inline=True)
                    
                    novo_embed.add_field(name="⚔️ Estratégia do Atacante", value=f"`{raid_data['atacante']['estrategia'].replace('_', ' ').title()}`", inline=True)
                    novo_embed.add_field(name="🛡️ Estratégia do Defensor", value=f"`{raid_data['defensor']['estrategia'].replace('_', ' ').title()}`", inline=True)
                    
                    total_xp_atacante = raid_data['atacante'].get('total_doacoes_xp', 0)
                    total_coins_atacante = raid_data['atacante'].get('total_doacoes_coins', 0)
                    total_xp_defensor = raid_data['defensor'].get('total_doacoes_xp', 0)
                    total_coins_defensor = raid_data['defensor'].get('total_doacoes_coins', 0)
                    
                    doadores_atacante = len(raid_data['atacante'].get('doacoes', {}))
                    doadores_defensor = len(raid_data['defensor'].get('doacoes', {}))
                    
                    novo_embed.add_field(
                        name="💝 Doações Finais",
                        value=f"**Atacante:** {total_xp_atacante} XP, {total_coins_atacante} Coins ({doadores_atacante} doadores)\n**Defensor:** {total_xp_defensor} XP, {total_coins_defensor} Coins ({doadores_defensor} doadores)",
                        inline=False
                    )
                    
                    aliados_atacante = raid_data["atacante"].get("aliados", {})
                    aliados_defensor = raid_data["defensor"].get("aliados", {})
                    
                    if aliados_atacante:
                        aliados_str = ", ".join([aliado["guild_nome"] for aliado in aliados_atacante.values()])
                        novo_embed.add_field(name="🤝 Aliados do Atacante", value=aliados_str, inline=False)
                    
                    if aliados_defensor:
                        aliados_str = ", ".join([aliado["guild_nome"] for aliado in aliados_defensor.values()])
                        novo_embed.add_field(name="🤝 Aliados do Defensor", value=aliados_str, inline=False)
                    
                    novo_embed.set_footer(text="Tópico será arquivado em 1 hora")
                    
                    await message.edit(embed=novo_embed)
                    
                    embed_resultado = discord.Embed(
                        title="📊 RESULTADO DETALHADO",
                        description="As recompensas foram distribuídas entre os membros das guilds!",
                        color=cor
                    )
                    
                    if vencedor == "atacante":
                        embed_resultado.add_field(
                            name="💰 Recompensas",
                            value=f"• {raid_data['atacante']['guild_nome']} roubou XP e coins\n• Doadores receberam bônus extras\n• Todos os membros receberam bônus",
                            inline=False
                        )
                    else:
                        embed_resultado.add_field(
                            name="💰 Recompensas", 
                            value=f"• {raid_data['defensor']['guild_nome']} recebeu compensação\n• Doadores receberam bônus extras\n• Todos os membros receberam bônus",
                            inline=False
                        )
                    
                    await thread.send(embed=embed_resultado)
                    break
                    
        except Exception as e:
            print(f"❌ Erro ao atualizar embed final: {e}")

    async def calcular_resultado_raid(self, raid_data: dict) -> str:
        try:
            dados = self.carregar_dados()
            guild_atacante = dados[raid_data["atacante"]["guild_id"]]
            guild_defensora = dados[raid_data["defensor"]["guild_id"]]
            
            membros_atacante = raid_data["atacante"]["membros_count"]
            membros_defensor = len(guild_defensora["membros"])
            
            coins_atacante = guild_atacante["banco"]
            coins_defensor = guild_defensora["banco"]
            
            xp_atacante = guild_atacante["xp"]
            xp_defensor = guild_defensora["xp"]
            
            chance_atacante = 50
            chance_defensor = 50
            
            membros_extras_atacante = max(0, membros_atacante - 5)
            bonus_membros = (membros_extras_atacante // 5) * 10
            chance_atacante += bonus_membros
            
            if membros_atacante >= membros_defensor * 2:
                chance_atacante += 50
            
            elif membros_atacante == membros_defensor:
                if coins_atacante > coins_defensor:
                    chance_atacante += 20
                elif coins_defensor > coins_atacante:
                    chance_defensor += 20
            
            if xp_atacante > xp_defensor:
                chance_atacante += 40
            elif xp_defensor > xp_atacante:
                chance_defensor += 40
            
            estrategia_atacante = raid_data["atacante"]["estrategia"]
            estrategia_defensor = raid_data["defensor"]["estrategia"]
            
            if estrategia_atacante == "furtivo" and estrategia_defensor == "defesa":
                chance_atacante += 25
            elif estrategia_atacante == "frontal" and estrategia_defensor == "contra_ataque":
                chance_defensor += 25
            elif estrategia_atacante == "furtivo" and estrategia_defensor == "contra_ataque":
                chance_defensor += 15
            elif estrategia_atacante == "frontal" and estrategia_defensor == "defesa":
                chance_atacante += 15
            
            aliados_atacante = raid_data["atacante"].get("aliados", {})
            aliados_defensor = raid_data["defensor"].get("aliados", {})
            
            for aliado in aliados_atacante.values():
                if aliado["estrategia"] == "frente":
                    chance_atacante += 15
                elif aliado["estrategia"] == "flancos":
                    chance_atacante += 10
            
            for aliado in aliados_defensor.values():
                if aliado["estrategia"] == "muros":
                    chance_defensor += 15
                elif aliado["estrategia"] == "bloquear_flechas":
                    chance_defensor += 10
            
            total_xp_atacante = raid_data['atacante'].get('total_doacoes_xp', 0)
            total_coins_atacante = raid_data['atacante'].get('total_doacoes_coins', 0)
            total_xp_defensor = raid_data['defensor'].get('total_doacoes_xp', 0)
            total_coins_defensor = raid_data['defensor'].get('total_doacoes_coins', 0)
            
            chance_atacante += total_xp_atacante // 10
            chance_defensor += total_xp_defensor // 10
            
            chance_atacante += total_coins_atacante // 100
            chance_defensor += total_coins_defensor // 100
            
            chance_atacante = max(5, min(95, chance_atacante))
            chance_defensor = max(5, min(95, chance_defensor))
            
            total_chance = chance_atacante + chance_defensor
            rolagem = random.randint(1, total_chance)
            
            print(f"🎯 CALCULO RAID:")
            print(f"   Atacante: {chance_atacante}% | Defensor: {chance_defensor}%")
            print(f"   Rolagem: {rolagem}/{total_chance}")
            print(f"   Doações Atacante: {total_xp_atacante} XP, {total_coins_atacante} Coins")
            print(f"   Doações Defensor: {total_xp_defensor} XP, {total_coins_defensor} Coins")
            
            if rolagem <= chance_atacante:
                return "atacante"
            else:
                return "defensor"
                
        except Exception as e:
            print(f"❌ Erro ao calcular resultado da raid: {e}")
            return "defensor"

    async def distribuir_recompensas_raid(self, raid_data: dict, vencedor: str):
        try:
            dados = self.carregar_dados()
            guild_atacante = dados[raid_data["atacante"]["guild_id"]]
            guild_defensora = dados[raid_data["defensor"]["guild_id"]]
            
            if vencedor == "atacante":
                xp_roubado = int(guild_defensora["xp"] * 0.3)
                coins_roubados = int(guild_defensora["banco"] * 0.6)
                
                guild_defensora["xp"] = max(0, guild_defensora["xp"] - xp_roubado)
                guild_defensora["banco"] = max(0, guild_defensora["banco"] - coins_roubados)
                
                for user_id_str in guild_atacante["membros"]:
                    user_id = int(user_id_str)
                    
                    xp_membro = xp_roubado // len(guild_atacante["membros"])
                    xp_bonus_membro = 50
                    
                    total_xp_membro = xp_membro + xp_bonus_membro
                    
                    doacoes_usuario = raid_data["atacante"].get("doacoes", {}).get(user_id_str, {})
                    if doacoes_usuario:
                        bonus_xp_doacao = doacoes_usuario.get("xp", 0) * 2  
                        bonus_coins_doacao = doacoes_usuario.get("coins", 0) * 2
                        total_xp_membro += bonus_xp_doacao
                 
                    if not adicionar_xp_usuario(user_id, total_xp_membro, f"Vitória em raid contra {guild_defensora['nome']}"):
                        print(f"❌ Erro ao adicionar XP para {user_id}")
                    
                    coins_membro = coins_roubados // len(guild_atacante["membros"])
                    if doacoes_usuario:
                        coins_membro += bonus_coins_doacao
                    
                    if not adicionar_coins_usuario(user_id, coins_membro, f"Recompensa de raid vitoriosa contra {guild_defensora['nome']}"):
                        print(f"❌ Erro ao adicionar coins para {user_id}")
                    
                    print(f"✅ Recompensa para {user_id}: +{total_xp_membro} XP, +{coins_membro} coins")
                
                print(f"✅ Atacante venceu! Distribuído {xp_roubado} XP e {coins_roubados} coins entre {len(guild_atacante['membros'])} membros")
                
            else:
                xp_compensacao = int(guild_atacante["xp"] * 0.15)
                coins_compensacao = int(guild_atacante["banco"] * 0.3)
                
                guild_atacante["xp"] = max(0, guild_atacante["xp"] - xp_compensacao)
                guild_atacante["banco"] = max(0, guild_atacante["banco"] - coins_compensacao)

                for user_id_str in guild_defensora["membros"]:
                    user_id = int(user_id_str)
                    
                    xp_membro = xp_compensacao // len(guild_defensora["membros"])
                    xp_bonus_membro = 25
                    
                    total_xp_membro = xp_membro + xp_bonus_membro

                    doacoes_usuario = raid_data["defensor"].get("doacoes", {}).get(user_id_str, {})
                    if doacoes_usuario:
                        bonus_xp_doacao = doacoes_usuario.get("xp", 0) * 2 
                        bonus_coins_doacao = doacoes_usuario.get("coins", 0) * 2 
                        total_xp_membro += bonus_xp_doacao

                    if not adicionar_xp_usuario(user_id, total_xp_membro, f"Defesa bem-sucedida contra {guild_atacante['nome']}"):
                        print(f"❌ Erro ao adicionar XP para {user_id}")

                    coins_membro = coins_compensacao // len(guild_defensora["membros"])
                    if doacoes_usuario:
                        coins_membro += bonus_coins_doacao
                    
                    if not adicionar_coins_usuario(user_id, coins_membro, f"Recompensa de defesa bem-sucedida contra {guild_atacante['nome']}"):
                        print(f"❌ Erro ao adicionar coins para {user_id}")
                    
                    print(f"✅ Recompensa para {user_id}: +{total_xp_membro} XP, +{coins_membro} coins")
                
                print(f"✅ Defensor venceu! Distribuído {xp_compensacao} XP e {coins_compensacao} coins entre {len(guild_defensora['membros'])} membros")
            
            dados[raid_data["atacante"]["guild_id"]] = guild_atacante
            dados[raid_data["defensor"]["guild_id"]] = guild_defensora
            self.salvar_dados(dados)

            await self.notificar_distribuicao_recompensas(raid_data, vencedor)
            
        except Exception as e:
            print(f"❌ Erro ao distribuir recompensas: {e}")

    async def notificar_distribuicao_recompensas(self, raid_data: dict, vencedor: str):
        try:
            lider_atacante = await self.bot.fetch_user(int(raid_data["atacante"]["lider_id"]))
            lider_defensor = await self.bot.fetch_user(int(raid_data["defensor"]["lider_id"]))
            
            dados = self.carregar_dados()
            guild_atacante = dados[raid_data["atacante"]["guild_id"]]
            guild_defensora = dados[raid_data["defensor"]["guild_id"]]
            
            if vencedor == "atacante":
                embed_vencedor = discord.Embed(
                    title="💰 Recompensas Distribuídas!",
                    description=f"**{guild_atacante['nome']}** recebeu as recompensas da raid!",
                    color=discord.Color.green()
                )
                embed_vencedor.add_field(
                    name="🎯 Recompensas para cada membro:",
                    value=f"• XP de vitória + bônus por participação\n• Coins do banco inimigo\n• **BÔNUS EXTRA PARA DOADORES**\n• Multiplicadores de guild/premium aplicados",
                    inline=False
                )
                embed_vencedor.add_field(
                    name="👥 Beneficiados:",
                    value=f"Todos os {len(guild_atacante['membros'])} membros da guild",
                    inline=True
                )
                embed_vencedor.add_field(
                    name="💝 Doadores Premiados:",
                    value=f"{len(raid_data['atacante'].get('doacoes', {}))} membros receberam bônus extras",
                    inline=True
                )
                
                embed_perdedor = discord.Embed(
                    title="💸 Penalidades Aplicadas",
                    description=f"**{guild_defensora['nome']}** sofreu penalidades da derrota.",
                    color=discord.Color.red()
                )
                embed_perdedor.add_field(
                    name="📉 Perdas:",
                    value=f"• -30% XP da guild\n• -60% coins do banco",
                    inline=False
                )
                
            else:
                embed_vencedor = discord.Embed(
                    title="💰 Recompensas de Defesa!",
                    description=f"**{guild_defensora['nome']}** recebeu recompensas pela defesa bem-sucedida!",
                    color=discord.Color.blue()
                )
                embed_vencedor.add_field(
                    name="🎯 Recompensas para cada membro:",
                    value=f"• XP de defesa + bônus\n• Coins de compensação\n• **BÔNUS EXTRA PARA DOADORES**\n• Multiplicadores de guild/premium aplicados",
                    inline=False
                )
                embed_vencedor.add_field(
                    name="👥 Beneficiados:",
                    value=f"Todos os {len(guild_defensora['membros'])} membros da guild",
                    inline=True
                )
                embed_vencedor.add_field(
                    name="💝 Doadores Premiados:",
                    value=f"{len(raid_data['defensor'].get('doacoes', {}))} membros receberam bônus extras",
                    inline=True
                )
                
                embed_perdedor = discord.Embed(
                    title="💸 Penalidades do Atacante",
                    description=f"**{guild_atacante['nome']}** perdeu recursos pelo ataque falho.",
                    color=discord.Color.orange()
                )
                embed_perdedor.add_field(
                    name="📉 Perdas:",
                    value=f"• -15% XP da guild\n• -30% coins do banco",
                    inline=False
                )
            
            try:
                if vencedor == "atacante":
                    await lider_atacante.send(embed=embed_vencedor)
                    await lider_defensor.send(embed=embed_perdedor)
                else:
                    await lider_defensor.send(embed=embed_vencedor)
                    await lider_atacante.send(embed=embed_perdedor)
            except Exception as e:
                print(f"❌ Erro ao enviar notificação de recompensas: {e}")
                
        except Exception as e:
            print(f"❌ Erro em notificar_distribuicao_recompensas: {e}")

    async def notificar_resultado_raid(self, raid_data: dict, vencedor: str):
        try:
            lider_atacante = await self.bot.fetch_user(int(raid_data["atacante"]["lider_id"]))
            lider_defensor = await self.bot.fetch_user(int(raid_data["defensor"]["lider_id"]))
            
            dados = self.carregar_dados()
            guild_atacante = dados[raid_data["atacante"]["guild_id"]]
            guild_defensora = dados[raid_data["defensor"]["guild_id"]]
            
            if vencedor == "atacante":
                cor = discord.Color.green()
                titulo = "🎉 VITÓRIA NA RAID!"
                descricao = f"**{raid_data['atacante']['guild_nome']}** venceu a raid contra **{raid_data['defensor']['guild_nome']}**!"
                
                recompensa_xp = int(guild_defensora["xp"] * 0.3) + (len(guild_atacante["membros"]) * 50)
                recompensa_coins = int(guild_defensora["banco"] * 0.6)
                
            else:
                cor = discord.Color.blue()
                titulo = "🛡️ DEFESA BEM SUCEDIDA!"
                descricao = f"**{raid_data['defensor']['guild_nome']}** defendeu com sucesso a raid de **{raid_data['atacante']['guild_nome']}**!"
                
                recompensa_xp = int(guild_atacante["xp"] * 0.15)
                recompensa_coins = int(guild_atacante["banco"] * 0.3)
            
            embed_vencedor = discord.Embed(
                title=titulo,
                description=descricao,
                color=cor
            )
            
            if vencedor == "atacante":
                embed_vencedor.add_field(name="💰 XP Roubado", value=f"{recompensa_xp} XP", inline=True)
                embed_vencedor.add_field(name="🎯 Coins Roubados", value=f"{recompensa_coins} coins", inline=True)
                embed_vencedor.add_field(name="👥 Bônus por Membro", value=f"+{len(guild_atacante['membros']) * 50} XP", inline=True)
            else:
                embed_vencedor.add_field(name="💰 XP de Compensação", value=f"{recompensa_xp} XP", inline=True)
                embed_vencedor.add_field(name="🎯 Coins de Compensação", value=f"{recompensa_coins} coins", inline=True)
            
            total_xp_atacante = raid_data['atacante'].get('total_doacoes_xp', 0)
            total_coins_atacante = raid_data['atacante'].get('total_doacoes_coins', 0)
            total_xp_defensor = raid_data['defensor'].get('total_doacoes_xp', 0)
            total_coins_defensor = raid_data['defensor'].get('total_doacoes_coins', 0)
            
            embed_vencedor.add_field(
                name="💝 Doações que Ajudaram",
                value=f"Atacante: {total_xp_atacante} XP, {total_coins_atacante} Coins\nDefensor: {total_xp_defensor} XP, {total_coins_defensor} Coins",
                inline=False
            )
            
            aliados_atacante = raid_data["atacante"].get("aliados", {})
            aliados_defensor = raid_data["defensor"].get("aliados", {})
            
            if aliados_atacante:
                aliados_str = ", ".join([aliado["guild_nome"] for aliado in aliados_atacante.values()])
                embed_vencedor.add_field(name="🤝 Aliados Atacantes", value=aliados_str, inline=False)
            
            if aliados_defensor:
                aliados_str = ", ".join([aliado["guild_nome"] for aliado in aliados_defensor.values()])
                embed_vencedor.add_field(name="🤝 Aliados Defensores", value=aliados_str, inline=False)
            
            embed_vencedor.add_field(name="⚔️ Estratégia Usada", 
                                   value=f"Atacante: {raid_data['atacante']['estrategia'].replace('_', ' ').title()}\n"
                                         f"Defensor: {raid_data['defensor']['estrategia'].replace('_', ' ').title()}",
                                   inline=False)
            
            embed_perdedor = discord.Embed(
                title="💔 DERROTA NA RAID",
                description=descricao,
                color=discord.Color.red()
            )
            
            if vencedor == "atacante":
                embed_perdedor.add_field(name="💸 XP Perdido", value=f"{int(guild_defensora['xp'] * 0.3)} XP", inline=True)
                embed_perdedor.add_field(name="🎯 Coins Perdidos", value=f"{int(guild_defensora['banco'] * 0.6)} coins", inline=True)
            else:
                embed_perdedor.add_field(name="💸 XP Perdido", value=f"{int(guild_atacante['xp'] * 0.15)} XP", inline=True)
                embed_perdedor.add_field(name="🎯 Coins Perdidos", value=f"{int(guild_atacante['banco'] * 0.3)} coins", inline=True)
            
            embed_perdedor.add_field(name="⚔️ Estratégia Usada", 
                                   value=f"Atacante: {raid_data['atacante']['estrategia'].replace('_', ' ').title()}\n"
                                         f"Defensor: {raid_data['defensor']['estrategia'].replace('_', ' ').title()}",
                                   inline=False)
            
            try:
                if vencedor == "atacante":
                    await lider_atacante.send(embed=embed_vencedor)
                    await lider_defensor.send(embed=embed_perdedor)
                else:
                    await lider_defensor.send(embed=embed_vencedor)
                    await lider_atacante.send(embed=embed_perdedor)
            except Exception as e:
                print(f"❌ Erro ao enviar DM: {e}")
            
        except Exception as e:
            print(f"❌ Erro ao notificar resultado: {e}")

    @app_commands.command(name="guild_raid_status", description="Verifica o status de raids ativas")
    async def guild_raid_status(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            
            user_id = str(interaction.user.id)
            dados = self.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            raids_encontradas = []
            
            for raid_id, raid_data in raids_ativas.items():
                if (raid_data["atacante"]["lider_id"] == user_id or 
                    raid_data["defensor"]["lider_id"] == user_id):
                    raids_encontradas.append((raid_id, raid_data))
            
            if not raids_encontradas:
                await interaction.followup.send("❌ Você não tem raids ativas no momento!", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="⚔️ Raids Ativas",
                color=discord.Color.orange()
            )
            
            for raid_id, raid_data in raids_encontradas:
                tempo_restante = raid_data["timestamp_finalizacao"] - time.time()
                horas = int(tempo_restante // 3600)
                minutos = int((tempo_restante % 3600) // 60)
                
                if raid_data["atacante"]["lider_id"] == user_id:
                    papel = "⚔️ Atacante"
                    estrategia = raid_data["atacante"]["estrategia"] or "Não definida"
                    aliados = raid_data["atacante"].get("aliados", {})
                    doacoes = raid_data["atacante"].get("doacoes", {})
                else:
                    papel = "🛡️ Defensor" 
                    estrategia = raid_data["defensor"]["estrategia"] or "Não definida"
                    aliados = raid_data["defensor"].get("aliados", {})
                    doacoes = raid_data["defensor"].get("doacoes", {})
                
                info_raid = f"**Papel:** {papel}\n"
                info_raid += f"**Estratégia:** {estrategia.replace('_', ' ').title() if estrategia != 'Não definida' else estrategia}\n"
                info_raid += f"**Tempo restante:** {horas}h {minutos}m\n"
                info_raid += f"**💝 Doadores:** {len(doacoes)} membros\n"
                
                if aliados:
                    aliados_str = ", ".join([aliado["guild_nome"] for aliado in aliados.values()])
                    info_raid += f"**🤝 Aliados:** {aliados_str}\n"
                
                embed.add_field(
                    name=f"{raid_data['atacante']['guild_nome']} vs {raid_data['defensor']['guild_nome']}",
                    value=info_raid,
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"❌ Erro em guild_raid_status: {e}")
            await interaction.followup.send("❌ Erro ao verificar status das raids!")

    @tasks.loop(minutes=1)
    async def verificar_raids(self):
        try:
            dados = self.carregar_dados()
            raids_ativas = dados.get("raids_ativas", {})
            raids_para_remover = []
            
            for raid_id, raid_data in raids_ativas.items():
                await self.atualizar_embed_principal_raid(raid_id)

                if raid_data.get("timestamp_finalizacao", 0) <= time.time():
                    await self.finalizar_raid(raid_id)
                    raids_para_remover.append(raid_id)
            for raid_id in raids_para_remover:
                del raids_ativas[raid_id]
            
            if raids_para_remover:
                dados["raids_ativas"] = raids_ativas
                self.salvar_dados(dados)
                
        except Exception as e:
            print(f"❌ Erro ao verificar raids: {e}")

    @verificar_raids.before_loop
    async def before_verificar_raids(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(GuildAllianceRaidSystem(bot))