import { AttachmentBuilder, ChatInputCommandInteraction, Embed, EmbedBuilder } from "discord.js";
import wait from 'node:timers/promises';
import { Commands } from "../constants";
import API, { PredictTaskRequest, PredictTaskStatus } from '../services/api';

export async function drawHandler(interaction: ChatInputCommandInteraction) {
    await interaction.reply({ ephemeral: true, fetchReply: true, content: `⌛ ${Commands.Draw} processing` });
    const prompt = interaction.options.getString("prompt", true)
    const predictTaskRequest: PredictTaskRequest = {
        model: interaction.options.getString("model", true),
        prompt: prompt,
        width: interaction.options.getInteger("width", false) || 512,
        height: interaction.options.getInteger("height", false) || 512,
        num_inference_steps: interaction.options.getInteger("num_inference_steps", false) || 20,
    }
    const submissionId = await API.predict(predictTaskRequest)
    console.log('submissionId', submissionId)
    let status: PredictTaskStatus
    do {
        await wait.setTimeout(4000);
        const statusResp = await API.status(submissionId)
        status = statusResp.status
        console.log(`status of ${submissionId}`, statusResp)
    } while (status != PredictTaskStatus.COMPLETE)
    const bufferResolvable = await API.result(submissionId)

    // see https://discordjs.guide/popular-topics/embeds.html#attaching-images
    const file = new AttachmentBuilder(bufferResolvable)
    const embed = new EmbedBuilder()
        .setTitle(prompt)
        .setImage(`attachment://${submissionId}.png`)

    await interaction.editReply({ embeds: [embed], files: [file] })
}