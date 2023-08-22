import { ChatInputCommandInteraction } from "discord.js";
import { Commands } from "../constants";
import API, { PredictTaskRequest, PredictTaskStatus } from '../services/api'

export async function drawHandler(interaction: ChatInputCommandInteraction) {
    await interaction.reply({ ephemeral: true, fetchReply: true, content: `⌛ ${Commands.Draw} processing` });
    const predictTaskRequest: PredictTaskRequest = {
        model: interaction.options.getString("model", true),
        prompt: interaction.options.getString("prompt", true),
        width: interaction.options.getInteger("width", false) || 512,
        height: interaction.options.getInteger("height", false) || 512,
        num_inference_steps: interaction.options.getInteger("num_inference_steps", false) || 20,
    }
    const submissionId = await API.predict(predictTaskRequest)
    console.log('submissionId', submissionId)
    let status: PredictTaskStatus
    do {
        const statusResp = await API.status(submissionId)
        status = statusResp.status
        console.log(`status of ${submissionId}`, statusResp)
        await new Promise(resolve => setTimeout(resolve, 5000));
    } while (status in [PredictTaskStatus.PENDING, PredictTaskStatus.PROCESSING])
    // const result = await API.result(submissionId)
}