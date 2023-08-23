import { AttachmentBuilder, ChatInputCommandInteraction, EmbedBuilder } from "discord.js";
import fs from 'fs';
import wait from 'node:timers/promises';
import { Commands } from "../constants";
import API, { PredictTaskRequest, PredictTaskState } from '../services/api';
import { AxiosError, AxiosResponse } from "axios";

export async function drawHandler(interaction: ChatInputCommandInteraction) {
    const prompt = interaction.options.getString("prompt", true)
    await interaction.reply({ fetchReply: true, content: `⌛ ${Commands.Draw}ing ${prompt}` });
    const predictTaskRequest: PredictTaskRequest = {
        model: interaction.options.getString("model", true),
        prompt: prompt,
        width: interaction.options.getInteger("width", false) || 512,
        height: interaction.options.getInteger("height", false) || 512,
        num_inference_steps: interaction.options.getInteger("num_inference_steps", false) || 20,
    }
    const submissionId = await API.predict(predictTaskRequest)
    console.log('submissionId', submissionId)

    // eslint-disable-next-line no-constant-condition
    while (true) {
        await wait.setTimeout(4000);
        let statusResp: AxiosResponse
        try {
            statusResp = await API.status(submissionId)
        } catch (error) {
            if (error instanceof AxiosError && error.response?.status == 303) break
            throw error
        }
        const status = statusResp.data as PredictTaskState;
        console.log("status", status)
    }

    const path = await API.result(submissionId)

    // see https://discordjs.guide/popular-topics/embeds.html#attaching-images
    const file = new AttachmentBuilder(path)
    const embed = new EmbedBuilder()
        .setTitle(prompt)
        .setImage(`attachment://${submissionId}.png`)

    await interaction.editReply({ content: null, embeds: [embed], files: [file] })

    // cleanup
    await new Promise(resolve => fs.unlink(path, resolve))
    await API.deleteResult(submissionId)
}
