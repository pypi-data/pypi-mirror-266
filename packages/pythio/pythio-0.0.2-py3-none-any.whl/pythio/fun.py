from client import Client
import asyncio


client = Client("7054226719:AAEaoVXm9foVAhb04QpFvmofi8vHrq-75Jk")

async def main():

    message_count = 0
    async for message in client.on_message():
        if message_count == 5:
            await client.disconnect()

        message_count =+ 1
        print(message.text)
        await message.reply('Hello World!')


if __name__ == '__main__':
    asyncio.run(main())
