import { SlashCommandSubcommandBuilder } from '@discordjs/builders';
// import API from '../services/api';
import { Commands } from '../constants';


export const buildTextToImageSubcommand = async () => {
  // const models = (await API.getModels()).map((model) => {
  //   return { name: model, value: model }
  // })
  const models = [{ "name": "stablediffusionxl", "value": "stablediffusionxl" }]

  return new SlashCommandSubcommandBuilder()
    .setName(Commands.TextToImage)
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
        .setMinValue(8)
        .setMaxValue(2560) // can change if your GPU has the allowed memory
    )
    .addIntegerOption(option =>
      option
        .setName("height")
        .setDescription("Height of image")
        .setRequired(false)
        .setMinValue(8)
        .setMaxValue(1440) // can change if your GPU has the allowed memory
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