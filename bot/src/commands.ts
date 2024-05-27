import { SlashCommandBuilder } from "discord.js";
import { buildTextToImageSubcommand } from "./commands/textToImage";
import { buildTextToVideoSubcommand } from "./commands/textToVideo";
import { buildImageToImageSubcommand } from "./commands/imageToImage";

import { COMMAND_NAME } from './constants';

export const buildCommands = async () => {
    const textToImageSubcommand = await buildTextToImageSubcommand();
    const textToVideoSubcommand = await buildTextToVideoSubcommand();
    const imageToImageSubcommand = await buildImageToImageSubcommand();

    return [new SlashCommandBuilder()
        .setName(COMMAND_NAME)
        .setDescription("A bot to explore your imagination")
        .addSubcommand(textToImageSubcommand)
        .addSubcommand(textToVideoSubcommand)
        .addSubcommand(imageToImageSubcommand)
    ].map(command => command.toJSON())
}

