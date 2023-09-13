import { AttachmentBuilder, Channel, ChatInputCommandInteraction, EmbedBuilder, Message } from "discord.js";
import fs from 'fs';
import API, { TextToImageRequest, TaskState } from '../services/api';
import { Commands, Fields } from "../constants";
import { generateRefinerSelectActionRow } from "./utils";

export async function textToImageHandler(interaction: ChatInputCommandInteraction, channel: Channel) {
    // tell discord that we got the interaction
    const deferredReply = await interaction.deferReply({ fetchReply: true });

    // get the text channel to which to send results
    if (!channel || !channel.isTextBased()) {
        await interaction.editReply({ content: `${Commands.TextToImage} only works in guilds` })
        await deferredReply.delete()
        return
    }

    // send initial state of request
    const prompt = interaction.options.getString("prompt", true);
    const model = interaction.options.getString("model", true)
    const width = interaction.options.getInteger("width", false) || 1024
    const height = interaction.options.getInteger("height", false) || 1024
    const numInferenceSteps = interaction.options.getInteger("num_inference_steps", false) || undefined;

    const textToImageRequest: TextToImageRequest = {
        model: model,
        prompt: prompt,
        width: width,
        height: height,
        num_inference_steps: numInferenceSteps,
    }
    const author = interaction.user.displayName
    const initialEmbed = new EmbedBuilder()
        .setFields([
            { name: Fields.Author, value: author },
            { name: Fields.Model, value: model },
            { name: Fields.PositionInQueue, value: "N/A" },
            { name: Fields.StepsCompleted, value: "0" },
            { name: Fields.TimeElapsed, value: `0 seconds` },

        ])
    const message: Message = await channel.send({ content: prompt, embeds: [initialEmbed] })
    // prevent error after 15 minutes of not responding to interaction
    await deferredReply.delete()

    // update request state every polling interval
    const callback = async (state: TaskState) => {
        const timeElapsed = (new Date().getTime() - start) / 1000;
        const embed = new EmbedBuilder()
            .setFields([
                { name: Fields.Author, value: author },
                { name: Fields.Model, value: model },
                { name: Fields.PositionInQueue, value: state.position.toString() },
                { name: Fields.StepsCompleted, value: `${parseInt(state.steps_completed.toString()).toString()}` },
                { name: Fields.TimeElapsed, value: `${timeElapsed} seconds` },
            ])
        await message.edit({ content: prompt, embeds: [embed] })
    }

    // actually start the polling
    const start = new Date().getTime()
    const submissionId = await API.textToImage(textToImageRequest)
    const path = await API.result(submissionId, callback)

    // send the result to the channel
    // see https://discordjs.guide/popular-topics/embeds.html#attaching-images
    const file = new AttachmentBuilder(path)
    const embed = new EmbedBuilder()
        .setFields([
            { name: Fields.Author, value: author },
            { name: Fields.Model, value: model },
        ])
        .setImage(`attachment://${submissionId}.png`)


    const row = await generateRefinerSelectActionRow()
    await message.edit({ content: prompt, embeds: [embed], files: [file], components: [row] })

    // cleanup
    await new Promise(resolve => fs.unlink(path, resolve))
    await API.deleteResult(submissionId)
}
