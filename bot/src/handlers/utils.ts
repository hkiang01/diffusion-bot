import { StringSelectMenuBuilder, StringSelectMenuOptionBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } from "discord.js";
import { Buttons, Emojis, Selects } from "../constants";
import API from "../services/api";

export async function generateRefineImageSelectActionRow(): Promise<ActionRowBuilder<StringSelectMenuBuilder>> {
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

export function generateRedrawImageButton(): ActionRowBuilder<ButtonBuilder> {
    const button = new ButtonBuilder()
        .setCustomId(Buttons.ReDrawImage)
        .setLabel(Buttons.ReDrawImage)
        .setEmoji(Emojis.ReDrawImage)
        .setStyle(ButtonStyle.Primary)
    const row = new ActionRowBuilder<ButtonBuilder>()
        .addComponents(button);
    return row
}

export function generateRecreateVideoButton(): ActionRowBuilder<ButtonBuilder> {
    const button = new ButtonBuilder()
        .setCustomId(Buttons.ReCreateVideo)
        .setLabel(Buttons.ReCreateVideo)
        .setEmoji(Emojis.ReCreateVideo)
        .setStyle(ButtonStyle.Primary)
    const row = new ActionRowBuilder<ButtonBuilder>()
        .addComponents(button);
    return row
}
