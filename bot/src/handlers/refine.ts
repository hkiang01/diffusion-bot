import { AttachmentBuilder, Channel, EmbedBuilder, Message, StringSelectMenuInteraction } from "discord.js";
import fs from 'fs';
import API, { ImageToImageRequest } from '../services/api';
import { Fields, Selects } from "../constants";
import { generateRedrawImageButton, generateRefineImageSelectActionRow } from "./utils";

export async function refineHandler(interaction: StringSelectMenuInteraction, channel: Channel) {
    // tell discord that we got the interaction
    const deferredReply = await interaction.deferReply({ fetchReply: true });

    // get the text channel to which to send results
    if (!channel || !channel.isTextBased()) {
        await interaction.editReply({ content: `${Selects.RefinerModel} only works in guilds` })
        await deferredReply.delete()
        return
    }

    const originalMessage = interaction.message;
    const originalEmbed = originalMessage.embeds[0];
    const fields = originalEmbed.fields;

    // send initial state of request
    const prompt = originalMessage.content;
    const model = interaction.values[0];
    const numInferenceSteps = fields.find(f => f.name == Fields.NumInferenceSteps)?.value;
    const author = fields.find(f => f.name == Fields.Author)?.value;
    const refiner = interaction.user.displayName;
    const imageURL = originalEmbed.image?.url

    if (!model || !author || !imageURL) {
        await interaction.editReply({ content: `Error while processing ${Selects.RefinerModel}: ` + 'Unable to resolve model or author or imageURL' })
        return
    }

    const imageToImageRequest: ImageToImageRequest = {
        model: model,
        prompt: prompt,
        image_url: imageURL,
    }
    const initialEmbed = new EmbedBuilder()
        .setFields([
            { name: Fields.OriginalMessage, value: originalMessage.url },
            { name: Fields.Author, value: author },
            { name: Fields.Refiner, value: refiner },
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
                { name: Fields.OriginalMessage, value: originalMessage.url },
                { name: Fields.Author, value: author },
                { name: Fields.Refiner, value: refiner },
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
            { name: Fields.OriginalMessage, value: originalMessage.url },
            { name: Fields.Author, value: author },
            { name: Fields.Refiner, value: refiner },
            { name: Fields.Model, value: model },
            { name: Fields.NumInferenceSteps, value: numInferenceSteps?.toString() || "N/A" },
        ])
        .setImage(`attachment://${submissionId}.png`)
    const selectActionRow = await generateRefineImageSelectActionRow()
    const redrawButtonRow = generateRedrawImageButton()
    await message.edit({ content: prompt, embeds: [embed], files: [file], components: [redrawButtonRow, selectActionRow] })

    // cleanup
    await new Promise(resolve => fs.unlink(path, resolve))
    await API.deleteResult(submissionId)
}
