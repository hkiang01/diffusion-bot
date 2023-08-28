import { Interaction } from 'discord.js';
import { Buttons, COMMAND_NAME, Commands } from './constants';
import { textToImageHandler } from './handlers/textToImage';
import { imageToImageHandler } from './handlers/imageToImage';
import { refineHandler } from './handlers/refine';

export async function interactionHandler(interaction: Interaction) {
    if (interaction.user.bot) return;
    if (!interaction.inGuild()) return;


    if (interaction.isChatInputCommand()) {
        if (interaction.commandName !== COMMAND_NAME) return;
        const channelId = interaction.channelId;
        const channel = await interaction.client.channels.fetch(channelId)

        if (!channel || !channel.isTextBased()) {
            await interaction.reply({ content: `${COMMAND_NAME} only works in text channels`, ephemeral: true })
            return
        }
        try {
            switch (interaction.options.getSubcommand()) {
                case Commands.TextToImage:
                    await textToImageHandler(interaction, channel);
                    break;
                case Commands.ImageToimage:
                    await imageToImageHandler(interaction, channel);
                    break;
                default:
                    await interaction.followUp({ ephemeral: true, content: 'Unrecognized command' });
                    break;
            }
        } catch (err) {
            console.error(err);
            await channel.send({ content: `Error, contact bot developers\n${err}` });
        }

    } else if (interaction.isButton()) {
        const channelId = interaction.channelId;
        const channel = await interaction.client.channels.fetch(channelId)

        if (!channel || !channel.isTextBased()) {
            await interaction.reply({ content: `${COMMAND_NAME} only works in text channels`, ephemeral: true })
            return
        }
        try {
            switch (interaction.customId) {
                case Buttons.Refine:
                    await refineHandler(interaction, channel);
                    break;
                default:
                    await interaction.followUp({ ephemeral: true, content: 'Unrecognized button' });
                    break;
            }
        } catch (err) {
            console.error(err);
            await channel.send({ content: `Error, contact bot developers\n${err}` });
        }
    }
}