import { AttachmentBuilder, ChatInputCommandInteraction, EmbedBuilder, Message } from "discord.js";
import fs from 'fs';
import API, { PredictTaskRequest, PredictTaskState } from '../services/api';
import { COMMAND_NAME } from "../constants";

export async function drawHandler(interaction: ChatInputCommandInteraction) {
    // tell discord that we got the interaction
    const deferredReply = await interaction.deferReply({ fetchReply: true });

    // get the text channel to which to send results
    const channelId = interaction.channelId;
    const channel = await interaction.client.channels.fetch(channelId)
    if (!channel || !channel.isTextBased()) {
        await interaction.editReply({ content: `${COMMAND_NAME} only works in guilds` })
        await deferredReply.delete()
        return
    }

    // send initial state of request
    const prompt = interaction.options.getString("prompt", true);
    const model = interaction.options.getString("model", true)
    const width = interaction.options.getInteger("width", false) || 1024
    const height = interaction.options.getInteger("height", false) || 1024
    const predictTaskRequest: PredictTaskRequest = {
        model: model,
        prompt: prompt,
        width: width,
        height: height,
        num_inference_steps: interaction.options.getInteger("num_inference_steps", false) || 20,
    }
    const author = interaction.user.displayName
    const initialEmbed = new EmbedBuilder()
        .setFields([
            { name: "Author", value: author },
            { name: "Model", value: model },
            { name: "Position in queue", value: "N/A" },
            { name: "Percent complete", value: "0" },
            { name: "Time elapsed", value: `0 seconds` },

        ])
    const message: Message = await channel.send({ content: prompt, embeds: [initialEmbed] })
    // prevent error after 15 minutes of not responding to interaction
    await deferredReply.delete()

    // update request state every polling interval
    const callback = async (state: PredictTaskState) => {
        const timeElapsed = (new Date().getTime() - start) / 1000;
        const embed = new EmbedBuilder()
            .setFields([
                { name: "Author", value: author },
                { name: "Model", value: model },
                { name: "Position in queue", value: state.position.toString() },
                { name: "Percent complete", value: `${parseInt(state.percent_complete.toString()).toString()}%` },
                { name: "Time elapsed", value: `${timeElapsed} seconds` },

            ])
        await message.edit({ content: prompt, embeds: [embed] })
    }

    // actually start the polling
    const start = new Date().getTime()
    const submissionId = await API.predict(predictTaskRequest)
    const path = await API.result(submissionId, callback)

    // send the result to the channel
    // see https://discordjs.guide/popular-topics/embeds.html#attaching-images
    const file = new AttachmentBuilder(path)
    const embed = new EmbedBuilder()
        .setFields([
            { name: "Author", value: author },
            { name: "Model", value: model },
        ])
        .setImage(`attachment://${submissionId}.png`)
    await message.edit({ content: prompt, embeds: [embed], files: [file] })

    // cleanup
    await new Promise(resolve => fs.unlink(path, resolve))
    await API.deleteResult(submissionId)
}
