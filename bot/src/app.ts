import { Client, GatewayIntentBits, Interaction } from 'discord.js'

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

