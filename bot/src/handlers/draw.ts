import { AttachmentBuilder, ChatInputCommandInteraction, EmbedBuilder } from "discord.js";
import fs from 'fs';
import { Commands } from "../constants";
import API, { PredictTaskRequest, PredictTaskState } from '../services/api';

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
    const start = new Date().getTime()
    const callback = async (state: PredictTaskState) => {
        const timeElapsed = (new Date().getTime() - start) / 1000;
        const embed = new EmbedBuilder()
            .setTitle(prompt)
            .setFields([
                { name: "Position in queue", value: state.position.toString() },
                { name: "Percent complete", value: `${state.percent_complete.toString()}%` },
                { name: "Time elapsed", value: `${timeElapsed} seconds` },

            ])
        await interaction.editReply({ content: null, embeds: [embed] })
    }

    const path = await API.result(submissionId, callback)

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
