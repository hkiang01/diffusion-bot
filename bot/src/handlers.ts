import { Interaction } from 'discord.js';
import { COMMAND_NAME, Commands } from './constants';
import { drawHandler } from './handlers/draw';

export async function interactionHandler(interaction: Interaction) {
    // ensure that:
    // i) the interaction was not issued by a bot,
    // ii) the interaction is indeed a command,
    // iii) the command name is the command of interest.
    // iv) the interaction was issued in a GuildTextBasedChannelt
    if (!interaction.isChatInputCommand()) return;
    if (interaction.user.bot) return;
    if (!interaction.isCommand()) return;
    if (interaction.commandName !== COMMAND_NAME) return;
    if (!interaction.inGuild()) return;

    const channelId = interaction.channelId;
    const channel = await interaction.client.channels.fetch(channelId)
    if (!channel || !channel.isTextBased()) {
        await interaction.reply({ content: `${COMMAND_NAME} only works in text channels`, ephemeral: true })
        return
    }

    try {
        switch (interaction.options.getSubcommand()) {
            case Commands.Draw:
                await drawHandler(interaction, channel);
                break;
            default:
                await interaction.followUp({ ephemeral: true, content: 'Unrecognized command' });
                break;
        }
    } catch (err) {
        console.error(err);
        await channel.send({ content: `Error, contact bot developers\n${err}` });
    }
}