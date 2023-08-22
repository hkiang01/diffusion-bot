import { Client, Events, REST, Routes } from 'discord.js';
import { buildCommands } from './commands';
import { DISCORD_BOT_TOKEN, DISCORD_OAUTH2_CLIENT_ID } from './constants';
import { interactionHandler } from './handlers';

const client = new Client(
  {
    intents: [
      // GatewayIntentBits.Guilds,
    ]
  }
);

// log when bot is ready
client.on('ready', () => {
  console.info(`Logged in!`);
});

client.on(Events.InteractionCreate, async (interaction) => {
  await interactionHandler(interaction)
})

const rest = new REST().setToken(DISCORD_BOT_TOKEN);
(async () => {
  const commands = await buildCommands();
  try {
    console.log(`Started refreshing ${commands.length} application (/) commands.`);

    // The put method is used to fully refresh all commands in the guild with the current set
    await rest.put(
      Routes.applicationCommands(DISCORD_OAUTH2_CLIENT_ID),
      { body: commands },
    );

    console.log(`Successfully reloaded application (/) commands.`);

  } catch (error) {
    // And of course, make sure you catch and log any errors!
    console.error(error);
  }
})();


// log in bot
client.login(DISCORD_BOT_TOKEN);
