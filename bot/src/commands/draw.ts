import { SlashCommandSubcommandBuilder } from '@discordjs/builders';
import API from '../services/api';
import { Commands } from '../constants';


export const buildDrawSubcommand = async () => {
  const models = (await API.getModels()).map((model) => {
    return { name: model, value: model }
  })
  return new SlashCommandSubcommandBuilder()
    .setName(Commands.Draw)
    .setDescription("Turns text into an image")
    .addStringOption(option =>
      option
        .setName("prompt")
        .setDescription("What you want to create")
        .setRequired(true)
    )
    .addStringOption(option =>
      option
        .setName("model")
        .setDescription("The text to image model to draw with")
        .setRequired(true)
        .addChoices(
          ...models
        )
    )
    .addIntegerOption(option =>
      option
        .setName("width")
        .setDescription("Width of image")
        .setRequired(false)
        .setMinValue(1)
        .setMaxValue(1920)
    )
    .addIntegerOption(option =>
      option
        .setName("height")
        .setDescription("Height of image")
        .setRequired(false)
        .setMinValue(1)
        .setMaxValue(1920)
    )
    .addIntegerOption(option =>
      option
        .setName("num_inference_steps")
        .setDescription("Number of inference steps")
        .setRequired(false)
        .setMinValue(1)
        .setMaxValue(20)
    )
    ;
}