import { StringSelectMenuBuilder, StringSelectMenuOptionBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } from "discord.js";
import { Buttons, Emojis, Selects } from "../constants";
import API from "../services/api";

export async function generateRefinerSelectActionRow(): Promise<ActionRowBuilder<StringSelectMenuBuilder>> {
    const imageToImageModels = await API.getImageToImageModels()
    const refinerModelSelect = new StringSelectMenuBuilder()
        .setCustomId(Selects.RefinerModel)
        .setPlaceholder("Pick a model to refine the image with")
        .addOptions(imageToImageModels.map((imageToImageModel) =>
            new StringSelectMenuOptionBuilder()
                .setLabel(imageToImageModel)
                .setValue(imageToImageModel)
        ))
    const row = new ActionRowBuilder<StringSelectMenuBuilder>()
        .addComponents(refinerModelSelect);
    return row
}

export function generateRedrawButton(): ActionRowBuilder<ButtonBuilder> {
    const button = new ButtonBuilder()
        .setCustomId(Buttons.ReDraw)
        .setLabel(Buttons.ReDraw)
        .setEmoji(Emojis.ReDraw)
        .setStyle(ButtonStyle.Primary)
    const row = new ActionRowBuilder<ButtonBuilder>()
        .addComponents(button);
    return row
}
