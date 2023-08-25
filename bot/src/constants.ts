import dotenv from 'dotenv';

dotenv.config();

// Used by the Discord API to register the bot
export const discordOauth2ClientId = process.env.DISCORD_OAUTH2_CLIENT_ID;
if (!discordOauth2ClientId) throw Error("DISCORD_OAUTH2_CLIENT_ID must be defined");
export const DISCORD_OAUTH2_CLIENT_ID: string = discordOauth2ClientId;

// Used by the Discord API to register the bot
export const discordBotToken: string | undefined = process.env.DISCORD_BOT_TOKEN;
if (!discordBotToken) throw Error("DISCORD_BOT_TOKEN must be defined");
export const DISCORD_BOT_TOKEN: string = discordBotToken;

// The URL of the text to image server
export const apiURL = process.env.API_URL;
if (!apiURL) throw Error("API_URL must be defined");
export const API_URL: string = apiURL;

export const OUTPUTS_DIR = 'outputs'

export const COMMAND_NAME = 'diffusion-bot'
export enum Commands {
    Draw = 'draw',
}

