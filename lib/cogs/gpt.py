from discord import Message
from discord.ext.commands import Cog, command, Context
from lib.bot import Bot
from revChatGPT.revChatGPT import Chatbot


class GPT(Cog):

    def __init__(self, bot):
        self.bot: Bot = bot

        self.api_mail = bot.config.chatgpt_mail
        self.api_password = bot.config.chatgpt_password

        self.chatbot = Chatbot({"email": self.api_mail, "password": self.api_password}, conversation_id=None)
        self.chatbot.refresh_session()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('gpt')

    async def get_input_message(self, ctx: Context) -> Message | None:
        replied_to = ctx.message.reference
        if replied_to and isinstance(replied_to.resolved, Message):
            return replied_to.resolved
        message = await ctx.channel.history(limit=1, before=ctx.message).get()
        return message

    def get_prompt(self, input_message: Message, additional_context: list[Message]) -> str:
        content = input_message.clean_content
        if additional_context:
            content = f'{input_message.author.display_name}: {content}\n'
            for msg in additional_context:
                content += f'{msg.author.display_name}: {msg.clean_content}\n'

        # content += "\nBitte fass dich in deiner Antwort kurz."
        return content

    @command(name="answer", aliases=["antwort"])
    async def answer(self, ctx: Context, previous_messages: int = 0):

        input_message = await self.get_input_message(ctx)
        if input_message is None:
            await ctx.send("Nachricht nicht gefunden :(")
            return

        reply = await input_message.reply("Thinking...")

        additional_context: list[Message] = []
        if previous_messages:
            async for m in ctx.channel.history(limit=min(previous_messages, 5), before=input_message):
                additional_context.append(m)

        prompt = self.get_prompt(input_message, additional_context)
        print(f'{prompt=}')
        try:
            response = await self.get_response(prompt)
        except ValueError as e:
            print(e)
            await reply.edit(content="Kann grad ned denken, sorry :(")
            return
        print(response)
        if "message" not in response:
            await reply.edit(content="something went wrong :(")
            return
        await reply.edit(content=response["message"])

    async def get_response(self, prompt: str) -> dict[str, str]:
        self.chatbot.reset_chat()
        response = self.chatbot.get_chat_response(prompt, output="text")
        print(response)
        return response


def setup(bot):
    bot.add_cog(GPT(bot))
