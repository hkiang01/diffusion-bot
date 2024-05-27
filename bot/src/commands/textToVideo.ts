import { SlashCommandSubcommandBuilder } from '@discordjs/builders';
import API from '../services/api';
import { Commands } from '../constants';


export const buildTextToVideoSubcommand = async () => {
  const models = (await API.getTextToVideoModels()).map((model) => {
    return { name: model, value: model }
  })

  return new SlashCommandSubcommandBuilder()
    .setName(Commands.TextToVideo)
    .setDescription("Turns text into a video")
    .addStringOption(option =>
      option
        .setName("prompt")
        .setDescription("What you want to create")
        .setRequired(true)
    )
    .addStringOption(option =>
      option
        .setName("model")
        .setDescription("The text to video model to draw with")
        .setRequired(true)
        .addChoices(
          ...models
        )
    )
    .addIntegerOption(option =>
      option
        .setName("num_inference_steps")
        .setDescription("Number of inference steps. 4 is good default.")
        .setRequired(true)
        .setChoices({ name: "1", value: 1 }, { name: "2", value: 2 }, { name: "4", value: 4 }, { name: "8", value: 8 })
    );
}