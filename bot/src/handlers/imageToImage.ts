import { AttachmentBuilder, Channel, ChatInputCommandInteraction, EmbedBuilder, Message } from "discord.js";
import fs from 'fs';
import API, { ImageToImageRequest } from '../services/api';
import { Commands, Fields } from "../constants";
import { generateRedrawImageButton, generateRefineImageSelectActionRow } from "./utils";

export async function imageToImageHandler(interaction: ChatInputCommandInteraction, channel: Channel) {
    // tell discord that we got the interaction
    const deferredReply = await interaction.deferReply({ fetchReply: true });

    // get the text channel to which to send results
    if (!channel || !channel.isTextBased()) {
        await interaction.editReply({ content: `${Commands.ImageToimage} only works in guilds` })
        await deferredReply.delete()
        return
    }

    // send initial state of request
    const prompt = interaction.options.getString("prompt", true);
    const model = interaction.options.getString("model", true)
    const imageURL = interaction.options.getString("image_url", true)
    const numInferenceSteps = interaction.options.getInteger("num_inference_steps", false) || undefined;
    const strength = interaction.options.getNumber("strength", false) || undefined
    const guidanceScale = interaction.options.getNumber("guidance_scale", false) || undefined


    const imageToImageRequest: ImageToImageRequest = {
        model: model,
        prompt: prompt,
        image_url: imageURL,
        num_inference_steps: numInferenceSteps,
        strength: strength,
        guidance_scale: guidanceScale
    }
    const author = interaction.user.displayName
    const initialEmbed = new EmbedBuilder()
        .setFields([
            { name: Fields.Author, value: author },
            { name: Fields.Model, value: model },
            { name: Fields.NumInferenceSteps, value: numInferenceSteps?.toString() || "N/A" },
            { name: Fields.TimeElapsed, value: `0 seconds` },
        ])
    const message: Message = await channel.send({ content: prompt, embeds: [initialEmbed] })
    // prevent error after 15 minutes of not responding to interaction
    await deferredReply.delete()

    // update request task every polling interval
    const callback = async () => {
        const timeElapsed = (new Date().getTime() - start) / 1000;
        const embed = new EmbedBuilder()
            .setFields([
                { name: Fields.Author, value: author },
                { name: Fields.Model, value: model },
                { name: Fields.NumInferenceSteps, value: numInferenceSteps?.toString() || "N/A" },
                { name: Fields.TimeElapsed, value: `${timeElapsed} seconds` },
            ])
        await message.edit({ content: prompt, embeds: [embed] })
    }

    // actually start the polling
    const start = new Date().getTime()
    const submissionId = await API.imageToImage(imageToImageRequest)
    const path = await API.result(submissionId, ".png", callback)

    // send the result to the channel
    // see https://discordjs.guide/popular-topics/embeds.html#attaching-images
    const file = new AttachmentBuilder(path)
    const embed = new EmbedBuilder()
        .setFields([
            { name: Fields.Author, value: author },
            { name: Fields.Model, value: model },
            { name: Fields.NumInferenceSteps, value: numInferenceSteps?.toString() || "N/A" },

        ])
        .setImage(`attachment://${submissionId}.png`)
    const selectActionRow = await generateRefineImageSelectActionRow()
    const redrawButtonRow = generateRedrawImageButton()
    await message.edit({ content: prompt, embeds: [embed], files: [file], components: [selectActionRow, redrawButtonRow] })

    // cleanup
    await new Promise(resolve => fs.unlink(path, resolve))
    await API.deleteResult(submissionId)
}
