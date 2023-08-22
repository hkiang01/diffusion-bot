import { ChatInputCommandInteraction } from "discord.js";
import { Commands } from "../constants";


export async function drawHandler(interaction: ChatInputCommandInteraction) {
    await interaction.reply({ ephemeral: false, fetchReply: true, content: `⌛ ${Commands.Draw} processing` });
}