import { AttachmentBuilder, ChatInputCommandInteraction, EmbedBuilder, Message } from "discord.js";
import fs from 'fs';
import API, { PredictTaskRequest, PredictTaskState } from '../services/api';
import { COMMAND_NAME } from "../constants";

export async function drawHandler(interaction: ChatInputCommandInteraction) {
    const deferredReply = await interaction.deferReply({ fetchReply: true });
    const channelId = interaction.channelId;
    const channel = await interaction.client.channels.fetch(channelId)
    if (!channel || !channel.isTextBased()) {
        await interaction.editReply({ content: `${COMMAND_NAME} only works in guilds` })
        await deferredReply.delete()
        return
    }

    const prompt = interaction.options.getString("prompt", true)
    const predictTaskRequest: PredictTaskRequest = {
        model: interaction.options.getString("model", true),
        prompt: prompt,
        width: interaction.options.getInteger("width", false) || 1024,
        height: interaction.options.getInteger("height", false) || 1024,
        num_inference_steps: interaction.options.getInteger("num_inference_steps", false) || 20,
    }
    const author = interaction.user.displayName
    const initialEmbed = new EmbedBuilder()
        .setTitle(prompt)
        .setFields([
            { name: "Author", value: author },
            { name: "Position in queue", value: "N/A" },
            { name: "Percent complete", value: "0" },
            { name: "Time elapsed", value: `0 seconds` },

        ])
    const message: Message = await channel.send({ embeds: [initialEmbed] })
    await deferredReply.delete()

    const callback = async (state: PredictTaskState) => {
        const timeElapsed = (new Date().getTime() - start) / 1000;
        const embed = new EmbedBuilder()
            .setTitle(prompt)
            .setFields([
                { name: "Author", value: author },
                { name: "Position in queue", value: state.position.toString() },
                { name: "Percent complete", value: `${state.percent_complete.toString()}%` },
                { name: "Time elapsed", value: `${timeElapsed} seconds` },

            ])
        await message.edit({ content: null, embeds: [embed] })
    }

    const start = new Date().getTime()
    const submissionId = await API.predict(predictTaskRequest)
    const path = await API.result(submissionId, callback)

    // see https://discordjs.guide/popular-topics/embeds.html#attaching-images
    const file = new AttachmentBuilder(path)
    const embed = new EmbedBuilder()
        .setTitle(`${prompt} - by ${author}`)
        .setImage(`attachment://${submissionId}.png`)

    await message.edit({ content: null, embeds: [embed], files: [file] })

    // cleanup
    await new Promise(resolve => fs.unlink(path, resolve))
    await API.deleteResult(submissionId)
}
