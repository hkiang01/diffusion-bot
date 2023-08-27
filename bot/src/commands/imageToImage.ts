import { SlashCommandSubcommandBuilder } from '@discordjs/builders';
// import API from '../services/api';
import { Commands } from '../constants';


export const buildImageToImageSubcommand = async () => {
  // const models = (await API.getModels()).map((model) => {
  //   return { name: model, value: model }
  // })
  const models = [{ "name": "stablediffusionxl", "value": "stablediffusionxl" }]

  return new SlashCommandSubcommandBuilder()
    .setName(Commands.ImageToimage)
    .setDescription("Uses an image to condition the generation of new images")
    .addStringOption(option =>
      option
        .setName("image_url")
        .setDescription("URL to initial image")
        .setRequired(true)
    )
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
        .setName("num_inference_steps")
        .setDescription("Number of inference steps")
        .setRequired(false)
        .setMinValue(1)
        .setMaxValue(20)
    )
    .addNumberOption(option =>
      option
        .setName("strength")
        .setDescription("Transform image with strength 0-1. More strength adds more changes. At strength 1, maximal change")
        .setRequired(false)
        .setMinValue(0)
        .setMaxValue(1)
    )
    .addNumberOption(option =>
      option
        .setName("guidance_scale")
        .setDescription("Higher value = prompt-aligned images, lower quality. Default: 7.5.")
        .setRequired(false)
    );
}