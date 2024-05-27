import { Interaction } from 'discord.js';
import { Buttons, COMMAND_NAME, Commands, Selects } from './constants';
import { textToImageButtonHandler, textToImageCommandHandler } from './handlers/textToImage';
import { textToVideoButtonHandler, textToVideoCommandHandler } from './handlers/textToVideo';
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
                    await textToImageCommandHandler(interaction, channel);
                    break;
                case Commands.TextToVideo:
                    await textToVideoCommandHandler(interaction, channel);
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
                case Buttons.ReDraw:
                    await textToImageButtonHandler(interaction, channel);
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
    else if (interaction.isStringSelectMenu()) {
        const channelId = interaction.channelId;
        const channel = await interaction.client.channels.fetch(channelId)

        if (!channel || !channel.isTextBased()) {
            await interaction.reply({ content: `${COMMAND_NAME} only works in text channels`, ephemeral: true })
            return
        }
        try {
            switch (interaction.customId) {
                case Selects.RefinerModel:
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