import { ChatInputCommandInteraction } from "discord.js";
import { Commands } from "../constants";
import API, { PredictTaskRequest } from '../services/api'

export async function drawHandler(interaction: ChatInputCommandInteraction) {
    await interaction.reply({ ephemeral: true, fetchReply: true, content: `⌛ ${Commands.Draw} processing` });
    const predictTaskRequest: PredictTaskRequest = {
        model: interaction.options.getString("model") || "",
        prompt: interaction.options.getString("prompt") || "",
        width: interaction.options.getInteger("width"),
        height: interaction.options.getInteger("height"),
        num_inference_steps: interaction.options.getInteger("num_inference_steps"),
    }
    const submissionId = await API.predict(predictTaskRequest)
    console.log('submissionId', submissionId)
}