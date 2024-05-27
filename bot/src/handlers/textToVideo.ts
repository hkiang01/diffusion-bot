import { AttachmentBuilder, ButtonInteraction, Channel, ChatInputCommandInteraction, EmbedBuilder, Message, PartialTextBasedChannelFields } from "discord.js";
import fs from 'fs';
import API, { TextToVideoRequest, TaskState } from '../services/api';
import { Buttons, Commands, Fields } from "../constants";
import { generateRedrawButton, generateRefinerSelectActionRow } from "./utils";

export async function textToVideoCommandHandler(interaction: ChatInputCommandInteraction, channel: Channel) {
    // tell discord that we got the interaction
    const deferredReply = await interaction.deferReply({ fetchReply: true });

    // get the text channel to which to send results
    if (!channel || !channel.isTextBased()) {
        await interaction.editReply({ content: `${Commands.TextToVideo} only works in guilds` })
        await deferredReply.delete()
        return
    }

    // send initial state of request
    const prompt = interaction.options.getString("prompt", true);
    const author = interaction.user.displayName;
    const model = interaction.options.getString("model", true)
    const width = interaction.options.getInteger("width", false) || 1024
    const height = interaction.options.getInteger("height", false) || 1024
    const numInferenceSteps = interaction.options.getInteger("num_inference_steps", false) || undefined;

    const textToVideoRequest: TextToVideoRequest = {
        model: model,
        prompt: prompt,
        width: width,
        height: height,
        num_inference_steps: numInferenceSteps,
    }
    await processTextToVideoRequest(textToVideoRequest, author, channel, deferredReply)
}

export async function textToVideoButtonHandler(interaction: ButtonInteraction, channel: Channel) {
    // tell discord that we got the interaction
    const deferredReply = await interaction.deferReply({ fetchReply: true });

    // get the text channel to which to send results
    if (!channel || !channel.isTextBased()) {
        await interaction.editReply({ content: `${Commands.TextToVideo} only works in guilds` })
        await deferredReply.delete()
        return
    }

    const originalMessage = interaction.message;
    const originalEmbed = originalMessage.embeds[0];
    const fields = originalEmbed.fields;

    // send initial state of request
    const prompt = originalMessage.content;
    const model = fields.find(f => f.name == Fields.Model)?.value;
    const author = interaction.user.displayName;
    const width = originalEmbed.image?.width;
    const height = originalEmbed.image?.height;
    const numInferenceSteps = fields.find(f => f.name == Fields.NumInferenceSteps)?.value;

    if (!model || !width || !height || !numInferenceSteps || !author) {
        await interaction.editReply({ content: `Error while processing ${Buttons.ReDraw}: ` + 'Unable to resolve model or width or height or numInferenceSteps or author' })
        return
    }

    const textToVideoRequest: TextToVideoRequest = {
        model: model,
        prompt: prompt,
        width: width,
        height: height,
        num_inference_steps: numInferenceSteps != "N/A" ? parseInt(numInferenceSteps) : undefined,
    }
    await processTextToVideoRequest(textToVideoRequest, author, channel, deferredReply)
}

async function processTextToVideoRequest(textToVideoRequest: TextToVideoRequest, author: string, channel: PartialTextBasedChannelFields, deferredReply: Message) {
    const initialEmbed = new EmbedBuilder()
        .setFields([
            { name: Fields.Author, value: author },
            { name: Fields.Model, value: textToVideoRequest.model },
            { name: Fields.PositionInQueue, value: "N/A" },
            { name: Fields.NumInferenceSteps, value: textToVideoRequest.num_inference_steps?.toString() || "N/A" },
            { name: Fields.StepsCompleted, value: "0" },
            { name: Fields.TimeElapsed, value: `0 seconds` },

        ])
    const message: Message = await channel.send({ content: textToVideoRequest.prompt, embeds: [initialEmbed] })
    // prevent error after 15 minutes of not responding to interaction
    await deferredReply.delete()

    // update request state every polling interval
    const callback = async (state: TaskState) => {
        const timeElapsed = (new Date().getTime() - start) / 1000;
        const embed = new EmbedBuilder()
            .setFields([
                { name: Fields.Author, value: author },
                { name: Fields.Model, value: textToVideoRequest.model },
                { name: Fields.PositionInQueue, value: state.position.toString() },
                { name: Fields.NumInferenceSteps, value: textToVideoRequest.num_inference_steps?.toString() || "N/A" },
                { name: Fields.StepsCompleted, value: `${parseInt(state.steps_completed.toString()).toString()}` },
                { name: Fields.TimeElapsed, value: `${timeElapsed} seconds` },
            ])
        await message.edit({ content: textToVideoRequest.prompt, embeds: [embed] })
    }

    // actually start the polling
    const start = new Date().getTime()
    const submissionId = await API.textToVideo(textToVideoRequest)
    const path = await API.result(submissionId, ".gif", callback)

    // send the result to the channel
    // see https://discordjs.guide/popular-topics/embeds.html#attaching-images
    const file = new AttachmentBuilder(path)
    const embed = new EmbedBuilder()
        .setFields([
            { name: Fields.Author, value: author },
            { name: Fields.Model, value: textToVideoRequest.model },
            { name: Fields.NumInferenceSteps, value: textToVideoRequest.num_inference_steps?.toString() || "N/A" },
        ])
        .setImage(`attachment://${submissionId}.png`)


    const selectActionRow = await generateRefinerSelectActionRow()
    const redrawButtonRow = generateRedrawButton()
    await message.edit({ content: textToVideoRequest.prompt, embeds: [embed], files: [file], components: [redrawButtonRow, selectActionRow] })

    // cleanup
    await new Promise(resolve => fs.unlink(path, resolve))
    await API.deleteResult(submissionId)
}
