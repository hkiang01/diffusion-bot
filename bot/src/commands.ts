import { SlashCommandBuilder } from "discord.js";
import { buildDrawSubcommand } from "./commands/draw";
import { COMMAND_NAME } from './constants';

export const buildCommands = async () => {
    const drawSubcommand = await buildDrawSubcommand();
    return [new SlashCommandBuilder()
        .setName(COMMAND_NAME)
        .setDescription("A bot to explore your imagination")
        .addSubcommand(drawSubcommand)
    ].map(command => command.toJSON())
}

