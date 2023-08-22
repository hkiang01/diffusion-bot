import { SlashCommandSubcommandBuilder } from '@discordjs/builders';
import { Commands } from '../constants';

export const addMemeSubcommand = new SlashCommandSubcommandBuilder()
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
      .setName("image-url")
      .setDescription("image associated with meme")
      .setRequired(false)
  );
